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
import numbers
from collections import OrderedDict
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from pydantic import BaseModel
from rich.align import Align
from rich.columns import Columns
from rich.console import Console, Group
from rich.padding import Padding
from rich.panel import Panel
from rich.pretty import Pretty
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from typing_extensions import Self

from .base import ConfigBase
from .constants import DEFAULT_HIST_NAME_COLOR, DEFAULT_HIST_VALUE_COLOR
from .params.code import CodeLang, code_lang_to_syntax_lexer
from .params.llm_gen import LLMJudgePromptTemplateType, OutputType
from .params.rubrics import JudgeRubric
from .params.samplers import SamplerType

if TYPE_CHECKING:
    from .builder import DataDesignerConfigBuilder


console = Console()


class DataDesignerMetadata(BaseModel):
    """Metadata related to the dataset created by DataDesigner.

    We pass this object around to enable streamlined helper methods like
    `display_sample_record`, `fetch_dataset`, and `download_evaluation_report`.
    """

    sampler_columns: list[str] = []
    seed_columns: list[str] = []
    llm_text_columns: list[str] = []
    llm_code_columns: list[str] = []
    llm_structured_columns: list[str] = []
    llm_judge_columns: list[str] = []
    validation_columns: list[str] = []
    expression_columns: list[str] = []
    evaluation_columns: list[str] = []
    drop_columns: list[str] = []
    person_samplers: list[str] = []
    code_langs: list[CodeLang | str] = []
    eval_type: LLMJudgePromptTemplateType | None = None

    @classmethod
    def from_config_builder(cls, builder: "DataDesignerConfigBuilder") -> Self:
        validation_columns = []

        for code_val_col in builder.code_validation_columns:
            validation_columns.extend([code_val_col.name] + list(code_val_col.side_effect_columns))

        for val_col in builder.validation_with_remote_endpoint_columns:
            validation_columns.extend([val_col.name])

        sampling_based_columns = [
            col.name for col in builder.sampler_columns if col.name not in list(builder._latent_person_columns.keys())
        ]

        # Temporary logic to funnel LLMGenColumn column names into the correct list.
        # This can be removed once we migrate magic to the new column types.
        llm_text_columns = []
        llm_code_columns = []
        llm_structured_columns = []
        for col in builder.llm_gen_columns:
            if col.output_type == OutputType.TEXT and col.name not in [c.name for c in builder.llm_text_columns]:
                llm_text_columns.append(col)
            elif col.output_type == OutputType.CODE and col.name not in [c.name for c in builder.llm_code_columns]:
                llm_code_columns.append(col)
            elif col.output_type == OutputType.STRUCTURED and col.name not in [
                c.name for c in builder.llm_structured_columns
            ]:
                llm_structured_columns.append(col)
        llm_text_columns = builder.llm_text_columns + llm_text_columns
        llm_code_columns = builder.llm_code_columns + llm_code_columns
        llm_structured_columns = builder.llm_structured_columns + llm_structured_columns

        return cls(
            sampler_columns=sampling_based_columns,
            seed_columns=[col.name for col in builder.seed_columns],
            llm_text_columns=[col.name for col in llm_text_columns],
            llm_code_columns=[col.name for col in llm_code_columns],
            llm_structured_columns=[col.name for col in llm_structured_columns],
            llm_judge_columns=[col.name for col in builder.llm_judge_columns],
            validation_columns=validation_columns,
            expression_columns=[col.name for col in builder.expression_columns],
            drop_columns=builder.drop_columns,
            person_samplers=list(builder._latent_person_columns.keys()),
            code_langs=[col.output_format for col in builder.llm_code_columns],
            eval_type=None,
        )


def create_rich_histogram_table(
    data: dict[str, int | float],
    column_names: tuple[int, int],
    title: str | None = None,
    name_color: str = DEFAULT_HIST_NAME_COLOR,
    value_color: str = DEFAULT_HIST_VALUE_COLOR,
) -> Table:
    table = Table(title=title, title_style="bold")
    table.add_column(column_names[0], justify="right", style=name_color)
    table.add_column(column_names[1], justify="left", style=value_color)

    max_count = max(data.values())

    for name, value in data.items():
        bar = "" if max_count <= 0 else "█" * int((value / max_count) * 20)
        table.add_row(str(name), f"{bar} {value:.1f}")

    return table


def display_sample_record(
    record: dict | pd.Series | pd.DataFrame,
    ndd_metadata: DataDesignerMetadata,
    background_color: str | None = None,
    syntax_highlighting_theme: str = "dracula",
    record_index: int | None = None,
    hide_seed_columns: bool = False,
):
    if isinstance(record, (dict, pd.Series)):
        record = pd.DataFrame([record]).iloc[0]
    elif isinstance(record, pd.DataFrame):
        if record.shape[0] > 1:
            raise ValueError(
                f"The record must be a single record. You provided a DataFrame with {record.shape[0]} records."
            )
        record = record.iloc[0]
    else:
        raise ValueError(
            "The record must be a single record in a dictionary, pandas Series, "
            f"or pandas DataFrame. You provided: {type(record)}."
        )

    table_kws = dict(show_lines=True, expand=True)

    render_list = []

    if not hide_seed_columns and len(ndd_metadata.seed_columns) > 0:
        table = Table(title="Seed Columns", **table_kws)
        table.add_column("Name")
        table.add_column("Value")
        for col in ndd_metadata.seed_columns:
            if col not in ndd_metadata.drop_columns:
                table.add_row(col, _convert_to_row_element(record[col]))
        render_list.append(_pad_console_element(table))

    non_code_columns = (
        ndd_metadata.sampler_columns
        + ndd_metadata.expression_columns
        + ndd_metadata.llm_text_columns
        + ndd_metadata.llm_structured_columns
    )

    if len(non_code_columns) > 0:
        table = Table(title="Generated Columns", **table_kws)
        table.add_column("Name")
        table.add_column("Value")
        for col in [c for c in non_code_columns if c not in ndd_metadata.drop_columns]:
            table.add_row(col, _convert_to_row_element(record[col]))
        render_list.append(_pad_console_element(table))

    for num, col in enumerate(ndd_metadata.llm_code_columns):
        if not ndd_metadata.code_langs:
            raise ValueError("`code_langs` must be provided when code columns are specified.")
        code_lang = ndd_metadata.code_langs[num]
        if code_lang is None:
            raise ValueError(
                "`code_lang` must be provided when code columns are specified."
                f"Valid options are: {', '.join([c.value for c in CodeLang])}"
            )
        panel = Panel(
            Syntax(
                record[col],
                lexer=code_lang_to_syntax_lexer(code_lang),
                theme=syntax_highlighting_theme,
                word_wrap=True,
                background_color=background_color,
            ),
            title=col,
            expand=True,
        )
        render_list.append(_pad_console_element(panel))

    if len(ndd_metadata.validation_columns) > 0:
        table = Table(title="Validation", **table_kws)
        row = []
        for col in [c for c in ndd_metadata.validation_columns if c not in ndd_metadata.drop_columns]:
            value = record[col]
            if isinstance(value, numbers.Number):
                table.add_column(col)
                row.append(f"{value:.2f}")
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) > 0:
                length = len(value)
                label = "" if length == 1 else f" (first of {length} messages)"
                table.add_column(f"{col}{label}")
                row.append(str(value[0]))
            else:
                table.add_column(col)
                row.append(str(value))
        table.add_row(*row)
        render_list.append(_pad_console_element(table, (1, 0, 1, 0)))

    if len(ndd_metadata.llm_judge_columns) > 0:
        for col in [c for c in ndd_metadata.llm_judge_columns if c not in ndd_metadata.drop_columns]:
            table = Table(title=f"LLM-as-a-Judge: {col}", **table_kws)
            row = []
            judge = record[col]

            for measure, results in judge.items():
                table.add_column(measure)
                row.append(f"score: {results['score']}\nreasoning: {results['reasoning']}")
            table.add_row(*row)
            render_list.append(_pad_console_element(table, (1, 0, 1, 0)))

    if record_index is not None:
        index_label = Text(f"[index: {record_index}]", justify="center")
        render_list.append(index_label)

    console.print(Group(*render_list), markup=False)


def display_sampler_table(
    sampler_params: dict[SamplerType, ConfigBase],
    title: str | None = None,
) -> None:
    table = Table(expand=True)
    table.add_column("Type")
    table.add_column("Parameter")
    table.add_column("Data Type")
    table.add_column("Required", justify="center")
    table.add_column("Constraints")

    for sampler_type, params in sampler_params.items():
        num = 0
        schema = params.model_json_schema()
        for param_name, field_info in schema["properties"].items():
            is_required = param_name in schema.get("required", [])
            table.add_row(
                sampler_type if num == 0 else "",
                param_name,
                _get_field_type(field_info),
                "✓" if is_required else "",
                _get_field_constraints(field_info, schema),
            )
            num += 1
        table.add_section()

    title = title or "AI Data Designer Samplers"

    group = Group(Rule(title, end="\n\n"), table)
    console.print(group)


def display_preview_evaluation_summary(
    eval_type: LLMJudgePromptTemplateType,
    eval_results: dict,
    hist_name_color: str = DEFAULT_HIST_NAME_COLOR,
    hist_value_color: str = DEFAULT_HIST_VALUE_COLOR,
):
    render_list = []

    dash_sep = Text("-" * 100, style="bold")
    viz_name = Text(" " * 32 + "📊 Preview Evaluation Summary 📊", style="bold")

    render_list.append(dash_sep)
    render_list.append(viz_name)
    render_list.append(dash_sep)

    metrics = {}

    results = eval_results["results"]
    if "valid_records_score" in results:
        metrics["Valid Code"] = results["valid_records_score"]["percent"] * 100
    metrics.update(
        {
            "Completely Unique": results["row_uniqueness"]["percent_unique"],
            "Semantically Unique": results["row_uniqueness"]["percent_semantically_unique"],
        }
    )

    console_columns = []
    metrics_hist = create_rich_histogram_table(
        metrics,
        (
            "Values",
            "Percent of Records",
        ),
        "Quality & Diversity" if len(metrics) == 3 else "Diversity",
        name_color=hist_name_color,
        value_color=hist_value_color,
    )
    metrics_hist = Align(metrics_hist, vertical="bottom", align="left")
    console_columns.append(metrics_hist)

    if eval_type in list(LLMJudgePromptTemplateType):
        rubric = JudgeRubric.get_rubric(eval_type)
        judge_summary = {}
        for k in rubric.keys():
            judge_summary[k.capitalize()] = results.get("llm_as_a_judge_mean_scores", {}).setdefault(f"{k}_score", 0)
        judge_hist = create_rich_histogram_table(
            judge_summary,
            column_names=("Rubric", "Mean Score (0 - 5)"),
            title="LLM-as-a-Judge",
            name_color=hist_name_color,
            value_color=hist_value_color,
        )
        judge_hist = Align(judge_hist, vertical="bottom", align="right")
        console_columns.append(judge_hist)

    console_columns = Columns(console_columns, padding=(0, 7))
    render_list.append(_pad_console_element(console_columns, (1, 0, 0, 0)))

    fields = ["average_words_per_record", "average_tokens_per_record", "total_tokens"]
    text_stats = results.get("num_words_per_record")
    if text_stats is not None:
        text_stats_table = Table(expand=True, title="Text Stats", width=100, title_style="bold")
        for field in fields:
            text_stats_table.add_column(field, justify="right")
        text_stats_table.add_row(
            *[
                (f"{text_stats[field]:.1f}" if isinstance(text_stats[field], float) else str(text_stats[field]))
                for field in fields
            ]
        )
        render_list.append(_pad_console_element(text_stats_table, (2, 0, 1, 0)))

    render_list.append(dash_sep)

    console.print(Group(*render_list), markup=False)


def _convert_to_row_element(elem):
    try:
        elem = Pretty(json.loads(elem))
    except (TypeError, json.JSONDecodeError):
        pass
    if isinstance(elem, (np.integer, np.floating, np.ndarray)):
        elem = str(elem)
    elif isinstance(elem, (list, dict)):
        elem = Pretty(elem)
    return elem


def _pad_console_element(elem, padding=(1, 0, 1, 0)):
    return Padding(elem, padding)


def _get_field_type(field: dict) -> str:
    """Extract human-readable type information from a JSON Schema field."""

    # single type
    if "type" in field:
        if field["type"] == "array":
            return " | ".join([f"{f.strip()}[]" for f in _get_field_type(field["items"]).split("|")])
        if field["type"] == "object":
            return "dict"
        return field["type"]

    # union type
    elif "anyOf" in field:
        types = []
        for f in field["anyOf"]:
            if "$ref" in f:
                types.append("enum")
            elif f.get("type") == "array":
                if "items" in f and "$ref" in f["items"]:
                    types.append("enum[]")
                else:
                    types.append(f"{f['items']['type']}[]")
            else:
                types.append(f.get("type", ""))
        return " | ".join(t for t in types if t)

    return ""


def _get_field_constraints(field: dict, schema: dict) -> str:
    """Extract human-readable constraints from a JSON Schema field."""
    constraints = []

    # numeric constraints
    if "minimum" in field:
        constraints.append(f">= {field['minimum']}")
    if "exclusiveMinimum" in field:
        constraints.append(f"> {field['exclusiveMinimum']}")
    if "maximum" in field:
        constraints.append(f"<= {field['maximum']}")
    if "exclusiveMaximum" in field:
        constraints.append(f"< {field['exclusiveMaximum']}")

    # string constraints
    if "minLength" in field:
        constraints.append(f"len > {field['minLength']}")
    if "maxLength" in field:
        constraints.append(f"len < {field['maxLength']}")

    # array constraints
    if "minItems" in field:
        constraints.append(f"len > {field['minItems']}")
    if "maxItems" in field:
        constraints.append(f"len < {field['maxItems']}")

    # enum constraints
    if "enum" in _get_field_type(field) and "$defs" in schema:
        enum_values = []
        for defs in schema["$defs"].values():
            if "enum" in defs:
                enum_values.extend(defs["enum"])
        if len(enum_values) > 0:
            enum_values = OrderedDict.fromkeys(enum_values)
            constraints.append(f"allowed: {', '.join(enum_values.keys())}")

    return ", ".join(constraints)
