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

from pydantic import BaseModel, Field


class DatastoreSettings(BaseModel):
    """Configuration for interacting with a datastore."""

    endpoint: str = Field(
        ...,
        description="Datastore endpoint. Use 'https://huggingface.co' for the Hugging Face Hub.",
    )
    token: str | None = Field(default=None, description="If needed, token to use for authentication.")
