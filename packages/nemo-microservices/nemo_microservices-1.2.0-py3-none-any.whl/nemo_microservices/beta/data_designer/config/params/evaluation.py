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

from pydantic import Field, model_validator
from typing_extensions import Self

from ..base import ConfigBase


class EvaluateDatasetSettings(ConfigBase):
    ordered_list_like_columns: list[str] = Field(default_factory=list)
    list_like_columns: list[str] = Field(default_factory=list)
    columns_to_ignore: list[str] = Field(default_factory=list)


class EvaluateDataDesignerDatasetSettings(ConfigBase):
    llm_judge_columns: list[str] = Field(default_factory=list)
    columns_to_ignore: list[str] = Field(default_factory=list)
    validation_columns: list[str] = Field(default_factory=list)
    defined_categorical_columns: list[str] = Field(default_factory=list)
    model_alias: str | None = None

    @model_validator(mode="after")
    def check_for_llm_judge_columns(self) -> Self:
        if self.llm_judge_columns and "judged_by_llm" not in self.columns_to_ignore:
            self.columns_to_ignore.append("judged_by_llm")
        return self
