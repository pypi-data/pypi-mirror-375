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

import inspect
import json
import os
import re
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any, Type

import pandas as pd
import requests
import yaml
from jinja2 import TemplateSyntaxError, meta
from jinja2.sandbox import ImmutableSandboxedEnvironment
from pydantic import BaseModel

from .constants import (
    TASK_TYPE_EMOJI_MAP,
)
from .params import samplers as sampler_module


def fetch_config_if_remote(config: Any) -> str:
    if isinstance(config, str) and config.startswith("https://"):
        config = requests.get(config).content.decode("utf-8")
    return config


def get_task_log_emoji(task_name: str) -> str:
    log_emoji = ""
    for task_type, emoji in TASK_TYPE_EMOJI_MAP.items():
        if task_name.startswith(task_type):
            log_emoji = emoji + " "
    return log_emoji


def _split_camel_case(s: str, sep: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", sep, s).lower()


def camel_to_kebab(s: str) -> str:
    return _split_camel_case(s, "-")


def camel_to_snake(s: str) -> str:
    return _split_camel_case(s, "_")


def make_date_obj_serializable(obj: dict) -> dict:
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj: Any) -> Any:
            if isinstance(obj, date):
                return obj.isoformat()
            return super().default(obj)

    return json.loads(json.dumps(obj, cls=DateTimeEncoder))


class UserJinjaTemplateSyntaxError(Exception): ...


@contextmanager
def template_error_handler():
    try:
        yield
    except TemplateSyntaxError as exception:
        exception_string = (
            f"Encountered a syntax error in the provided Jinja2 template:\n{str(exception)}\n"
            "For more information on writing Jinja2 templates, refer to https://jinja.palletsprojects.com/en/stable/templates"
        )
        raise UserJinjaTemplateSyntaxError(exception_string)
    except Exception:
        raise


def assert_valid_jinja2_template(template: str) -> None:
    """Raises an error if the template cannot be parsed."""
    with template_error_handler():
        meta.find_undeclared_variables(ImmutableSandboxedEnvironment().parse(template))


def get_prompt_template_keywords(template: str) -> set[str]:
    """Extract all keywords from a valid string template."""
    with template_error_handler():
        ast = ImmutableSandboxedEnvironment().parse(template)
        keywords = set(meta.find_undeclared_variables(ast))

    return keywords


def get_sampler_params() -> dict[str, Type[BaseModel]]:
    """Returns a dictionary of sampler parameter classes."""
    params_cls_list = [
        params_cls
        for cls_name, params_cls in inspect.getmembers(sampler_module, inspect.isclass)
        if cls_name.endswith("SamplerParams")
    ]

    params_cls_dict = {}

    for source in sampler_module.SamplerType:
        source_name = source.value.replace("_", "")
        # Iterate in reverse order so the shortest match is first.
        # This is necessary for params that start with the same name.
        # For example, "bernoulli" and "bernoulli_mixture".
        params_cls_dict[source.value] = [
            params_cls
            for params_cls in reversed(params_cls_list)
            # Match param type string with parameter class.
            # For example, "gaussian" -> "GaussianSamplerParams"
            if source_name == params_cls.__name__.lower()[: len(source_name)]
            # Take the first match.
        ][0]

    return params_cls_dict


def smart_load_dataframe(dataframe: str | Path | pd.DataFrame) -> pd.DataFrame:
    """Load a dataframe from file if a path is given, otherwise return the dataframe.

    Args:
        dataframe: A path to a file or a pandas DataFrame object.

    Returns:
        A pandas DataFrame object.
    """
    if isinstance(dataframe, pd.DataFrame):
        return dataframe

    # Get the file extension.
    if isinstance(dataframe, str) and dataframe.startswith("http"):
        ext = dataframe.split(".")[-1].lower()
    else:
        dataframe = Path(dataframe)
        ext = dataframe.suffix.lower()
        if not dataframe.exists():
            raise FileNotFoundError(f"File not found: {dataframe}")

    # Load the dataframe based on the file extension.
    if ext == "csv":
        return pd.read_csv(dataframe)
    elif ext == "json":
        return pd.read_json(dataframe, lines=True)
    elif ext == "parquet":
        return pd.read_parquet(dataframe)
    else:
        raise ValueError(f"Unsupported file format: {dataframe}")


def smart_load_yaml(yaml_in: str | Path | dict) -> dict:
    """Return the yaml config as a dict given flexible input types.

    Args:
        config: The config as a dict, yaml string, or yaml file path.

    Returns:
        The config as a dict.
    """
    if isinstance(yaml_in, dict):
        yaml_out = yaml_in
    elif isinstance(yaml_in, Path) or (isinstance(yaml_in, str) and os.path.isfile(yaml_in)):
        with open(yaml_in) as file:
            yaml_out = yaml.safe_load(file)
    elif isinstance(yaml_in, str):
        yaml_out = yaml.safe_load(yaml_in)
    else:
        raise ValueError(
            f"'{yaml_in}' is an invalid yaml config format. Valid options are: dict, yaml string, or yaml file path."
        )

    if not isinstance(yaml_out, dict):
        raise ValueError(f"Loaded yaml must be a dict. Got {yaml_out}, which is of type {type(yaml_out)}.")

    return yaml_out
