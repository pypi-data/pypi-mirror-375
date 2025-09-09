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

from typing import Any

from pydantic import BaseModel, Field, computed_field, model_validator
from typing_extensions import Self

from .base import ConfigBase
from .constants import (
    VALIDATE_PYTHON_COLUMN_SUFFIXES,
    VALIDATE_SQL_COLUMN_SUFFIXES,
)
from .params.code import SQL_DIALECTS, CodeLang
from .params.llm_gen import (
    GenerateColumnFromExpression,
    GenerateColumnFromTemplate,
    JudgeWithLlm,
    OutputType,
)
from .params.mixins import (
    WithDAGColumnMixin,
    WithDropColumnMixin,
    WithPrettyRepr,
)
from .params.samplers import ConditionalDataColumn
from .utils import assert_valid_jinja2_template, get_prompt_template_keywords

##########################################################
# Sampler column config
##########################################################


class SamplerColumn(WithDropColumnMixin, WithPrettyRepr, ConditionalDataColumn):
    """Data Designer column that uses a sampler to generate data.

    Sampler columns can be conditioned on other sampler columns using the `conditional_params` argument,
    which is a dictionary of conditions and parameters. Conditions are specified as strings involving
    the names of other sampler columns and the operators `==`, `!=`, `>`, `>=`, `<`, `<=`.

    Args:
        name: Name of the column.
        type: Type of sampler to use.
        params: Parameters for the sampler. If conditional_params are provided,
            these parameters will be used as the default when no condition is met.
        conditional_params: Conditional parameters for the sampler. The keys of the
            dict are conditions from other columns, and the values are the parameters
            for the sampler.
        convert_to: Optional data conversion to apply to the generated data. For
            numerical columns this can be "int" or "float", and for datetime columns,
            this can be a datetime format string (e.g. "%Y/%m/%d").
    """


##########################################################
# LLM-generated column configs
##########################################################


class LLMGenColumn(
    WithDropColumnMixin,
    WithPrettyRepr,
    GenerateColumnFromTemplate,
    WithDAGColumnMixin,
):
    @model_validator(mode="before")
    @classmethod
    def _set_output_format(cls, data: Any) -> Any:
        if "output_format" not in data:
            return data

        if isinstance(data["output_format"], type) and issubclass(data["output_format"], BaseModel):
            data["output_format"] = data["output_format"].model_json_schema()

        return data

    @property
    def required_columns(self) -> list[str]:
        return list(get_prompt_template_keywords(self.prompt))

    @property
    def step_name(self) -> str:
        return f"generating-{OutputType(self.output_type).value}-column-{self.name}"

    @model_validator(mode="after")
    def assert_prompt_valid_jinja(self) -> Self:
        assert_valid_jinja2_template(self.prompt)
        return self

    def model_post_init(self, __context: Any) -> None:
        # Mark these fields as explicitly set. This is a workaround to ensure
        # their values are always sent over the wire, since stainless hardcodes
        # `exclude_unset=True` by default.
        self.__pydantic_fields_set__.add("output_type")
        self.__pydantic_fields_set__.add("output_format")
        self.__pydantic_fields_set__.add("model_alias")

    def to_specific_column_type(self):
        if self.output_type == OutputType.TEXT:
            return LLMTextColumn(**self.model_dump())
        elif self.output_type == OutputType.CODE:
            return LLMCodeColumn(**self.model_dump())
        elif self.output_type == OutputType.STRUCTURED:
            return LLMStructuredColumn(**self.model_dump())
        else:
            raise NotImplementedError(f"Unknown output type: {self.output_type}")


class LLMTextColumn(LLMGenColumn):
    """Data Designer column that uses an LLM to generate text.

    Args:
        name: Name of the column.
        prompt: Prompt template to use for generation.
        system_prompt: System prompt for the LLM. Useful for defining the LLM's role,
            tone, and other instructions. However, do not provide any instructions
            related to the output format, as this is handled internally by AIDD.
        model_alias: Model alias to use for the LLM.
    """

    model_alias: str
    output_type: OutputType = Field(default=OutputType.TEXT)


class LLMCodeColumn(LLMGenColumn):
    """Data Designer column that uses an LLM to generate code.

    Args:
        name: Name of the column.
        prompt: Prompt template to use for generation.
        system_prompt: System prompt for the LLM. Useful for defining the LLM's role,
            tone, and other instructions. However, do not provide any instructions
            related to the output format, as this is handled internally by AIDD.
        model_alias: Model alias to use for the LLM.
    """

    model_alias: str
    output_type: OutputType = Field(default=OutputType.CODE)


class LLMStructuredColumn(LLMGenColumn):
    """Data Designer column that uses an LLM to generate structured data.

    Args:
        name: Name of the column.
        prompt: Prompt template to use for generation.
        system_prompt: System prompt for the LLM. Useful for defining the LLM's role,
            tone, and other instructions. However, do not provide any instructions
            related to the output format, as this is handled internally by AIDD.
        model_alias: Model alias to use for the LLM.
    """

    model_alias: str
    output_type: OutputType = Field(default=OutputType.STRUCTURED)


class LLMJudgeColumn(WithDropColumnMixin, WithPrettyRepr, JudgeWithLlm, WithDAGColumnMixin):
    """Data Designer column for llm-as-a-judge with custom rubrics.

    Args:
        name: Name of the column.
        prompt: Prompt template to use for llm-as-a-judge.
        rubrics: List of rubrics to use for evaluation.
        num_samples_to_judge: Number of samples to judge. If None, the full dataset
            will be judged. If less than the total number of rows in the dataset,
            a random sample of the specified size will be judged.
        model_alias: Model alias to use for the LLM.
    """

    result_column: str = Field(..., alias="name")

    @computed_field
    def name(self) -> str:
        return self.result_column

    @property
    def required_columns(self) -> list[str]:
        return list(get_prompt_template_keywords(self.prompt))

    @property
    def step_name(self) -> str:
        return f"using-llm-to-judge-column-{self.name}"

    def model_post_init(self, __context: Any) -> None:
        self.__pydantic_fields_set__.add("model_alias")
        self.__pydantic_fields_set__.add("result_column")


##########################################################
# Validator column configs
##########################################################


class CodeValidationColumn(WithDropColumnMixin, WithPrettyRepr, ConfigBase, WithDAGColumnMixin):
    """Data Designer column for validating code in another column.

    Code validation is currently supported for Python and SQL.

    Args:
        name: Name of the column.
        code_lang: Language of the code to validate.
        target_column: Column with code to validate.
    """

    name: str
    code_lang: CodeLang
    target_column: str

    @property
    def required_columns(self) -> list[str]:
        return [self.target_column]

    @property
    def side_effect_columns(self) -> list[str]:
        suffixes = VALIDATE_SQL_COLUMN_SUFFIXES if self.code_lang in SQL_DIALECTS else VALIDATE_PYTHON_COLUMN_SUFFIXES
        columns = []
        for suffix in suffixes:
            columns.append(f"{self.target_column}{suffix}")
        return columns

    @property
    def step_name(self) -> str:
        return f"validating-code-in-column-{self.target_column}"


class ValidationWithRemoteEndpointColumn(WithDropColumnMixin, WithPrettyRepr, ConfigBase, WithDAGColumnMixin):
    """Data Designer column for validating arbitrary fields using a remote endpoint.

    Args:
        name: Name of the column.
        target_columns: Columns with content to validate.
        validator: URL of the remote endpoint to use for validation.
        batch_size: Number of records to validate in each batch (default: 10).
        timeout: Timeout for the remote endpoint (default: 30.0).
    """

    name: str
    target_columns: list[str]
    validator: str
    batch_size: int = 10
    timeout: float = 30.0

    @property
    def required_columns(self) -> list[str]:
        return self.target_columns

    @property
    def step_name(self) -> str:
        return f"validating-with-remote-endpoint-column-{self.name}"


##########################################################
# Expression column config
##########################################################


class ExpressionColumn(
    WithDropColumnMixin,
    WithPrettyRepr,
    GenerateColumnFromExpression,
    WithDAGColumnMixin,
):
    """Data Designer column for generated data based on jinja2 expressions.

    Args:
        name: Name of the column.
        expr: Expression to use for generation.
        dtype: Data type of the column. Can be "str" (default), "int",
            "float", or "bool".
    """

    @property
    def required_columns(self) -> list[str]:
        return list(get_prompt_template_keywords(self.expr))

    @model_validator(mode="after")
    def assert_expression_valid_jinja(self) -> Self:
        assert_valid_jinja2_template(self.expr)
        return self

    @property
    def step_name(self) -> str:
        return f"rendering-expression-column-{self.name}"


##########################################################
# Data seed column config (for bookkeeping purposes)
##########################################################


class DataSeedColumn(WithPrettyRepr, ConfigBase):
    """Column in a seed dataset.

    This object is meant for internal bookkeeping and should not be used directly.

    Args:
        name: Name of the column.
        file_id: File ID of the seed dataset.
    """

    name: str
    dataset: str
