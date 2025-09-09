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

from typing import Dict, List, Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .output_type import OutputType
from .model_config_param import ModelConfigParam

__all__ = [
    "DataDesignerConfigParam",
    "Column",
    "ColumnSamplerColumn",
    "ColumnSamplerColumnParams",
    "ColumnSamplerColumnParamsSubcategorySamplerParams",
    "ColumnSamplerColumnParamsCategorySamplerParams",
    "ColumnSamplerColumnParamsDatetimeSamplerParams",
    "ColumnSamplerColumnParamsPersonSamplerParams",
    "ColumnSamplerColumnParamsTimeDeltaSamplerParams",
    "ColumnSamplerColumnParamsUuidSamplerParams",
    "ColumnSamplerColumnParamsBernoulliSamplerParams",
    "ColumnSamplerColumnParamsBernoulliMixtureSamplerParams",
    "ColumnSamplerColumnParamsBinomialSamplerParams",
    "ColumnSamplerColumnParamsGaussianSamplerParams",
    "ColumnSamplerColumnParamsPoissonSamplerParams",
    "ColumnSamplerColumnParamsUniformSamplerParams",
    "ColumnSamplerColumnParamsScipySamplerParams",
    "ColumnSamplerColumnConditionalParams",
    "ColumnSamplerColumnConditionalParamsSubcategorySamplerParams",
    "ColumnSamplerColumnConditionalParamsCategorySamplerParams",
    "ColumnSamplerColumnConditionalParamsDatetimeSamplerParams",
    "ColumnSamplerColumnConditionalParamsPersonSamplerParams",
    "ColumnSamplerColumnConditionalParamsTimeDeltaSamplerParams",
    "ColumnSamplerColumnConditionalParamsUuidSamplerParams",
    "ColumnSamplerColumnConditionalParamsBernoulliSamplerParams",
    "ColumnSamplerColumnConditionalParamsBernoulliMixtureSamplerParams",
    "ColumnSamplerColumnConditionalParamsBinomialSamplerParams",
    "ColumnSamplerColumnConditionalParamsGaussianSamplerParams",
    "ColumnSamplerColumnConditionalParamsPoissonSamplerParams",
    "ColumnSamplerColumnConditionalParamsUniformSamplerParams",
    "ColumnSamplerColumnConditionalParamsScipySamplerParams",
    "ColumnLlmGenColumn",
    "ColumnLlmGenColumnMultiModalContext",
    "ColumnLlmTextColumn",
    "ColumnLlmTextColumnMultiModalContext",
    "ColumnLlmCodeColumn",
    "ColumnLlmCodeColumnMultiModalContext",
    "ColumnLlmStructuredColumn",
    "ColumnLlmStructuredColumnMultiModalContext",
    "ColumnLlmJudgeColumn",
    "ColumnLlmJudgeColumnRubric",
    "ColumnCodeValidationColumn",
    "ColumnValidationWithRemoteEndpointColumn",
    "ColumnExpressionColumn",
    "Constraint",
    "ConstraintParams",
    "Evaluation",
    "PersonSamplers",
    "Seed",
]


class ColumnSamplerColumnParamsSubcategorySamplerParams(TypedDict, total=False):
    category: Required[str]
    """Name of parent category to this subcategory."""

    values: Required[Dict[str, List[Union[str, float]]]]
    """Mapping from each value of parent category to a list of subcategory values."""


class ColumnSamplerColumnParamsCategorySamplerParams(TypedDict, total=False):
    values: Required[List[Union[str, float]]]
    """List of possible categorical values that can be sampled from."""

    weights: Iterable[float]
    """List of unnormalized probability weights to assigned to each value, in order.

    Larger values will be sampled with higher probability.
    """


class ColumnSamplerColumnParamsDatetimeSamplerParams(TypedDict, total=False):
    end: Required[str]
    """Latest possible datetime for sampling range, inclusive."""

    start: Required[str]
    """Earliest possible datetime for sampling range, inclusive."""

    unit: Literal["Y", "M", "D", "h", "m", "s"]
    """Sampling units, e.g. the smallest possible time interval between samples."""


class ColumnSamplerColumnParamsPersonSamplerParams(TypedDict, total=False):
    age_range: Iterable[int]
    """If specified, then only synthetic people within this age range will be sampled."""

    city: Union[List[str], str]
    """If specified, then only synthetic people from these cities will be sampled."""

    locale: str
    """
    Locale string, determines the language and geographic locale that a synthetic
    person will be sampled from. E.g, en_US, en_GB, fr_FR, ...
    """

    sex: Literal["Male", "Female"]
    """If specified, then only synthetic people of the specified sex will be sampled."""

    state: Union[List[str], str]
    """Only supported for 'en_US' locale.

    If specified, then only synthetic people from these states will be sampled.
    States must be given as two-letter abbreviations.
    """

    with_synthetic_personas: bool
    """If True, then append synthetic persona columns to each generated person."""


class ColumnSamplerColumnParamsTimeDeltaSamplerParams(TypedDict, total=False):
    dt_max: Required[int]
    """Maximum possible time-delta for sampling range, exclusive.

    Must be greater than `dt_min`.
    """

    dt_min: Required[int]
    """Minimum possible time-delta for sampling range, inclusive.

    Must be less than `dt_max`.
    """

    reference_column_name: Required[str]
    """Name of an existing datetime column to condition time-delta sampling on."""

    unit: Literal["Y", "M", "D", "h", "m", "s"]
    """Sampling units, e.g. the smallest possible time interval between samples."""


class ColumnSamplerColumnParamsUuidSamplerParams(TypedDict, total=False):
    prefix: str
    """String prepended to the front of the UUID."""

    short_form: bool
    """If true, all UUIDs sampled will be truncated at 8 characters."""

    uppercase: bool
    """If true, all letters in the UUID will be capitalized."""


class ColumnSamplerColumnParamsBernoulliSamplerParams(TypedDict, total=False):
    p: Required[float]
    """Probability of success."""


class ColumnSamplerColumnParamsBernoulliMixtureSamplerParams(TypedDict, total=False):
    dist_name: Required[str]
    """Mixture distribution name.

    Samples will be equal to the distribution sample with probability `p`, otherwise
    equal to 0. Must be a valid scipy.stats distribution name.
    """

    dist_params: Required[object]
    """Parameters of the scipy.stats distribution given in `dist_name`."""

    p: Required[float]
    """Bernoulli distribution probability of success."""


class ColumnSamplerColumnParamsBinomialSamplerParams(TypedDict, total=False):
    n: Required[int]
    """Number of trials."""

    p: Required[float]
    """Probability of success on each trial."""


class ColumnSamplerColumnParamsGaussianSamplerParams(TypedDict, total=False):
    mean: Required[float]
    """Mean of the Gaussian distribution"""

    stddev: Required[float]
    """Standard deviation of the Gaussian distribution"""


class ColumnSamplerColumnParamsPoissonSamplerParams(TypedDict, total=False):
    mean: Required[float]
    """Mean number of events in a fixed interval."""


class ColumnSamplerColumnParamsUniformSamplerParams(TypedDict, total=False):
    high: Required[float]
    """Upper bound of the uniform distribution, inclusive."""

    low: Required[float]
    """Lower bound of the uniform distribution, inclusive."""


class ColumnSamplerColumnParamsScipySamplerParams(TypedDict, total=False):
    dist_name: Required[str]
    """Name of a scipy.stats distribution."""

    dist_params: Required[object]
    """Parameters of the scipy.stats distribution given in `dist_name`."""


ColumnSamplerColumnParams: TypeAlias = Union[
    ColumnSamplerColumnParamsSubcategorySamplerParams,
    ColumnSamplerColumnParamsCategorySamplerParams,
    ColumnSamplerColumnParamsDatetimeSamplerParams,
    ColumnSamplerColumnParamsPersonSamplerParams,
    ColumnSamplerColumnParamsTimeDeltaSamplerParams,
    ColumnSamplerColumnParamsUuidSamplerParams,
    ColumnSamplerColumnParamsBernoulliSamplerParams,
    ColumnSamplerColumnParamsBernoulliMixtureSamplerParams,
    ColumnSamplerColumnParamsBinomialSamplerParams,
    ColumnSamplerColumnParamsGaussianSamplerParams,
    ColumnSamplerColumnParamsPoissonSamplerParams,
    ColumnSamplerColumnParamsUniformSamplerParams,
    ColumnSamplerColumnParamsScipySamplerParams,
]


class ColumnSamplerColumnConditionalParamsSubcategorySamplerParams(TypedDict, total=False):
    category: Required[str]
    """Name of parent category to this subcategory."""

    values: Required[Dict[str, List[Union[str, float]]]]
    """Mapping from each value of parent category to a list of subcategory values."""


class ColumnSamplerColumnConditionalParamsCategorySamplerParams(TypedDict, total=False):
    values: Required[List[Union[str, float]]]
    """List of possible categorical values that can be sampled from."""

    weights: Iterable[float]
    """List of unnormalized probability weights to assigned to each value, in order.

    Larger values will be sampled with higher probability.
    """


class ColumnSamplerColumnConditionalParamsDatetimeSamplerParams(TypedDict, total=False):
    end: Required[str]
    """Latest possible datetime for sampling range, inclusive."""

    start: Required[str]
    """Earliest possible datetime for sampling range, inclusive."""

    unit: Literal["Y", "M", "D", "h", "m", "s"]
    """Sampling units, e.g. the smallest possible time interval between samples."""


class ColumnSamplerColumnConditionalParamsPersonSamplerParams(TypedDict, total=False):
    age_range: Iterable[int]
    """If specified, then only synthetic people within this age range will be sampled."""

    city: Union[List[str], str]
    """If specified, then only synthetic people from these cities will be sampled."""

    locale: str
    """
    Locale string, determines the language and geographic locale that a synthetic
    person will be sampled from. E.g, en_US, en_GB, fr_FR, ...
    """

    sex: Literal["Male", "Female"]
    """If specified, then only synthetic people of the specified sex will be sampled."""

    state: Union[List[str], str]
    """Only supported for 'en_US' locale.

    If specified, then only synthetic people from these states will be sampled.
    States must be given as two-letter abbreviations.
    """

    with_synthetic_personas: bool
    """If True, then append synthetic persona columns to each generated person."""


class ColumnSamplerColumnConditionalParamsTimeDeltaSamplerParams(TypedDict, total=False):
    dt_max: Required[int]
    """Maximum possible time-delta for sampling range, exclusive.

    Must be greater than `dt_min`.
    """

    dt_min: Required[int]
    """Minimum possible time-delta for sampling range, inclusive.

    Must be less than `dt_max`.
    """

    reference_column_name: Required[str]
    """Name of an existing datetime column to condition time-delta sampling on."""

    unit: Literal["Y", "M", "D", "h", "m", "s"]
    """Sampling units, e.g. the smallest possible time interval between samples."""


class ColumnSamplerColumnConditionalParamsUuidSamplerParams(TypedDict, total=False):
    prefix: str
    """String prepended to the front of the UUID."""

    short_form: bool
    """If true, all UUIDs sampled will be truncated at 8 characters."""

    uppercase: bool
    """If true, all letters in the UUID will be capitalized."""


class ColumnSamplerColumnConditionalParamsBernoulliSamplerParams(TypedDict, total=False):
    p: Required[float]
    """Probability of success."""


class ColumnSamplerColumnConditionalParamsBernoulliMixtureSamplerParams(TypedDict, total=False):
    dist_name: Required[str]
    """Mixture distribution name.

    Samples will be equal to the distribution sample with probability `p`, otherwise
    equal to 0. Must be a valid scipy.stats distribution name.
    """

    dist_params: Required[object]
    """Parameters of the scipy.stats distribution given in `dist_name`."""

    p: Required[float]
    """Bernoulli distribution probability of success."""


class ColumnSamplerColumnConditionalParamsBinomialSamplerParams(TypedDict, total=False):
    n: Required[int]
    """Number of trials."""

    p: Required[float]
    """Probability of success on each trial."""


class ColumnSamplerColumnConditionalParamsGaussianSamplerParams(TypedDict, total=False):
    mean: Required[float]
    """Mean of the Gaussian distribution"""

    stddev: Required[float]
    """Standard deviation of the Gaussian distribution"""


class ColumnSamplerColumnConditionalParamsPoissonSamplerParams(TypedDict, total=False):
    mean: Required[float]
    """Mean number of events in a fixed interval."""


class ColumnSamplerColumnConditionalParamsUniformSamplerParams(TypedDict, total=False):
    high: Required[float]
    """Upper bound of the uniform distribution, inclusive."""

    low: Required[float]
    """Lower bound of the uniform distribution, inclusive."""


class ColumnSamplerColumnConditionalParamsScipySamplerParams(TypedDict, total=False):
    dist_name: Required[str]
    """Name of a scipy.stats distribution."""

    dist_params: Required[object]
    """Parameters of the scipy.stats distribution given in `dist_name`."""


ColumnSamplerColumnConditionalParams: TypeAlias = Union[
    ColumnSamplerColumnConditionalParamsSubcategorySamplerParams,
    ColumnSamplerColumnConditionalParamsCategorySamplerParams,
    ColumnSamplerColumnConditionalParamsDatetimeSamplerParams,
    ColumnSamplerColumnConditionalParamsPersonSamplerParams,
    ColumnSamplerColumnConditionalParamsTimeDeltaSamplerParams,
    ColumnSamplerColumnConditionalParamsUuidSamplerParams,
    ColumnSamplerColumnConditionalParamsBernoulliSamplerParams,
    ColumnSamplerColumnConditionalParamsBernoulliMixtureSamplerParams,
    ColumnSamplerColumnConditionalParamsBinomialSamplerParams,
    ColumnSamplerColumnConditionalParamsGaussianSamplerParams,
    ColumnSamplerColumnConditionalParamsPoissonSamplerParams,
    ColumnSamplerColumnConditionalParamsUniformSamplerParams,
    ColumnSamplerColumnConditionalParamsScipySamplerParams,
]


class ColumnSamplerColumn(TypedDict, total=False):
    name: Required[str]

    params: Required[ColumnSamplerColumnParams]

    type: Required[
        Literal[
            "bernoulli",
            "bernoulli_mixture",
            "binomial",
            "category",
            "datetime",
            "gaussian",
            "person",
            "poisson",
            "scipy",
            "subcategory",
            "timedelta",
            "uniform",
            "uuid",
        ]
    ]

    conditional_params: Dict[str, ColumnSamplerColumnConditionalParams]

    convert_to: str

    drop: bool
    """If true, remove this column from the final dataset before evaluation."""


class ColumnLlmGenColumnMultiModalContext(TypedDict, total=False):
    column_name: Required[str]

    data_type: Required[Literal["url", "base64"]]

    image_format: Literal["png", "jpg", "jpeg", "gif", "webp"]

    modality: Literal["image"]


class ColumnLlmGenColumn(TypedDict, total=False):
    model_alias: Required[str]

    prompt: Required[str]

    drop: bool
    """If true, remove this column from the final dataset before evaluation."""

    failure_threshold: float

    multi_modal_context: Iterable[ColumnLlmGenColumnMultiModalContext]

    name: str

    output_format: Union[str, object]

    output_type: OutputType

    system_prompt: str


class ColumnLlmTextColumnMultiModalContext(TypedDict, total=False):
    column_name: Required[str]

    data_type: Required[Literal["url", "base64"]]

    image_format: Literal["png", "jpg", "jpeg", "gif", "webp"]

    modality: Literal["image"]


class ColumnLlmTextColumn(TypedDict, total=False):
    model_alias: Required[str]

    prompt: Required[str]

    drop: bool
    """If true, remove this column from the final dataset before evaluation."""

    failure_threshold: float

    multi_modal_context: Iterable[ColumnLlmTextColumnMultiModalContext]

    name: str

    output_format: Union[str, object]

    output_type: OutputType

    system_prompt: str


class ColumnLlmCodeColumnMultiModalContext(TypedDict, total=False):
    column_name: Required[str]

    data_type: Required[Literal["url", "base64"]]

    image_format: Literal["png", "jpg", "jpeg", "gif", "webp"]

    modality: Literal["image"]


class ColumnLlmCodeColumn(TypedDict, total=False):
    model_alias: Required[str]

    prompt: Required[str]

    drop: bool
    """If true, remove this column from the final dataset before evaluation."""

    failure_threshold: float

    multi_modal_context: Iterable[ColumnLlmCodeColumnMultiModalContext]

    name: str

    output_format: Union[str, object]

    output_type: OutputType

    system_prompt: str


class ColumnLlmStructuredColumnMultiModalContext(TypedDict, total=False):
    column_name: Required[str]

    data_type: Required[Literal["url", "base64"]]

    image_format: Literal["png", "jpg", "jpeg", "gif", "webp"]

    modality: Literal["image"]


class ColumnLlmStructuredColumn(TypedDict, total=False):
    model_alias: Required[str]

    prompt: Required[str]

    drop: bool
    """If true, remove this column from the final dataset before evaluation."""

    failure_threshold: float

    multi_modal_context: Iterable[ColumnLlmStructuredColumnMultiModalContext]

    name: str

    output_format: Union[str, object]

    output_type: OutputType

    system_prompt: str


class ColumnLlmJudgeColumnRubric(TypedDict, total=False):
    name: Required[str]
    """A clear, pythonic class name for this rubric."""

    scoring: Required[Dict[str, str]]
    """Dictionary specifying score: description pairs for rubric scoring."""

    description: str
    """An informative and detailed assessment guide for using this rubric."""


class ColumnLlmJudgeColumn(TypedDict, total=False):
    model_alias: Required[str]

    name: Required[str]

    prompt: Required[str]
    """
    Template for generating prompts.Use Jinja2 templates to reference dataset
    columns.
    """

    rubrics: Required[Iterable[ColumnLlmJudgeColumnRubric]]
    """
    List of rubric configurations to use for evaluation.At least one must be
    provided.
    """

    drop: bool
    """If true, remove this column from the final dataset before evaluation."""

    failure_threshold: float

    judge_random_seed: int
    """Random seed to use for selecting samples to judge.

    Same seed ensures same samples are selected each time.
    """

    num_samples_to_judge: int
    """
    Number of samples to judge.If unset or None, then defaults to judging all
    records. Default is None.
    """


class ColumnCodeValidationColumn(TypedDict, total=False):
    code_lang: Required[
        Literal[
            "go",
            "javascript",
            "java",
            "kotlin",
            "python",
            "ruby",
            "rust",
            "scala",
            "swift",
            "typescript",
            "sql:sqlite",
            "sql:tsql",
            "sql:bigquery",
            "sql:mysql",
            "sql:postgres",
            "sql:ansi",
        ]
    ]

    name: Required[str]

    target_column: Required[str]

    drop: bool
    """If true, remove this column from the final dataset before evaluation."""


class ColumnValidationWithRemoteEndpointColumn(TypedDict, total=False):
    name: Required[str]

    target_columns: Required[List[str]]

    validator: Required[str]

    batch_size: int

    drop: bool
    """If true, remove this column from the final dataset before evaluation."""

    timeout: float


class ColumnExpressionColumn(TypedDict, total=False):
    expr: Required[str]

    name: Required[str]

    drop: bool
    """If true, remove this column from the final dataset before evaluation."""

    dtype: Literal["int", "float", "str", "bool"]


Column: TypeAlias = Union[
    ColumnSamplerColumn,
    ColumnLlmGenColumn,
    ColumnLlmTextColumn,
    ColumnLlmCodeColumn,
    ColumnLlmStructuredColumn,
    ColumnLlmJudgeColumn,
    ColumnCodeValidationColumn,
    ColumnValidationWithRemoteEndpointColumn,
    ColumnExpressionColumn,
]


class ConstraintParams(TypedDict, total=False):
    operator: Required[Literal["lt", "le", "gt", "ge"]]

    rhs: Required[Union[float, str]]


class Constraint(TypedDict, total=False):
    params: Required[ConstraintParams]

    target_column: Required[str]

    type: Required[Literal["scalar_inequality", "column_inequality"]]


class Evaluation(TypedDict, total=False):
    columns_to_ignore: List[str]

    defined_categorical_columns: List[str]

    llm_judge_columns: List[str]

    model_alias: str

    validation_columns: List[str]


class PersonSamplers(TypedDict, total=False):
    age_range: Iterable[int]
    """If specified, then only synthetic people within this age range will be sampled."""

    city: Union[List[str], str]
    """If specified, then only synthetic people from these cities will be sampled."""

    locale: str
    """
    Locale string, determines the language and geographic locale that a synthetic
    person will be sampled from. E.g, en_US, en_GB, fr_FR, ...
    """

    sex: Literal["Male", "Female"]
    """If specified, then only synthetic people of the specified sex will be sampled."""

    state: Union[List[str], str]
    """Only supported for 'en_US' locale.

    If specified, then only synthetic people from these states will be sampled.
    States must be given as two-letter abbreviations.
    """

    with_synthetic_personas: bool
    """If True, then append synthetic persona columns to each generated person."""


class Seed(TypedDict, total=False):
    dataset: Required[str]

    sampling_strategy: Literal["ordered", "shuffle"]

    with_replacement: bool


class DataDesignerConfigParam(TypedDict, total=False):
    columns: Required[Iterable[Column]]

    constraints: Iterable[Constraint]

    evaluation: Evaluation

    model_configs: Iterable[ModelConfigParam]

    person_samplers: Dict[str, PersonSamplers]

    seed: Seed
