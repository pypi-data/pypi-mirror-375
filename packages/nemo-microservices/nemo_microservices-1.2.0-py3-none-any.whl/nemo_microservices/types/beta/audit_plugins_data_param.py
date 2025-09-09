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

from typing import Dict, Union
from typing_extensions import TypedDict

from .audit_class_config_param import AuditClassConfigParam
from .audit_module_config_param import AuditModuleConfigParam

__all__ = ["AuditPluginsDataParam"]


class AuditPluginsDataParam(TypedDict, total=False):
    buff_max: str

    buff_spec: str

    buffs: Dict[str, Union[AuditModuleConfigParam, AuditClassConfigParam]]

    buffs_include_original_prompt: bool

    detector_spec: str

    detectors: Dict[str, Union[AuditModuleConfigParam, AuditClassConfigParam]]

    extended_detectors: bool

    generators: Dict[str, Union[AuditModuleConfigParam, AuditClassConfigParam]]

    harnesses: Dict[str, Union[AuditModuleConfigParam, AuditClassConfigParam]]

    model_name: str

    model_type: str

    probe_spec: str

    probes: Dict[str, Union[AuditModuleConfigParam, AuditClassConfigParam]]
