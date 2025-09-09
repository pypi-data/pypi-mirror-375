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

from .params.samplers import SamplerType
from .utils import get_sampler_params
from .viz_tools import display_sampler_table


class DataDesignerInfo:
    def __init__(self):
        self._sampler_params = get_sampler_params()

    @property
    def sampler_table(self) -> None:
        display_sampler_table(self._sampler_params)

    @property
    def sampler_types(self) -> list[str]:
        return [s.value for s in SamplerType]

    def display_sampler(self, sampler_type: SamplerType) -> None:
        title = f"{SamplerType(sampler_type).value.replace('_', ' ').title()} Sampler"
        display_sampler_table({sampler_type: self._sampler_params[sampler_type]}, title=title)
