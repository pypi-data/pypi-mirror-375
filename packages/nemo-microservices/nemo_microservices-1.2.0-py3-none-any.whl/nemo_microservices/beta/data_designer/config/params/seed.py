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
from typing import Optional

from pydantic import BaseModel

from ..base import ConfigBase


class SamplingStrategy(str, Enum):
    ORDERED = "ordered"
    SHUFFLE = "shuffle"


class Seed(ConfigBase):
    dataset: str
    sampling_strategy: SamplingStrategy = SamplingStrategy.ORDERED
    # TODO: Remove after moving to the new seed dataset generator.
    with_replacement: bool = False

    @property
    def repo_id(self) -> str:
        return "/".join(self.dataset.split("/")[:-1])

    @property
    def filename(self) -> str:
        return self.dataset.split("/")[-1]


class SampleFromDatasetConfig(BaseModel):
    num_samples: Optional[int] = None
    strategy: SamplingStrategy = SamplingStrategy.ORDERED
    with_replacement: bool = False
