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
from pathlib import Path
from typing import Type

import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import HfApi, HfFileSystem
from pydantic import BaseModel
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from typing_extensions import Self

from .columns import (
    CodeValidationColumn,
    DataSeedColumn,
    ExpressionColumn,
    LLMCodeColumn,
    LLMGenColumn,
    LLMJudgeColumn,
    LLMStructuredColumn,
    LLMTextColumn,
    SamplerColumn,
    ValidationWithRemoteEndpointColumn,
)
from .constants import DEFAULT_REPR_HTML_STYLE, REPR_HTML_TEMPLATE, REPR_LIST_LENGTH_USE_JSON
from .data_designer_config import DataDesignerConfig
from .datastore import DatastoreSettings
from .errors import DataDesignerValidationError
from .info import DataDesignerInfo
from .logs import get_logger
from .params.constraints import ColumnConstraint, ColumnConstraintParams, ConstraintType
from .params.evaluation import EvaluateDataDesignerDatasetSettings
from .params.llm_gen import ModelConfig, OutputType
from .params.samplers import PersonSamplerParams, SamplerType
from .params.seed import SamplingStrategy, Seed
from .type_aliases import (
    ColumnProviderTypeT,
    DAGColumnT,
    DataDesignerColumnT,
    ProviderType,
)
from .utils import get_sampler_params, make_date_obj_serializable, smart_load_yaml
from .validate import (
    ViolationLevel,
    rich_print_violations,
    validate_data_designer_config,
)
from .viz_tools import DataDesignerMetadata

_type_builtin = type
_SAMPLER_PARAMS: dict[SamplerType, Type[BaseModel]] = get_sampler_params()
logger = get_logger(__name__)


class BuilderConfig(BaseModel):
    data_designer: DataDesignerConfig
    datastore: DatastoreSettings | None = None
    skip_fetch_seed_column_names: bool = False


class DataDesignerConfigBuilder:
    """Builder for Data Designer configurations.

    This class provides a fluent interface for building Data Designer configurations.
    It allows you to add columns, constraints, and other configuration options to your
    Data Designer configuration.
    """

    @classmethod
    def from_config(cls, config: dict | str | Path | BuilderConfig) -> Self:
        if isinstance(config, BuilderConfig):
            builder_config = config
        else:
            json_config = make_date_obj_serializable(smart_load_yaml(config))
            builder_config = BuilderConfig.model_validate(json_config)

        builder = cls(model_configs=builder_config.data_designer.model_configs)
        config = builder_config.data_designer

        for col in config.columns:
            if isinstance(col, LLMGenColumn):
                col_dict = col.model_dump()
                if col.output_type == OutputType.STRUCTURED:
                    col = LLMStructuredColumn(**col_dict)
                elif col.output_type == OutputType.CODE:
                    col = LLMCodeColumn(**col_dict)
                else:
                    col = LLMTextColumn(**col_dict)
            builder.add_column(col)

        if config.constraints:
            for constraint in config.constraints:
                builder.add_constraint(
                    target_column=constraint.target_column,
                    type=constraint.type,
                    params=constraint.params,
                )

        if config.seed:
            builder.with_seed_dataset(
                repo_id=config.seed.repo_id,
                filename=config.seed.filename,
                datastore=builder_config.datastore,
                sampling_strategy=config.seed.sampling_strategy,
                with_replacement=config.seed.with_replacement,
                skip_fetch_column_names=builder_config.skip_fetch_seed_column_names,
            )

        if config.person_samplers:
            builder.with_person_samplers(config.person_samplers)
        if config.evaluation:
            builder.with_evaluation_report(config.evaluation)

        return builder

    def __init__(self, model_configs: list[ModelConfig] | str | Path | None = None):
        self._columns = {}
        self._model_configs = self._load_model_configs(model_configs)
        self._constraints: list[ColumnConstraint] = []
        self._latent_person_columns: dict[str, PersonSamplerParams] = {}
        self._seed: Seed | None = None
        self._evaluation: EvaluateDataDesignerDatasetSettings | None = None
        self._info = DataDesignerInfo()

    @property
    def model_configs(self) -> list[ModelConfig]:
        return self._model_configs

    @property
    def allowed_references(self) -> list[str]:
        """All referenceable variables allowed in prompt templates and expressions."""
        seed_column_names = [c.name for c in self.seed_columns]
        sampler_column_names = [c.name for c in self.sampler_columns]
        dag_column_names = sum([[c.name] + c.side_effect_columns for c in self._dag_columns], [])
        return seed_column_names + sampler_column_names + dag_column_names

    @property
    def info(self) -> DataDesignerInfo:
        return self._info

    @property
    def seed_columns(self) -> list[DataSeedColumn]:
        """Columns from the seed dataset, if one is defined."""
        return self.get_columns_of_type(DataSeedColumn)

    @property
    def sampler_columns(self) -> list[SamplerColumn]:
        """Columns that use a sampler to generate data."""
        return self.get_columns_of_type(SamplerColumn)

    @property
    def llm_gen_columns(self) -> list[LLMGenColumn]:
        """Columns that use an LLM to generate data."""
        return self.get_columns_of_type(LLMGenColumn)

    @property
    def llm_text_columns(self) -> list[LLMTextColumn]:
        """Columns that use an LLM to generate text data."""
        return self.get_columns_of_type(LLMTextColumn)

    @property
    def llm_code_columns(self) -> list[LLMCodeColumn]:
        """Columns that use an LLM to generate code."""
        return self.get_columns_of_type(LLMCodeColumn)

    @property
    def llm_structured_columns(self) -> list[LLMStructuredColumn]:
        """Columns that use an LLM to generate structured data."""
        return self.get_columns_of_type(LLMStructuredColumn)

    @property
    def llm_judge_columns(self) -> list[LLMJudgeColumn]:
        """Columns that use an LLM to judge the quality of generated data."""
        return self.get_columns_of_type(LLMJudgeColumn)

    @property
    def code_validation_columns(self) -> list[CodeValidationColumn]:
        """Columns with results from validation of columns with code."""
        return self.get_columns_of_type(CodeValidationColumn)

    @property
    def validation_with_remote_endpoint_columns(self) -> list[ValidationWithRemoteEndpointColumn]:
        """Columns with results from arbitrary validation of columns."""
        return self.get_columns_of_type(ValidationWithRemoteEndpointColumn)

    @property
    def expression_columns(self) -> list[ExpressionColumn]:
        """Columns that generate data from a jinja2 expression."""
        return self.get_columns_of_type(ExpressionColumn)

    @property
    def drop_columns(self) -> list[str]:
        """Names of columns marked with drop=True (computed on demand)."""
        return [name for name, col in self._columns.items() if getattr(col, "drop", False)]

    @property
    def has_latent_columns(self) -> bool:
        """Whether the configuration has latent columns."""
        return len(self._latent_person_columns) > 0

    @property
    def _dag_columns(self) -> list[DAGColumnT]:
        """Columns that are topologically sorted using a DAG."""
        return (
            self.llm_gen_columns
            + self.llm_judge_columns
            + self.code_validation_columns
            + self.validation_with_remote_endpoint_columns
            + self.expression_columns
        )

    @property
    def _categorical_columns(self) -> list[SamplerColumn]:
        """Columns that contain categorical data."""
        return [
            col
            for col in self.sampler_columns
            if (col.type == SamplerType.CATEGORY or col.type == SamplerType.SUBCATEGORY)
        ]

    def add_column(
        self,
        column: DataDesignerColumnT | None = None,
        *,
        name: str | None = None,
        type: ColumnProviderTypeT = ProviderType.LLM_TEXT,
        **kwargs,
    ) -> Self:
        """Add Data Designer column to the current Data Designer configuration.

        If no column object is provided, you must provide the `name`, `type`, and any
        additional keyword arguments that are required by the column constructor. For
        each column type, you can directly access their constructor parameters by
        importing from the `params` module: `gretel_client.data_designer.params`.

        Args:
            column: Data Designer column object to add.
            name: Name of the column to add. This is only used if `column` is not provided.
            type: Column type to add. This is only used if `column` is not provided.
            **kwargs: Additional keyword arguments to pass to the column constructor.

        Returns:
            The current Data Designer config builder instance.
        """
        if column is None:
            if isinstance(type, str):
                type = self._validate_column_provider_type(type)
            column = self._get_column_from_kwargs(name=name, type=type, **kwargs)
        column_types = DataDesignerColumnT.__args__
        if not isinstance(column, column_types):
            raise DataDesignerValidationError(
                f"🛑 {_type_builtin(column)} is not a valid column type. "
                f"Columns must be one of {[t.__name__ for t in DataDesignerColumnT.__args__]}."
            )
        if column.name in self._latent_person_columns:
            if not isinstance(column, SamplerColumn) or column.type != SamplerType.PERSON:
                raise DataDesignerValidationError(
                    f"🛑 The name `{column.name}` is already the name of a person sampler created "
                    "using `with_person_samplers`. Please ensure that all person sampler and "
                    "column names are unique."
                )
            self._latent_person_columns[column.name] = column.params
        self._columns[column.name] = column
        return self

    def add_constraint(
        self,
        target_column: str,
        type: ConstraintType,
        params: dict[str, str | float] | ColumnConstraintParams,
    ) -> Self:
        """Add a constraint to the current Data Designer configuration.

        Currently, constraints are only supported for numerical samplers.
        The `type` must be one of:

            - "scalar_inequality": Constraint between a column and a scalar value.
            - "column_inequality": Constraint between two columns.

        The `params` must be a dictionary of `ColumnConstraintParams` object with the
        following keyword arguments:

            - "rhs": The right-hand side of the inequality.
            - "operator": One of the following inequality operators:

                - "gt": Greater than.
                - "ge": Greater than or equal to.
                - "lt": Less than.
                - "le": Less than or equal to.

        Args:
            target_column: The column that the constraint applies to.
            type: Type of constraint to add.
            params: Parameters for the constraint.

        Returns:
            The current Data Designer config builder instance.
        """
        if isinstance(params, dict):
            params = ColumnConstraintParams.model_validate(params)
        self._constraints.append(
            ColumnConstraint(
                target_column=target_column,
                type=type,
                params=params,
            )
        )
        return self

    def build(self, *, skip_validation: bool = False, raise_exceptions: bool = False) -> DataDesignerConfig:
        """Build and instance of the current Data Designer configuration.

        Args:
            skip_validation: Whether to skip validation of the configuration.
            raise_exceptions: Whether to raise an exception if the configuration is invalid.

        Returns:
            The current Data Designer config object.
        """
        if not skip_validation:
            self.validate(raise_exceptions=raise_exceptions)

        columns = [
            c
            for c in self._columns.values()
            if c.name not in self._latent_person_columns
            if not isinstance(c, DataSeedColumn)
        ]
        person_samplers = {
            c.name: c.params
            for c in self.sampler_columns
            if c.type == SamplerType.PERSON
            if c.name in self._latent_person_columns
        }
        return DataDesignerConfig(
            model_configs=self._model_configs,
            seed=self._seed,
            person_samplers=person_samplers or None,
            columns=columns,
            constraints=self._constraints or None,
            evaluation=self._evaluation,
        )

    def delete_constraints(self, target_column: str) -> Self:
        """Deletes the constraints for the given target column."""
        self._constraints = [c for c in self._constraints if c.target_column != target_column]
        return self

    def delete_column(self, column_name: str) -> Self:
        """Deletes the column with the given name."""
        if isinstance(self._columns.get(column_name), DataSeedColumn):
            raise ValueError("Seed columns cannot be deleted. Please update the seed dataset instead.")
        self._columns.pop(column_name, None)
        return self

    def delete_evaluation_settings(self) -> Self:
        """Deletes the evaluation settings for the current Data Designer configuration."""
        self._evaluation = None
        return self

    def get_column(self, name: str) -> DataDesignerColumnT:
        """Get a column by name."""
        return self._columns[name]

    def get_columns_of_type(self, column_type: Type[DataDesignerColumnT]) -> list[DataDesignerColumnT]:
        """Returns all columns of the given type."""
        return [col for col in self._columns.values() if isinstance(col, column_type)]

    def get_constraints(self, target_column: str) -> list[ColumnConstraint]:
        """Returns the constraints for the given target column."""
        return [c for c in self._constraints if c.target_column == target_column]

    def get_evaluation_settings(self) -> EvaluateDataDesignerDatasetSettings | None:
        """Returns the evaluation settings for the current Data Designer configuration."""
        return self._evaluation

    def get_seed_settings(self) -> Seed | None:
        """Returns the seed settings for the current Data Designer configuration."""
        return self._seed

    def validate(self, *, raise_exceptions: bool = False) -> Self:
        """Validate the current Data Designer configuration.

        Args:
            raise_exceptions: Whether to raise an exception if the configuration is invalid.

        Returns:
            The current Data Designer config builder instance.
        """

        violations = validate_data_designer_config(
            columns=list(self._columns.values()), allowed_references=self.allowed_references
        )
        rich_print_violations(violations)
        if raise_exceptions and len([v for v in violations if v.level == ViolationLevel.ERROR]) > 0:
            raise DataDesignerValidationError(
                "🛑 Your configuration contains validation errors. Please address the indicated issues and try again."
            )
        if len(violations) == 0 and not raise_exceptions:
            logger.info("✅ Validation passed")
        return self

    def with_evaluation_report(self, settings: EvaluateDataDesignerDatasetSettings | None = None) -> Self:
        """Add an evaluation report to the current Data Designer configuration.

        Args:
            settings: Evaluation report settings.

        Returns:
            The current Data Designer config builder instance.
        """
        settings = settings or EvaluateDataDesignerDatasetSettings(
            llm_judge_columns=[c.name for c in self.llm_judge_columns if not c.drop],
            validation_columns=[c.name for c in self.code_validation_columns if not c.drop],
            defined_categorical_columns=[c.name for c in self._categorical_columns if not c.drop],
        )
        self._evaluation = EvaluateDataDesignerDatasetSettings.model_validate(settings)
        return self

    def with_seed_dataset(
        self,
        repo_id: str,
        filename: str,
        dataset_path: str | Path | None = None,
        *,
        datastore: DatastoreSettings | dict | None = None,
        sampling_strategy: SamplingStrategy = SamplingStrategy.ORDERED,
        with_replacement: bool = False,
        skip_fetch_column_names: bool = False,
        **kwargs,
    ) -> Self:
        """Add a seed dataset to the current Data Designer configuration.

        The `repo_id` and `filename` arguments follow the Hugging Face Hub API format. The dataset will be
        identified with the `repo_id/filename` string. If your dataset is not in the datastore, you must
        provide the `dataset_path` argument to upload the dataset to the datastore.

        Each synthetically generated record will be concatenated with a single row of the seed dataset, giving
        it access to all the columns in that row as context. This means when `with_replacement = False` (the default),
        you are limited to generating the number of rows in the seed dataset.

        Args:
            repo_id: Dataset datastore ID (format: repo-namespace/repo-name).
            filename: Name of the dataset file including the extension.
            dataset_path: Path to a dataset file. If provided, the dataset will be uploaded to the datastore.
                Otherwise, it is assumed that the dataset is already in the datastore.
            datastore: Datastore settings including the endpoint and optional token.
            sampling_strategy: Sampling strategy to use for the seed dataset: "ordered" or "shuffle".
            with_replacement: Whether to sample with replacement. If False, you are limited to generating
                the number of rows in the seed dataset.
            skip_fetch_column_names: If True, the column names will not be fetched from the dataset.
            **kwargs: Additional keyword arguments to pass to the `upload_file` method of the Hugging Face Hub API.

        Returns:
            The current Data Designer config builder instance.
        """
        dataset_id = f"{repo_id}/{filename}"

        if dataset_path is not None:
            self._upload_to_hf_hub(
                dataset_path=dataset_path,
                filename=filename,
                repo_id=repo_id,
                datastore=datastore,
                **kwargs,
            )

        self._seed = Seed(
            dataset=dataset_id,
            sampling_strategy=sampling_strategy,
            with_replacement=with_replacement,
        )

        if not skip_fetch_column_names:
            column_names = self._fetch_seed_dataset_column_names(repo_id, filename, dataset_path, datastore)
            for column_name in column_names:
                self._columns[column_name] = DataSeedColumn(name=column_name, dataset=dataset_id)

        return self

    def with_person_samplers(
        self,
        person_samplers: dict[str, PersonSamplerParams],
        *,
        keep_person_columns: bool = False,
    ) -> Self:
        """Define latent person samplers that will be dropped at the end of the workflow.

        Person samplers defined with this method are latent in the sense that they give
        you access to person objects with attributes that can be referenced by other columns,
        but the objects themselves are dropped from the final dataset. This is useful
        when you just need access to certain person attributes but don't need the entire
        object in the final dataset.

        If you want to keep the person sampler columns in the final dataset, you have two
        options. You can either set `keep_person_columns` to `True` or you can add person
        samplers as columns using the `add_column` method.

        Args:
            person_samplers: Dictionary of person sampler parameters. The keys are the names
                of the person samplers and the values are the parameters for each sampler.
            keep_person_columns: If True, keep the person sampler columns in the final dataset.

        Returns:
            The current Data Designer config builder instance.
        """
        for name, params in person_samplers.items():
            person_params = PersonSamplerParams.model_validate(params)
            self.add_column(
                SamplerColumn(
                    name=name,
                    type=SamplerType.PERSON,
                    params=person_params.model_dump(),
                )
            )
            if not keep_person_columns:
                self._latent_person_columns[name] = person_params

        return self

    def write_config(self, path: str | Path, indent: int | None = 2, **kwargs) -> None:
        """Write the current configuration object of this Data Designer instance to a file.

        Args:
            path: Path to the file to write the configuration to.
            indent: Indentation for the YAML or JSON file.
        """
        cfg = self.build()
        suffix = Path(path).suffix
        if suffix in {".yaml", ".yml"}:
            cfg.to_yaml(path, indent=indent, **kwargs)
        elif suffix == ".json":
            cfg.to_json(path, indent=indent, **kwargs)
        else:
            raise ValueError(f"🛑 Unsupported file type: {suffix}. Must be `.yaml`, `.yml` or `.json`.")

    @staticmethod
    def _load_model_configs(model_configs: list[ModelConfig] | str | Path | None) -> list[ModelConfig]:
        if model_configs is None:
            return []
        if isinstance(model_configs, list) and all(isinstance(mc, ModelConfig) for mc in model_configs):
            return model_configs
        json_config = smart_load_yaml(model_configs)
        if "model_configs" not in json_config:
            raise ValueError(
                "The list of model configs must be provided under model_configs in the YAML configuration file."
            )
        return [ModelConfig.model_validate(mc) for mc in json_config["model_configs"]]

    @staticmethod
    def _get_column_from_kwargs(name: str, type: ColumnProviderTypeT, **kwargs) -> DataDesignerColumnT:
        """Create a concrete Data Designer column object from kwargs.

        Args:
            name: Name of the column.
            type: Type of the column.
            **kwargs: Keyword arguments to pass to the column constructor.

        Returns:
            Data Designer column object of the appropriate type.
        """
        if name is None or type is None:
            raise ValueError("You must provide both `name` and `type` to add a column using kwargs.")
        column_klass = None
        if type == ProviderType.LLM_TEXT:
            column_klass = LLMTextColumn
        elif type == ProviderType.LLM_CODE:
            column_klass = LLMCodeColumn
        elif type == ProviderType.LLM_STRUCTURED:
            column_klass = LLMStructuredColumn
        elif type == ProviderType.LLM_JUDGE:
            column_klass = LLMJudgeColumn
        elif type == ProviderType.CODE_VALIDATION:
            column_klass = CodeValidationColumn
        elif type == ProviderType.EXPRESSION:
            column_klass = ExpressionColumn
        else:
            kwargs["params"] = _SAMPLER_PARAMS[type](**kwargs.get("params", {}))
            kwargs["type"] = type
            column_klass = SamplerColumn

        return column_klass(name=name, **kwargs)

    @staticmethod
    def _check_convert_to_json_str(
        column_names: list[str], *, indent: int | str | None = None
    ) -> list[str] | str | None:
        """Convert a list of column names to a JSON string if the list is long.

        This function helps keep AIDD's __repr__ output clean and readable.

        Args:
            column_names: List of column names.
            indent: Indentation for the JSON string.

        Returns:
            List of column names or a JSON string if the list is long.
        """
        return (
            None
            if len(column_names) == 0
            else (
                column_names
                if len(column_names) < REPR_LIST_LENGTH_USE_JSON
                else json.dumps(column_names, indent=indent)
            )
        )

    @staticmethod
    def _resolve_datastore(datastore: DatastoreSettings | dict | None) -> DatastoreSettings:
        if isinstance(datastore, DatastoreSettings):
            return datastore
        elif isinstance(datastore, dict):
            return DatastoreSettings.model_validate(datastore)
        else:
            raise ValueError("🛑 Datastore settings are required for uploading datasets to the datastore.")

    @staticmethod
    def _validate_column_provider_type(column_provider_type: str) -> ColumnProviderTypeT:
        """Validate the given column provider type and return the appropriate enum."""
        valid_provider_types = {t.value for t in list(ProviderType)}
        valid_sampling_source_types = {t.value for t in list(SamplerType)}
        combined_valid_types = valid_provider_types.union(valid_sampling_source_types)
        if column_provider_type not in combined_valid_types:
            raise ValueError(
                f"🛑 Invalid column provider type: '{column_provider_type}'. "
                f"Valid options are: {list(combined_valid_types)}"
            )
        elif column_provider_type in valid_provider_types:
            return ProviderType(column_provider_type)
        else:
            return SamplerType(column_provider_type)

    @staticmethod
    def _validate_dataset_path(dataset_path: str | Path) -> Path:
        if not Path(dataset_path).is_file():
            raise ValueError("🛑 To upload a dataset to the datastore, you must provide a valid file path.")
        if not Path(dataset_path).name.endswith((".parquet", ".csv", ".json", ".jsonl")):
            raise ValueError(
                "🛑 Dataset files must be in `parquet`, `csv`, or `json` (orient='records', lines=True) format."
            )
        return Path(dataset_path)

    def _fetch_seed_dataset_column_names(
        self,
        repo_id: str,
        filename: str,
        dataset_path: str | Path | None = None,
        datastore: DatastoreSettings | dict | None = None,
    ) -> list[str]:
        if dataset_path is not None:
            if filename.endswith(".parquet"):
                return pq.ParquetFile(dataset_path).schema.names
            elif filename.endswith(".json") or filename.endswith(".jsonl"):
                return pd.read_json(dataset_path, orient="records", lines=True, nrows=1).columns.tolist()
            elif filename.endswith(".csv"):
                return pd.read_csv(dataset_path, nrows=1).columns.tolist()

        datastore = self._resolve_datastore(datastore)
        fs = HfFileSystem(endpoint=datastore.endpoint, token=datastore.token)
        with fs.open(f"datasets/{repo_id}/{filename}") as f:
            if filename.endswith(".parquet"):
                return pq.ParquetFile(f).schema.names
            elif filename.endswith(".json") or filename.endswith(".jsonl"):
                return pd.read_json(f, orient="records", lines=True, nrows=1).columns.tolist()
            elif filename.endswith(".csv"):
                return pd.read_csv(f, nrows=1).columns.tolist()

        raise ValueError(f"🛑 Unsupported file type: {filename}")

    def _upload_to_hf_hub(
        self,
        dataset_path: str | Path,
        filename: str,
        repo_id: str,
        datastore: DatastoreSettings,
        **kwargs,
    ) -> str:
        datastore = self._resolve_datastore(datastore)
        dataset_path = self._validate_dataset_path(dataset_path)
        hfapi = HfApi(endpoint=datastore.endpoint, token=datastore.token)
        hfapi.create_repo(repo_id, exist_ok=True, repo_type="dataset")
        hfapi.upload_file(
            path_or_fileobj=dataset_path,
            path_in_repo=filename,
            repo_id=repo_id,
            repo_type="dataset",
            **kwargs,
        )
        return f"{repo_id}/{filename}"

    def __repr__(self) -> str:
        if len(self._columns) == 0:
            return f"{self.__class__.__name__}()"

        md = DataDesignerMetadata.from_config_builder(self)
        props_to_repr = {
            "person_samplers": self._check_convert_to_json_str(md.person_samplers),
            "seed_dataset": (None if self._seed is None else f"'{self._seed.dataset}'"),
        }

        for name in [
            "seed_columns",
            "sampler_columns",
            "llm_text_columns",
            "llm_code_columns",
            "llm_structured_columns",
            "llm_judge_columns",
            "validation_columns",
            "expression_columns",
        ]:
            props_to_repr[name] = self._check_convert_to_json_str(getattr(md, name), indent=8)

        repr_string = f"{self.__class__.__name__}(\n"
        for k, v in props_to_repr.items():
            if v is not None:
                v_indented = v if "[" not in v else f"{v[:-1]}" + "    " + v[-1]
                repr_string += f"    {k}: {v_indented}\n"
        repr_string += ")"
        return repr_string

    def _repr_html_(self) -> str:
        repr_string = self.__repr__()
        formatter = HtmlFormatter(style=DEFAULT_REPR_HTML_STYLE, cssclass="code")
        highlighted_html = highlight(repr_string, PythonLexer(), formatter)
        css = formatter.get_style_defs(".code")
        return REPR_HTML_TEMPLATE.format(css=css, highlighted_html=highlighted_html)
