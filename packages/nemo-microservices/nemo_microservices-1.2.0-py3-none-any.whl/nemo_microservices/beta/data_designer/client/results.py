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

import random
import time
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from ..config.errors import DataDesignerJobError
from ..config.logs import get_logger

if TYPE_CHECKING:
    from nemo_microservices import NeMoMicroservices
    from nemo_microservices.types.beta.data_designer import DataDesignerJob
    from nemo_microservices.types.beta.data_designer.jobs import DataDesignerResult

logger = get_logger(__name__)


class StrEnum(str, Enum):
    pass


class JobStatus(StrEnum):
    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    CANCELLED = "cancelled"
    CANCELLING = "cancelling"
    FAILED = "failed"
    COMPLETED = "completed"
    READY = "ready"
    UNKNOWN = "unknown"


CHECK_PROGRESS_LOG_MSG = (
    "To check on your job's progress, use the `get_job_status` method. "
    "If you want to wait until it's complete, use the `wait_until_done` method."
)
TERMINAL_JOB_STATUSES = [JobStatus.CANCELLED, JobStatus.CANCELLING, JobStatus.FAILED]
WAIT_INTERVAL_SECONDS = 2


class DataDesignerJobResults:
    def __init__(self, *, job: DataDesignerJob, client: NeMoMicroservices):
        self._job = job
        self._client = client
        self._data_designer_resource = self._client.beta.data_designer

    def get_job(self) -> DataDesignerJob:
        self._refresh_job()
        return self._job

    def get_job_status(self) -> str:
        return self.get_job().status

    def get_job_result(self, result_id: str) -> list[DataDesignerResult]:
        self._check_if_complete()
        return self._data_designer_resource.jobs.results.retrieve(result_id, job_id=self._job.id)

    def get_job_results(self, *, include_intermediate_results: bool = False) -> list[DataDesignerResult]:
        self._check_if_complete()
        results = self._data_designer_resource.jobs.results.list(job_id=self._job.id)
        return (
            [result for result in results]
            if include_intermediate_results
            else [result for result in results if result.canonical]
        )

    def download_evaluation_report(self, html_path: Path | str) -> None:
        self._check_if_complete(raise_if_not_complete=True)
        results = [r for r in self.get_job_results(include_intermediate_results=True) if r.format == "html"]
        if len(results) != 1:
            raise ValueError("Evaluation report not found in job results")
        html = self._data_designer_resource.jobs.results.download(results[0].id, job_id=self._job.id)
        with open(html_path, "w") as f:
            logger.info(f"📄 Writing evaluation report to {html_path}")
            f.write(html)

    def load_dataset(self) -> pd.DataFrame:
        self._check_if_complete(raise_if_not_complete=True)
        results = [r for r in self.get_job_results() if r.format == "csv"]
        if len(results) != 1:
            raise ValueError(f"Error loading dataset: expected 1 canonical CSV result, got {len(results)}")
        return pd.read_csv(
            StringIO(self._data_designer_resource.jobs.results.download(results[0].id, job_id=self._job.id))
        )

    def wait_until_done(self) -> None:
        error_occurred = False
        warning_occurred = False
        printed_logs = []
        while self.get_job_status() != JobStatus.COMPLETED:
            time.sleep(WAIT_INTERVAL_SECONDS)
            current_logs = list(self._data_designer_resource.jobs.get_logs(job_id=self._job.id))
            if current_logs != printed_logs:
                for log in current_logs[len(printed_logs) :]:
                    msg = log["msg"]
                    if log["level"] == "info":
                        logger.info(msg)
                        printed_logs.append(msg)
                    elif log["level"] in {"warning", "warn"}:
                        logger.warning(msg)
                        warning_occurred = True
                        printed_logs.append(msg)
                    elif log["level"] == "error":
                        logger.error(msg)
                        error_occurred = True
                        printed_logs.append(msg)
            if (status := self.get_job_status()) in TERMINAL_JOB_STATUSES:
                error_occurred = True
                logger.error(f"🛑 Terminating generation job with status `{status}`.")
                break
        if error_occurred:
            logger.error("🛑 Dataset generation completed with errors.")
        elif warning_occurred:
            logger.warning("⚠️ Dataset generation completed with warnings.")
        else:
            random_emoji = random.choice(["🎉", "🎊", "👏", "✅", "🙌", "🎆"])
            logger.info(f"{random_emoji} Dataset generation completed successfully.")

    def _check_if_complete(self, *, raise_if_not_complete: bool = False) -> None:
        status = self.get_job_status()
        if status == JobStatus.COMPLETED:
            return
        elif status == JobStatus.RUNNING:
            msg = f"Your dataset generation job is still running. {CHECK_PROGRESS_LOG_MSG}"
            if raise_if_not_complete:
                raise DataDesignerJobError(f"🛑 {msg}")
            logger.warning(f"⏳ {msg}")
        elif status in {JobStatus.CANCELLED, JobStatus.CANCELLING, JobStatus.FAILED}:
            msg = f"🛑 Your dataset generation job stopped with status `{status}`."
            if raise_if_not_complete:
                raise DataDesignerJobError(msg)
            logger.error(msg)
        elif status in {JobStatus.CREATED, JobStatus.PENDING}:
            msg = (
                f"⏹️ Your dataset generation job is still in the queue with status `{status}`. {CHECK_PROGRESS_LOG_MSG}"
            )
            if raise_if_not_complete:
                raise DataDesignerJobError(msg)
            logger.warning(msg)
        else:
            msg = f"Your job is in an unknown state: `{status}`."
            if raise_if_not_complete:
                raise DataDesignerJobError(msg)
            logger.error(msg)

    def _refresh_job(self) -> None:
        self._job = self._data_designer_resource.jobs.retrieve(self._job.id)
