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

from typing import Dict, Union, Optional

from ...._compat import PYDANTIC_V2, ConfigDict
from ...._models import BaseModel
from ..audit_module_config import AuditModuleConfig

__all__ = ["AuditPluginsDataOutput"]


class AuditPluginsDataOutput(BaseModel):
    buff_max: Optional[str] = None

    buff_spec: Optional[str] = None

    buffs: Optional[Dict[str, Union[AuditModuleConfig, object]]] = None

    buffs_include_original_prompt: Optional[bool] = None

    detector_spec: Optional[str] = None

    detectors: Optional[Dict[str, Union[AuditModuleConfig, object]]] = None

    extended_detectors: Optional[bool] = None

    generators: Optional[Dict[str, Union[AuditModuleConfig, object]]] = None

    harnesses: Optional[Dict[str, Union[AuditModuleConfig, object]]] = None

    model_name: Optional[str] = None

    model_type: Optional[str] = None

    probe_spec: Optional[str] = None

    probes: Optional[Dict[str, Union[AuditModuleConfig, object]]] = None

    if PYDANTIC_V2:
        # allow fields with a `model_` prefix
        model_config = ConfigDict(protected_namespaces=tuple())
