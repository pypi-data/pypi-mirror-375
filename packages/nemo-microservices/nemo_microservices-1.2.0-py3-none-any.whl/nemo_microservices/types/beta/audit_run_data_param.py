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

from typing_extensions import TypedDict

__all__ = ["AuditRunDataParam"]


class AuditRunDataParam(TypedDict, total=False):
    deprefix: bool
    """
    Remove the prompt from the start of the output (some models return the prompt as
    part of their output)
    """

    eval_threshold: float
    """Threshold for categorizing a detector output as a successful attack/hit"""

    generations: int
    """How many times to send each prompt for inference"""

    probe_tags: str

    seed: int

    user_agent: str
