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
from datetime import datetime
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo
from ..audit_config_param import AuditConfigParam
from ..audit_target_param import AuditTargetParam
from ...shared_params.ownership import Ownership

__all__ = ["JobCreateParams", "Config", "Target"]


class JobCreateParams(TypedDict, total=False):
    config: Required[Config]
    """A reference to AuditConfig."""

    target: Required[Target]
    """A reference to AuditTarget."""

    id: str
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    created_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Timestamp for when the entity was created."""

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    namespace: str
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The URN of the project associated with this entity."""

    schema_version: str
    """The version of the schema for the object. Internal use only."""

    type_prefix: str
    """The type prefix of the entity ID.

    If not specified, it will be inferred from the entity type name, but this will
    likely result in long prefixes.
    """

    updated_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Timestamp for when the entity was last updated."""


Config: TypeAlias = Union[str, AuditConfigParam]

Target: TypeAlias = Union[str, AuditTargetParam]
