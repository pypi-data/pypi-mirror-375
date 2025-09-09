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

from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ..base import ConfigBase

##########################################################
# Enums
##########################################################


class DistributionType(str, Enum):
    UNIFORM = "uniform"
    MANUAL = "manual"


class Dtype(str, Enum):
    INT = "int"
    FLOAT = "float"
    STR = "str"
    BOOL = "bool"


class LLMJudgePromptTemplateType(str, Enum):
    # TODO: eliminate to use new judge task format
    TEXT_TO_PYTHON = "text_to_python"
    TEXT_TO_SQL = "text_to_sql"


class OutputType(str, Enum):
    CODE = "code"
    TEXT = "text"
    STRUCTURED = "structured"


##########################################################
# Config parameters
##########################################################


class ManualDistributionParams(ConfigBase):
    values: Annotated[List[float], Field(min_length=1, title="Values")]
    weights: Annotated[Optional[List[float]], Field(title="Weights")] = None


class ManualDistribution(ConfigBase):
    distribution_type: Optional[DistributionType] = "manual"
    params: ManualDistributionParams


class UniformDistributionParams(ConfigBase):
    low: Annotated[float, Field(title="Low")]
    high: Annotated[float, Field(title="High")]


class UniformDistribution(ConfigBase):
    distribution_type: Optional[DistributionType] = "uniform"
    params: UniformDistributionParams


class InferenceParameters(ConfigBase):
    temperature: Annotated[
        Optional[Union[float, UniformDistribution, ManualDistribution]],
        Field(title="Temperature"),
    ] = None
    top_p: Annotated[
        Optional[Union[float, UniformDistribution, ManualDistribution]],
        Field(title="Top P"),
    ] = None
    max_tokens: Optional[int] = Field(default=None, ge=1, title="Max Tokens")
    max_parallel_requests: int = Field(default=4, ge=1, title="Max Parallel Requests")
    timeout: Optional[int] = Field(default=None, ge=1, title="Timeout")


class ApiEndpoint(ConfigBase):
    url: Annotated[str, Field(title="URL")]
    model_id: Annotated[str, Field(title="Model ID")]
    api_key: Annotated[Optional[str], Field(title="API Key")] = None
    provider_type: Annotated[str, Field(title="Provider Type", default="openai")]


class Model(ConfigBase):
    api_endpoint: Annotated[ApiEndpoint, Field(title="API Endpoint")]


class ModelConfig(ConfigBase):
    alias: Annotated[str, Field(title="Alias")]
    model: Annotated[str, Field(title="Model")]
    inference_parameters: InferenceParameters
    provider: Annotated[Optional[str], Field(title="Provider")] = None
    is_reasoner: Annotated[Optional[bool], Field(title="Is Reasoner")] = False


class Rubric(ConfigBase):
    scoring: Annotated[
        Dict[str, str],
        Field(
            description="Dictionary specifying score: description pairs for rubric scoring.",
            title="Scoring",
        ),
    ]
    name: Annotated[
        str,
        Field(description="A clear, pythonic class name for this rubric.", title="Name"),
    ]
    description: Annotated[
        Optional[str],
        Field(
            description="An informative and detailed assessment guide for using this rubric.",
            title="Description",
        ),
    ] = ""


class Modality(str, Enum):
    IMAGE = "image"


class ModalityDataType(str, Enum):
    URL = "url"
    BASE64 = "base64"


class ImageFormat(str, Enum):
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    gif = "gif"
    webp = "webp"


class ModalityContext(BaseModel):
    modality: Modality
    column_name: str
    data_type: ModalityDataType


class ImageContext(ModalityContext):
    modality: Modality = Modality.IMAGE
    image_format: Optional[ImageFormat] = None


##########################################################
# Task configs
##########################################################


class GenerateColumnFromExpression(ConfigBase):
    name: Annotated[str, Field(title="Name")]
    expr: Annotated[str, Field(title="Expr")]
    dtype: Annotated[Optional[Dtype], Field(title="Dtype")] = "str"


class GenerateColumnFromTemplate(ConfigBase):
    model_alias: Annotated[str, Field(title="Model Alias")]
    prompt: Annotated[str, Field(title="Prompt")]
    name: Annotated[Optional[str], Field(title="Name")] = "response"
    system_prompt: Annotated[Optional[str], Field(title="System Prompt")] = None
    output_type: Optional[OutputType] = "text"
    output_format: Annotated[Optional[Union[str, Dict[str, Any]]], Field(title="Output Format")] = None
    multi_modal_context: Annotated[Optional[list[ImageContext]], Field(title="Multi Modal Context")] = None
    failure_threshold: float = Field(default=0.2, ge=0.0, le=1.0)


class JudgeWithLlm(ConfigBase):
    model_alias: Annotated[str, Field(title="Model Alias")]
    prompt: Annotated[
        str,
        Field(
            description="Template for generating prompts.Use Jinja2 templates to reference dataset columns.",
            title="Prompt",
        ),
    ]
    num_samples_to_judge: Annotated[
        Optional[int],
        Field(
            description="Number of samples to judge.If unset or None, then defaults to judging all records. Default is None.",
            title="Num Samples To Judge",
        ),
    ] = None
    rubrics: Annotated[
        List[Rubric],
        Field(
            description="List of rubric configurations to use for evaluation.At least one must be provided.",
            min_length=1,
            title="Rubrics",
        ),
    ]
    result_column: Annotated[
        Optional[str],
        Field(description="Column name to store judge results.", title="Result Column"),
    ] = "llm_judge_results"
    judge_random_seed: Annotated[
        Optional[int],
        Field(
            description="Random seed to use for selecting samples to judge. Same seed ensures same samples are selected each time.",
            title="Judge Random Seed",
        ),
    ] = 2025
    failure_threshold: float = Field(default=0.2, ge=0.0, le=1.0)
