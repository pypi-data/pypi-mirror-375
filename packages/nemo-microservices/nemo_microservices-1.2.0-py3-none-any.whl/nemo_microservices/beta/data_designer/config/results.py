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

from dataclasses import dataclass

import pandas as pd

from .logs import get_logger
from .type_aliases import TaskOutputT
from .viz_tools import DataDesignerMetadata, display_sample_record

logger = get_logger(__name__)


@dataclass
class PreviewResults:
    """Results from a Data Designer preview run.

    Args:
        ndd_metadata: Metadata object with information about the dataset.
        output: Output of the preview run.
        evaluation_results: Evaluation results of the preview run if the workflow
            was configured to run evaluation.
        success: If True, the preview run was successful.
    """

    data_designer_metadata: DataDesignerMetadata
    output: TaskOutputT | None = None
    evaluation_results: dict | None = None
    success: bool = True
    _display_cycle_index: int = 0

    @property
    def dataset(self) -> pd.DataFrame | None:
        """Dataset object from the preview."""
        if isinstance(self.output, pd.DataFrame):
            return self.output
        return None

    def display_sample_record(
        self,
        index: int | None = None,
        *,
        hide_seed_columns: bool = False,
        syntax_highlighting_theme: str = "dracula",
        background_color: str | None = None,
    ) -> None:
        """Display a sample record from the Data Designer dataset preview.

        Args:
            index: Index of the record to display. If None, the next record will be displayed.
                This is useful for running the cell in a notebook multiple times.
            hide_seed_columns: If True, the columns from the seed dataset (if any) will not be displayed.
            syntax_highlighting_theme: Theme to use for syntax highlighting. See the `Syntax`
                documentation from `rich` for information about available themes.
            background_color: Background color to use for the record. See the `Syntax`
                documentation from `rich` for information about available background colors.
        """
        if self.dataset is None:
            raise ValueError("No dataset found in the preview results.")
        i = index or self._display_cycle_index
        display_sample_record(
            record=self.dataset.iloc[i],
            ndd_metadata=self.data_designer_metadata,
            background_color=background_color,
            syntax_highlighting_theme=syntax_highlighting_theme,
            hide_seed_columns=hide_seed_columns,
            record_index=i,
        )
        if index is None:
            self._display_cycle_index = (self._display_cycle_index + 1) % len(self.dataset)
