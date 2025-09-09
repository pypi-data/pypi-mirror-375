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

from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, Union

from pydantic import Field

from ..base import ConfigBase


class SamplerType(str, Enum):
    BERNOULLI = "bernoulli"
    BERNOULLI_MIXTURE = "bernoulli_mixture"
    BINOMIAL = "binomial"
    CATEGORY = "category"
    DATETIME = "datetime"
    GAUSSIAN = "gaussian"
    PERSON = "person"
    POISSON = "poisson"
    SCIPY = "scipy"
    SUBCATEGORY = "subcategory"
    TIMEDELTA = "timedelta"
    UNIFORM = "uniform"
    UUID = "uuid"


class Sex(str, Enum):
    MALE = "Male"
    FEMALE = "Female"


class Unit(str, Enum):
    YEAR = "Y"
    MONTH = "M"
    DAY = "D"
    HOUR = "h"
    MINUTE = "m"
    SECOND = "s"


class BernoulliMixtureSamplerParams(ConfigBase):
    p: Annotated[
        float,
        Field(
            description="Bernoulli distribution probability of success.",
            ge=0.0,
            le=1.0,
            title="P",
        ),
    ]
    dist_name: Annotated[
        str,
        Field(
            description="Mixture distribution name. Samples will be equal to the distribution sample with probability `p`, otherwise equal to 0. Must be a valid scipy.stats distribution name.",
            title="Dist Name",
        ),
    ]
    dist_params: Annotated[
        Dict[str, Any],
        Field(
            description="Parameters of the scipy.stats distribution given in `dist_name`.",
            title="Dist Params",
        ),
    ]


class BernoulliSamplerParams(ConfigBase):
    p: Annotated[float, Field(description="Probability of success.", ge=0.0, le=1.0, title="P")]


class BinomialSamplerParams(ConfigBase):
    n: Annotated[int, Field(description="Number of trials.", title="N")]
    p: Annotated[
        float,
        Field(
            description="Probability of success on each trial.",
            ge=0.0,
            le=1.0,
            title="P",
        ),
    ]


class CategorySamplerParams(ConfigBase):
    values: Annotated[
        List[Union[str, int, float]],
        Field(
            description="List of possible categorical values that can be sampled from.",
            min_length=1,
            title="Values",
        ),
    ]
    weights: Annotated[
        Optional[List[float]],
        Field(
            description="List of unnormalized probability weights to assigned to each value, in order. Larger values will be sampled with higher probability.",
            title="Weights",
        ),
    ] = None


class DatetimeSamplerParams(ConfigBase):
    start: Annotated[
        str,
        Field(
            description="Earliest possible datetime for sampling range, inclusive.",
            title="Start",
        ),
    ]
    end: Annotated[
        str,
        Field(
            description="Latest possible datetime for sampling range, inclusive.",
            title="End",
        ),
    ]
    unit: Annotated[
        Optional[Unit],
        Field(
            description="Sampling units, e.g. the smallest possible time interval between samples.",
            title="Unit",
        ),
    ] = "D"


class GaussianSamplerParams(ConfigBase):
    mean: Annotated[float, Field(description="Mean of the Gaussian distribution", title="Mean")]
    stddev: Annotated[
        float,
        Field(
            description="Standard deviation of the Gaussian distribution",
            title="Stddev",
        ),
    ]


class PersonSamplerParams(ConfigBase):
    locale: Annotated[
        Optional[str],
        Field(
            description="Locale string, determines the language and geographic locale that a synthetic person will be sampled from. E.g, en_US, en_GB, fr_FR, ...",
            title="Locale",
        ),
    ] = "en_US"
    sex: Annotated[
        Optional[Sex],
        Field(
            description="If specified, then only synthetic people of the specified sex will be sampled.",
            title="Sex",
        ),
    ] = None
    city: Annotated[
        Optional[Union[str, List[str]]],
        Field(
            description="If specified, then only synthetic people from these cities will be sampled.",
            title="City",
        ),
    ] = None
    age_range: Annotated[
        Optional[List[int]],
        Field(
            description="If specified, then only synthetic people within this age range will be sampled.",
            max_length=2,
            min_length=2,
            title="Age Range",
        ),
    ] = [18, 114]
    state: Annotated[
        Optional[Union[str, List[str]]],
        Field(
            description="Only supported for 'en_US' locale. If specified, then only synthetic people from these states will be sampled. States must be given as two-letter abbreviations.",
            title="State",
        ),
    ] = None
    with_synthetic_personas: Annotated[
        Optional[bool],
        Field(
            description="If True, then append synthetic persona columns to each generated person.",
            title="With Synthetic Personas",
        ),
    ] = False


class PoissonSamplerParams(ConfigBase):
    mean: Annotated[
        float,
        Field(description="Mean number of events in a fixed interval.", title="Mean"),
    ]


class ScipySamplerParams(ConfigBase):
    dist_name: Annotated[str, Field(description="Name of a scipy.stats distribution.", title="Dist Name")]
    dist_params: Annotated[
        Dict[str, Any],
        Field(
            description="Parameters of the scipy.stats distribution given in `dist_name`.",
            title="Dist Params",
        ),
    ]


class SubcategorySamplerParams(ConfigBase):
    category: Annotated[
        str,
        Field(description="Name of parent category to this subcategory.", title="Category"),
    ]
    values: Annotated[
        Dict[str, List[Union[str, int, float]]],
        Field(
            description="Mapping from each value of parent category to a list of subcategory values.",
            title="Values",
        ),
    ]


class TimeDeltaSamplerParams(ConfigBase):
    dt_min: Annotated[
        int,
        Field(
            description="Minimum possible time-delta for sampling range, inclusive. Must be less than `dt_max`.",
            ge=0,
            title="Dt Min",
        ),
    ]
    dt_max: Annotated[
        int,
        Field(
            description="Maximum possible time-delta for sampling range, exclusive. Must be greater than `dt_min`.",
            gt=0,
            title="Dt Max",
        ),
    ]
    reference_column_name: Annotated[
        str,
        Field(
            description="Name of an existing datetime column to condition time-delta sampling on.",
            title="Reference Column Name",
        ),
    ]
    unit: Annotated[
        Optional[Unit],
        Field(
            description="Sampling units, e.g. the smallest possible time interval between samples.",
            title="Unit",
        ),
    ] = "D"


class UniformSamplerParams(ConfigBase):
    low: Annotated[
        float,
        Field(
            description="Lower bound of the uniform distribution, inclusive.",
            title="Low",
        ),
    ]
    high: Annotated[
        float,
        Field(
            description="Upper bound of the uniform distribution, inclusive.",
            title="High",
        ),
    ]


class UUIDSamplerParams(ConfigBase):
    prefix: Annotated[
        Optional[str],
        Field(description="String prepended to the front of the UUID.", title="Prefix"),
    ] = None
    short_form: Annotated[
        Optional[bool],
        Field(
            description="If true, all UUIDs sampled will be truncated at 8 characters.",
            title="Short Form",
        ),
    ] = False
    uppercase: Annotated[
        Optional[bool],
        Field(
            description="If true, all letters in the UUID will be capitalized.",
            title="Uppercase",
        ),
    ] = False


class ConditionalDataColumn(ConfigBase):
    name: Annotated[str, Field(title="Name")]
    type: SamplerType
    params: Annotated[
        Union[
            SubcategorySamplerParams,
            CategorySamplerParams,
            DatetimeSamplerParams,
            PersonSamplerParams,
            TimeDeltaSamplerParams,
            UUIDSamplerParams,
            BernoulliSamplerParams,
            BernoulliMixtureSamplerParams,
            BinomialSamplerParams,
            GaussianSamplerParams,
            PoissonSamplerParams,
            UniformSamplerParams,
            ScipySamplerParams,
        ],
        Field(title="Params"),
    ]
    conditional_params: Annotated[
        Optional[
            Dict[
                str,
                Union[
                    SubcategorySamplerParams,
                    CategorySamplerParams,
                    DatetimeSamplerParams,
                    PersonSamplerParams,
                    TimeDeltaSamplerParams,
                    UUIDSamplerParams,
                    BernoulliSamplerParams,
                    BernoulliMixtureSamplerParams,
                    BinomialSamplerParams,
                    GaussianSamplerParams,
                    PoissonSamplerParams,
                    UniformSamplerParams,
                    ScipySamplerParams,
                ],
            ]
        ],
        Field(title="Conditional Params"),
    ] = {}
    convert_to: Annotated[Optional[str], Field(title="Convert To")] = None
