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

from enum import Enum
from typing import Union

import pandas as pd
from pydantic import BaseModel
from typing_extensions import TypeAlias

from .columns import (
    CodeValidationColumn,
    ExpressionColumn,
    LLMCodeColumn,
    LLMGenColumn,
    LLMJudgeColumn,
    LLMStructuredColumn,
    LLMTextColumn,
    SamplerColumn,
    ValidationWithRemoteEndpointColumn,
)
from .params.samplers import SamplerType


class ProviderType(str, Enum):
    LLM_TEXT = "llm-text"
    LLM_CODE = "llm-code"
    LLM_STRUCTURED = "llm-structured"
    LLM_JUDGE = "llm-judge"
    CODE_VALIDATION = "code-validation"
    EXPRESSION = "expression"


DAGColumnT: TypeAlias = Union[
    LLMGenColumn,
    LLMTextColumn,
    LLMCodeColumn,
    LLMStructuredColumn,
    LLMJudgeColumn,
    CodeValidationColumn,
    ValidationWithRemoteEndpointColumn,
    ExpressionColumn,
]
DataDesignerColumnT: TypeAlias = Union[SamplerColumn, DAGColumnT]
ColumnProviderTypeT: TypeAlias = Union[SamplerType, ProviderType]
TaskOutputT: TypeAlias = Union[pd.DataFrame, BaseModel]
