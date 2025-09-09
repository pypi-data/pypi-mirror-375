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

from enum import Enum
from string import Formatter

from jinja2 import meta
from jinja2.sandbox import ImmutableSandboxedEnvironment
from pydantic import BaseModel
from rich import box
from rich.console import Console, Group
from rich.padding import Padding
from rich.panel import Panel

from .columns import (
    CodeValidationColumn,
    DataSeedColumn,
    LLMGenColumn,
    LLMJudgeColumn,
)
from .constants import RICH_CONSOLE_THEME
from .type_aliases import DataDesignerColumnT


class ViolationType(str, Enum):
    ALL_COLUMNS_DROPPED = "all_columns_dropped"
    INVALID_REFERENCE = "invalid_reference"
    F_STRING_SYNTAX = "f_string_syntax"
    CODE_COLUMN_MISSING = "code_column_missing"
    CODE_COLUMN_NOT_CODE = "code_column_not_code"
    CODE_LANG_MISMATCH = "code_lang_mismatch"
    PROMPT_WITHOUT_REFERENCES = "prompt_without_references"
    INVALID_MODEL_CONFIG = "invalid_model_config"


class ViolationLevel(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


class Violation(BaseModel):
    column: str | None = None
    type: ViolationType
    message: str
    level: ViolationLevel

    @property
    def has_column(self) -> bool:
        return self.column is not None


def validate_data_designer_config(
    columns: list[DataDesignerColumnT],
    allowed_references: list[str],
) -> list[Violation]:
    violations = []
    violations.extend(_validate_prompt_templates(columns=columns, allowed_references=allowed_references))
    violations.extend(_validate_code_validation(columns=columns))
    violations.extend(_validate_columns_not_all_dropped(columns=columns))
    return violations


def rich_print_violations(violations: list[Violation]) -> None:
    if len(violations) == 0:
        return

    console = Console(theme=RICH_CONSOLE_THEME)

    render_list = []
    render_list.append(
        Padding(
            Panel(
                f"🔎 Identified {len(violations)} validation "
                f"issue{'' if len(violations) == 1 else 's'} "
                "in your Data Designer column definitions",
                box=box.SIMPLE,
                highlight=True,
            ),
            (0, 0, 1, 0),
        )
    )

    for v in violations:
        emoji = "🛑" if v.level == ViolationLevel.ERROR else "⚠️"

        error_title = f"{emoji} {v.level.upper()} | {v.type.value.upper()}"

        render_list.append(
            Padding(
                Panel(
                    f"{error_title}\n\n{v.message}",
                    box=box.HORIZONTALS,
                    title=f"Column: {v.column}" if v.has_column else "",
                    padding=(1, 0, 1, 1),
                    highlight=True,
                ),
                (0, 0, 1, 0),
            )
        )

    console.print(Group(*render_list), markup=False)


def _get_string_formatter_references(template: str, allowed_references: list[str]) -> list[str]:
    return [
        k[1].strip()
        for k in Formatter().parse(template)
        if len(k) > 1 and k[1] is not None and k[1].strip() in allowed_references
    ]


def _validate_prompt_templates(
    columns: list[DataDesignerColumnT],
    allowed_references: list[str],
) -> list[Violation]:
    env = ImmutableSandboxedEnvironment()

    columns_with_prompts = [c for c in columns if isinstance(c, (LLMGenColumn, LLMJudgeColumn))]

    violations = []
    for column in columns_with_prompts:
        for prompt_type in ["prompt", "system_prompt"]:
            if not hasattr(column, prompt_type) or getattr(column, prompt_type) is None:
                continue

            prompt = getattr(column, prompt_type)

            # check for invalid references
            prompt_references = set()
            prompt_references.update(meta.find_undeclared_variables(env.parse(prompt)))
            invalid_references = list(set(prompt_references) - set(allowed_references))
            num_invalid = len(invalid_references)
            if num_invalid > 0:
                ref_msg = (
                    f"references {num_invalid} columns that do not exist"
                    if num_invalid > 1
                    else "references a column that does not exist"
                )
                invalid_references = ", ".join([f"'{r}'" for r in invalid_references])
                message = f"The {prompt_type} template for '{column.name}' {ref_msg}: {invalid_references}."
                violations.append(
                    Violation(
                        column=column.name,
                        type=ViolationType.INVALID_REFERENCE,
                        message=message,
                        level=ViolationLevel.ERROR,
                    )
                )

            # check for prompts without references
            if prompt_type == "prompt" and len(prompt_references) == 0:
                message = (
                    f"The {prompt_type} template for '{column.name}' does not reference any columns. "
                    "This means the same prompt will be used for every row in the dataset. To increase "
                    "the diversity of the generated data, consider adding references to other columns "
                    "in the prompt template."
                )
                violations.append(
                    Violation(
                        column=column.name,
                        type=ViolationType.PROMPT_WITHOUT_REFERENCES,
                        message=message,
                        level=ViolationLevel.WARNING,
                    )
                )

            # check for f-string syntax
            f_string_references = _get_string_formatter_references(prompt, allowed_references)
            if len(f_string_references) > 0:
                f_string_references = ", ".join([f"'{r}'" for r in f_string_references])
                message = (
                    f"The {prompt_type} template for '{column.name}' references the "
                    f"following columns using f-string syntax: {f_string_references}. "
                    "Please use jinja2 syntax to reference columns: {reference} -> {{ reference }}."
                )
                violations.append(
                    Violation(
                        column=column.name,
                        type=ViolationType.F_STRING_SYNTAX,
                        message=message,
                        level=ViolationLevel.WARNING,
                    )
                )
    return violations


def _validate_code_validation(
    columns: list[DataDesignerColumnT],
) -> list[Violation]:
    code_validation_columns = [c for c in columns if isinstance(c, CodeValidationColumn)]
    columns_by_name = {c.name: c for c in columns}

    violations = []
    for validation_column in code_validation_columns:
        # check that the target column exists
        if validation_column.target_column not in columns_by_name:
            message = f"Target code column '{validation_column.target_column}' not found in column list."
            violations.append(
                Violation(
                    column=validation_column.name,
                    type=ViolationType.CODE_COLUMN_MISSING,
                    message=message,
                    level=ViolationLevel.ERROR,
                )
            )
            continue

        # check for consistent code languages
        target_column = columns_by_name[validation_column.target_column]
        if isinstance(target_column, LLMGenColumn):
            if target_column.output_type != "code":
                message = (
                    f"Code validation column '{validation_column.name}' is set to validate "
                    f"code, but the target column was generated as {target_column.output_type}."
                )
                violations.append(
                    Violation(
                        column=validation_column.name,
                        type=ViolationType.CODE_COLUMN_NOT_CODE,
                        message=message,
                        level=ViolationLevel.WARNING,
                    )
                )
            elif target_column.output_format != validation_column.code_lang:
                message = (
                    f"Code validation column '{validation_column.name}' is set to validate "
                    f"{validation_column.code_lang}, but the target column was generated as "
                    f"{target_column.output_format}."
                )
                violations.append(
                    Violation(
                        column=validation_column.name,
                        type=ViolationType.CODE_LANG_MISMATCH,
                        message=message,
                        level=ViolationLevel.ERROR,
                    )
                )

    return violations


def _validate_columns_not_all_dropped(
    columns: list[DataDesignerColumnT],
) -> list[Violation]:
    remaining_cols = [c for c in columns if not isinstance(c, DataSeedColumn) and not c.drop]

    if len(remaining_cols) == 0:
        return [
            Violation(
                column=None,
                type=ViolationType.ALL_COLUMNS_DROPPED,
                message="All generated columns are configured to be dropped. Please mark at least one column with `drop=False`.",
                level=ViolationLevel.ERROR,
            )
        ]

    return []
