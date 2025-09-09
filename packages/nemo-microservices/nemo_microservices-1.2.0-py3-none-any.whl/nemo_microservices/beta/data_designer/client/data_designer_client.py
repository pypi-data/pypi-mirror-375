# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

import pandas as pd
from typing_extensions import Self

from ..config.builder import DataDesignerConfigBuilder
from ..config.interface import BaseDataDesigner
from ..config.logs import get_logger
from ..config.results import PreviewResults
from ..config.utils import get_task_log_emoji
from ..config.viz_tools import DataDesignerMetadata
from .results import DataDesignerJobResults

if TYPE_CHECKING:
    from nemo_microservices import NeMoMicroservices
    from nemo_microservices.types.beta import DataDesignerPreviewResponse

logger = get_logger(__name__)

DEFAULT_PREVIEW_TIMEOUT = 120
DEFAULT_NUM_RECORDS_FOR_PREVIEW = 10


class DataDesignerClientError(Exception):
    """Base exception for Data Designer client errors."""


class DataDesignerConfigValidationError(DataDesignerClientError):
    """Exception raised when the Data Designer configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(message)


class DataDesignerClient(BaseDataDesigner):
    def __init__(self, client: NeMoMicroservices):
        self._client = client
        self._data_designer_resource = self._client.beta.data_designer

    def create(
        self,
        config_builder: DataDesignerConfigBuilder,
        *,
        num_records: int = 100,
        wait_until_done: bool = False,
    ) -> DataDesignerJobResults:
        """Create a Data Designer generation job.

        Args:
            config_builder: Data Designer configuration builder.
            num_records: The number of records to generate.
            wait_until_done: Whether to halt your program until the job is done.

        Returns:
            Data Designer results object with methods for querying the job's status and results.
        """
        logger.info("🎨 Creating Data Designer generation job")
        try:
            job = self._data_designer_resource.jobs.create(
                config=config_builder.build(raise_exceptions=True),
                num_records=num_records,
            )
            logger.info(f"  |-- job_id: {job.id}")
            results = DataDesignerJobResults(job=job, client=self._client)
            if wait_until_done:
                results.wait_until_done()
            return results
        except Exception as e:
            self._handle_api_exceptions(e)

    def preview(
        self,
        config_builder: DataDesignerConfigBuilder,
        *,
        num_records: int | None = None,
        verbose_logging: bool = False,
        timeout: int | None = None,
    ) -> PreviewResults:
        """Generate a set of preview records based on your current Data Designer configuration.

        This method is meant for fast iteration on your Data Designer configuration.

        Args:
            config_builder: Data Designer configuration builder.
            verbose_logging: Whether to log verbose information.
            timeout: The timeout for the preview in seconds. If not provided, one will be set based on the model configs.

        Returns:
            Preview results object containing the preview dataset and tools for inspecting the results.
        """
        try:
            return self._capture_preview_result(
                config_builder=config_builder, num_records=num_records, verbose_logging=verbose_logging, timeout=timeout
            )
        except Exception as e:
            self._handle_api_exceptions(e)

    def load_job_results(self, job_id: str) -> DataDesignerJobResults:
        job = self._data_designer_resource.jobs.retrieve(job_id)
        return DataDesignerJobResults(job=job, client=self._client)

    @staticmethod
    def _get_last_evaluation_step_name(workflow_step_names: list[str]) -> str | None:
        """Return the name of the last evaluation step in a workflow."""
        eval_steps = [s for s in workflow_step_names if s.startswith("evaluate-dataset")]
        return None if len(eval_steps) == 0 else eval_steps[-1]

    def _handle_api_exceptions(self, e: Exception) -> None:
        if hasattr(e, "status_code") and e.status_code == 422:
            raise DataDesignerConfigValidationError(f"‼️ Config validation failed!\n{e}") from None
        else:
            raise DataDesignerClientError(f"‼️ Something went wrong!\n{e}") from None

    def _capture_preview_result(
        self,
        config_builder: DataDesignerConfigBuilder,
        num_records: int | None,
        verbose_logging: bool,
        timeout: int | None,
    ) -> PreviewResults:
        """Capture the results (including logs) of a workflow preview."""
        config = config_builder.build(raise_exceptions=True)

        step_idx = 0
        current_step = None
        final_output = None
        outputs_by_step = {}
        success = True
        step_names = []
        column_names = [col.name for col in config.columns]

        timeout = (
            timeout
            or self._get_preview_timeout_for_model_configs(config_builder, num_records)
            or DEFAULT_PREVIEW_TIMEOUT
        )
        for response in self._data_designer_resource.preview(config=config, num_records=num_records, timeout=timeout):
            message = Message.from_preview_response(response)

            if not message.step:
                continue
            if current_step != message.step:
                current_step = message.step
                step_names.append(message.step)
                log_name = _add_backticks_to_column_names(message.step, column_names)
                logger.info(
                    f"{get_task_log_emoji(log_name)}Step {step_idx + 1}: {log_name.replace('-', ' ').capitalize()}"
                )
                step_idx += 1

            if message.has_log_message:
                log_msg = message.log_message

                if (log_msg.is_info and verbose_logging) or (log_msg.is_error or log_msg.is_warning):
                    spaces = "  " if log_msg.is_info else " "
                    formatted_msg = f"{spaces}{'|' if '|--' in log_msg.msg else '|--'} {log_msg.msg}"
                    if log_msg.is_info:
                        logger.info(formatted_msg)
                    elif log_msg.is_warning:
                        logger.warning(formatted_msg)
                    else:
                        success = False
                        logger.error(formatted_msg)

            if message.has_output:
                logger.debug(f"Step output: {json.dumps(message.payload, indent=4)}")

                output = message.payload
                if message.has_dataset:
                    final_output = message.dataset
                outputs_by_step[message.step] = output
        # the final output is either the dataset produced by the last
        # task in the workflow, or, if no dataset is produced by the workflow
        # the final output will be the output of the last task to complete
        # (which may also be none)
        last_evaluation_step_name = self._get_last_evaluation_step_name(workflow_step_names=step_names)
        if final_output is None:
            final_output = outputs_by_step.get(current_step)
        evaluation_results = (
            None if last_evaluation_step_name is None else outputs_by_step.get(last_evaluation_step_name)
        )
        return PreviewResults(
            output=final_output,
            evaluation_results=evaluation_results,
            data_designer_metadata=DataDesignerMetadata.from_config_builder(config_builder),
            success=success,
        )

    def _get_preview_timeout_for_model_configs(
        self, config_builder: DataDesignerConfigBuilder, num_records: int | None
    ) -> int | None:
        timeouts = []
        for model_config in config_builder.model_configs:
            if model_config.inference_parameters.timeout is not None:
                timeouts.append(model_config.inference_parameters.timeout)
        if len(timeouts) > 0:
            # Multiply the highest timeout by the number of llm columns and the number of records
            return (
                max(timeouts) * len(config_builder.llm_gen_columns) * (num_records or DEFAULT_NUM_RECORDS_FOR_PREVIEW)
            )
        return None


class WorkflowTaskError(Exception):
    """
    Represents an error returned by the Task. This error
    is most likely related to an issue with the Task
    itself. If you see this error check your Task config
    first. If the issue persists, the error might be a bug
    in the remote Task implementation.
    """


@dataclass
class LogMessage:
    level: str
    msg: str

    @property
    def is_error(self) -> bool:
        return self.level == "error"

    @property
    def is_info(self) -> bool:
        return self.level == "info"

    @property
    def is_warning(self) -> bool:
        return self.level == "warn"


@dataclass
class Message:
    step: str
    """The name of the step"""

    stream: str
    """
    The stream the message should be associated with.

    We use multiple streams so that we can differentiate between different types of outputs.
    """

    payload: dict
    """The actual value of the output"""

    type: str
    """The type of message"""

    ts: datetime
    """The date and time the message was created"""

    @classmethod
    def from_dict(cls, message: dict, raise_on_error: bool = False) -> Self:
        message["ts"] = datetime.fromisoformat(message["ts"])
        deserialized_message = cls(**message)

        if raise_on_error:
            deserialized_message.raise_for_error()

        return deserialized_message

    @classmethod
    def from_preview_response(cls, response: DataDesignerPreviewResponse) -> Self:
        return cls(
            step=response.step,
            stream=response.stream,
            payload=response.payload,
            type=response.type,
            ts=response.ts,
        )

    @property
    def has_log_message(self) -> bool:
        return self.stream == "logs" and "msg" in self.payload and ("level" in self.payload or "state" in self.payload)

    @property
    def log_message(self) -> LogMessage | None:
        if self.has_log_message:
            if "level" not in self.payload:
                self.payload["level"] = "info"
                if "state" in self.payload:
                    state = self.payload.pop("state")
                    self.payload["level"] = state if state == "error" else state
            return LogMessage(**self.payload)
        return None

    @property
    def has_output(self) -> bool:
        return self.stream == "step_outputs"

    @property
    def has_dataset(self) -> bool:
        return self.has_output and "dataset" in self.payload

    @property
    def dataset(self) -> pd.DataFrame:
        records = []
        if self.has_dataset:
            records = self.payload["dataset"]
        return pd.DataFrame.from_records(records)

    def raise_for_error(self) -> None:
        """Check for fatal errors and raise an exception if found."""
        if self.type == "step_state_change" and self.payload.get("state", "") == "error":
            raise WorkflowTaskError(
                f"Step {self.step!r} failed: "
                f"{self.payload.get('msg', '').strip(' .')}. "
                "Please check your Workflow config. "
                "If the issue persists please contact support."
            )


def _add_backticks_to_column_names(step_name: str, column_names: list[str]) -> str:
    """Add backticks to the column names in the step name if they are present.

    This function is used in the context of logging workflow steps.

    Args:
        step_name: Name of the step.
        column_names: List of possible column names.

    Returns:
        Step name with backticks added to the column names if present.
    """
    max_overlap = 0
    best_match = None
    for name in column_names:
        if name in step_name:
            overlap = len(name)
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = name
    if best_match:
        step_name = step_name.replace(best_match, f"`{best_match}`")
    return step_name
