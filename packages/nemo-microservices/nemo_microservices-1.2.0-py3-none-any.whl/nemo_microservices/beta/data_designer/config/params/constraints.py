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
from typing import Annotated, Union

from pydantic import Field

from ..base import ConfigBase


class ConstraintType(str, Enum):
    SCALAR_INEQUALITY = "scalar_inequality"
    COLUMN_INEQUALITY = "column_inequality"


class InequalityOperator(str, Enum):
    LT = "lt"
    LE = "le"
    GT = "gt"
    GE = "ge"


class ColumnConstraintParams(ConfigBase):
    operator: InequalityOperator
    rhs: Annotated[Union[float, str], Field(title="Rhs")]


class ColumnConstraint(ConfigBase):
    target_column: Annotated[str, Field(title="Target Column")]
    type: ConstraintType
    params: ColumnConstraintParams
