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
from typing import Any

import yaml
from pydantic import Field

from .base import ConfigBase
from .params.constraints import ColumnConstraint
from .params.evaluation import EvaluateDataDesignerDatasetSettings
from .params.llm_gen import ModelConfig
from .params.samplers import PersonSamplerParams
from .params.seed import Seed
from .type_aliases import DataDesignerColumnT


class DataDesignerConfig(ConfigBase):
    """Configuration for NeMo Data Designer."""

    model_configs: list[ModelConfig] | None = None
    seed: Seed | None = None
    person_samplers: dict[str, PersonSamplerParams] | None = None
    columns: list[DataDesignerColumnT] = Field(min_length=1)
    constraints: list[ColumnConstraint] | None = None
    evaluation: EvaluateDataDesignerDatasetSettings | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the Data Designer config to a dictionary."""
        return self.model_dump(mode="json", by_alias=True)

    def to_yaml(self, path: str | Path | None = None, *, indent: int | None = 2, **kwargs) -> str | None:
        """Convert the Data Designer config to a YAML string or file."""
        yaml_str = yaml.dump(self.to_dict(), indent=indent, **kwargs)
        if path is None:
            return yaml_str
        with open(path, "w") as f:
            f.write(yaml_str)

    def to_json(self, path: str | Path | None = None, *, indent: int | None = 2, **kwargs) -> str | None:
        """Convert the Data Designer config to a JSON string or file."""
        json_str = json.dumps(self.to_dict(), indent=indent, **kwargs)
        if path is None:
            return json_str
        with open(path, "w") as f:
            f.write(json_str)
