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

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from .jobs.jobs import (
    JobsResource,
    AsyncJobsResource,
    JobsResourceWithRawResponse,
    AsyncJobsResourceWithRawResponse,
    JobsResourceWithStreamingResponse,
    AsyncJobsResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.beta import data_designer_preview_params
from ...._base_client import make_request_options
from ...._decoders.jsonl import JSONLDecoder, AsyncJSONLDecoder
from ....types.beta.data_designer_preview_response import DataDesignerPreviewResponse
from ....types.beta.data_designer.data_designer_config_param import DataDesignerConfigParam

__all__ = ["DataDesignerResource", "AsyncDataDesignerResource"]


class DataDesignerResource(SyncAPIResource):
    @cached_property
    def jobs(self) -> JobsResource:
        return JobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DataDesignerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return DataDesignerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DataDesignerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return DataDesignerResourceWithStreamingResponse(self)

    def preview(
        self,
        *,
        config: DataDesignerConfigParam,
        num_records: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> JSONLDecoder[DataDesignerPreviewResponse]:
        """
        Generate preview Data Designer

        Args:
          config: Configuration for NeMo Data Designer.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/jsonl", **(extra_headers or {})}
        return self._post(
            "/v1beta1/data-designer/preview",
            body=maybe_transform(
                {
                    "config": config,
                    "num_records": num_records,
                },
                data_designer_preview_params.DataDesignerPreviewParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JSONLDecoder[DataDesignerPreviewResponse],
            stream=True,
        )


class AsyncDataDesignerResource(AsyncAPIResource):
    @cached_property
    def jobs(self) -> AsyncJobsResource:
        return AsyncJobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDataDesignerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncDataDesignerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDataDesignerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncDataDesignerResourceWithStreamingResponse(self)

    async def preview(
        self,
        *,
        config: DataDesignerConfigParam,
        num_records: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncJSONLDecoder[DataDesignerPreviewResponse]:
        """
        Generate preview Data Designer

        Args:
          config: Configuration for NeMo Data Designer.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/jsonl", **(extra_headers or {})}
        return await self._post(
            "/v1beta1/data-designer/preview",
            body=await async_maybe_transform(
                {
                    "config": config,
                    "num_records": num_records,
                },
                data_designer_preview_params.DataDesignerPreviewParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncJSONLDecoder[DataDesignerPreviewResponse],
            stream=True,
        )


class DataDesignerResourceWithRawResponse:
    def __init__(self, data_designer: DataDesignerResource) -> None:
        self._data_designer = data_designer

        self.preview = to_raw_response_wrapper(
            data_designer.preview,
        )

    @cached_property
    def jobs(self) -> JobsResourceWithRawResponse:
        return JobsResourceWithRawResponse(self._data_designer.jobs)


class AsyncDataDesignerResourceWithRawResponse:
    def __init__(self, data_designer: AsyncDataDesignerResource) -> None:
        self._data_designer = data_designer

        self.preview = async_to_raw_response_wrapper(
            data_designer.preview,
        )

    @cached_property
    def jobs(self) -> AsyncJobsResourceWithRawResponse:
        return AsyncJobsResourceWithRawResponse(self._data_designer.jobs)


class DataDesignerResourceWithStreamingResponse:
    def __init__(self, data_designer: DataDesignerResource) -> None:
        self._data_designer = data_designer

        self.preview = to_streamed_response_wrapper(
            data_designer.preview,
        )

    @cached_property
    def jobs(self) -> JobsResourceWithStreamingResponse:
        return JobsResourceWithStreamingResponse(self._data_designer.jobs)


class AsyncDataDesignerResourceWithStreamingResponse:
    def __init__(self, data_designer: AsyncDataDesignerResource) -> None:
        self._data_designer = data_designer

        self.preview = async_to_streamed_response_wrapper(
            data_designer.preview,
        )

    @cached_property
    def jobs(self) -> AsyncJobsResourceWithStreamingResponse:
        return AsyncJobsResourceWithStreamingResponse(self._data_designer.jobs)
