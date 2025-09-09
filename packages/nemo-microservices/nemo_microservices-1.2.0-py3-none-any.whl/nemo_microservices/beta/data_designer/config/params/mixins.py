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

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

from ..constants import DEFAULT_REPR_HTML_STYLE, REPR_HTML_TEMPLATE

##########################################################
# Mixins
##########################################################


class WithDropColumnMixin(BaseModel):
    """Adds a `drop` flag to indicate the column should be
    removed from the final dataset before evaluation."""

    drop: bool = Field(
        default=False,
        description="If true, remove this column from the final dataset before evaluation.",
    )


class WithDAGColumnMixin:
    @property
    def required_columns(self) -> list[str]:
        return []

    @property
    def side_effect_columns(self) -> list[str]:
        return []


class WithPrettyRepr:
    """Mixin offering stylized HTML and pretty rich console rendering of objects.

    For use in notebook displays of objects.
    """

    _repr_float_precision: int = 3

    @staticmethod
    def _get_display_value(v: Any, precision: int) -> Any:
        """Intercept values for custom redisplay.

        Args:
            v (Any): The value to display.
            precision (int): number of decimal digits to display
                for floating point values.

        Returns:
            A value to use for repr to display.
        """
        if isinstance(v, float):
            return round(v, precision)

        elif isinstance(v, Enum):
            return v.value

        elif isinstance(v, BaseModel):
            return WithPrettyRepr._get_display_value(v.model_dump(mode="json"), precision)

        elif isinstance(v, list):
            return [WithPrettyRepr._get_display_value(x, precision) for x in v]

        elif isinstance(v, set):
            return {WithPrettyRepr._get_display_value(x, precision) for x in v}

        elif isinstance(v, dict):
            return {k: WithPrettyRepr._get_display_value(x, precision) for k, x in v.items()}

        return v

    def _kv_to_string(self, k: str, v: Any) -> str:
        v_display_obj = self._get_display_value(v, self._repr_float_precision)
        if isinstance(v_display_obj, (dict, list)):
            v_display = json.dumps(v_display_obj, indent=4, ensure_ascii=False)
        else:
            v_display = f"{v_display_obj!r}"

        return f"    {k}={v_display}"

    def __repr__(self) -> str:
        """Base Repr implementation.

        Puts dict fields on new lines for legibility.
        """
        dict_repr = self.model_dump(mode="json", exclude_unset=True) if isinstance(self, BaseModel) else self.__dict__
        field_repr = ",\n".join(self._kv_to_string(k, v) for k, v in dict_repr.items() if not k.startswith("_"))
        return f"{self.__class__.__name__}(\n{field_repr}\n)"

    def _repr_html_(self) -> str:
        """Represent the Repr string of an object as HTML.

        Assumes that the representation string of the object is given as
        a "python code" object. This is then rendered using Pygments and
        a module-standard CSS theming.
        """
        repr_string = self.__repr__()
        formatter = HtmlFormatter(style=DEFAULT_REPR_HTML_STYLE, cssclass="code")
        highlighted_html = highlight(repr_string, PythonLexer(), formatter)
        css = formatter.get_style_defs(".code")
        return REPR_HTML_TEMPLATE.format(css=css, highlighted_html=highlighted_html)

    def __rich_console__(self, console, options):
        yield self.__repr__()
