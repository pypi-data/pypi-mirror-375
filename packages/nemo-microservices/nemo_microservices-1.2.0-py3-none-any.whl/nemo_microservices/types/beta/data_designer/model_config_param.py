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

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Required, TypeAlias, TypedDict

from .manual_distribution_param import ManualDistributionParam
from .uniform_distribution_param import UniformDistributionParam

__all__ = ["ModelConfigParam", "InferenceParameters", "InferenceParametersTemperature", "InferenceParametersTopP"]

InferenceParametersTemperature: TypeAlias = Union[float, UniformDistributionParam, ManualDistributionParam]

InferenceParametersTopP: TypeAlias = Union[float, UniformDistributionParam, ManualDistributionParam]


class InferenceParameters(TypedDict, total=False):
    max_parallel_requests: int

    max_tokens: int

    temperature: Optional[InferenceParametersTemperature]

    timeout: int

    top_p: Optional[InferenceParametersTopP]


class ModelConfigParam(TypedDict, total=False):
    alias: Required[str]

    inference_parameters: Required[InferenceParameters]

    model: Required[str]

    is_reasoner: bool

    provider: str
