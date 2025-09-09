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

from .configs import (
    ConfigsResource,
    AsyncConfigsResource,
    ConfigsResourceWithRawResponse,
    AsyncConfigsResourceWithRawResponse,
    ConfigsResourceWithStreamingResponse,
    AsyncConfigsResourceWithStreamingResponse,
)
from .targets import (
    TargetsResource,
    AsyncTargetsResource,
    TargetsResourceWithRawResponse,
    AsyncTargetsResourceWithRawResponse,
    TargetsResourceWithStreamingResponse,
    AsyncTargetsResourceWithStreamingResponse,
)
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
from ....pagination import SyncDefaultPagination, AsyncDefaultPagination
from ....types.beta import (
    AuditPluginSortField,
    audit_list_plugins_params,
    audit_get_plugin_info_params,
)
from ...._base_client import AsyncPaginator, make_request_options
from ....types.beta.audit_plugin import AuditPlugin
from ....types.beta.audit_plugin_sort_field import AuditPluginSortField
from ....types.beta.audit_plugin_filter_param import AuditPluginFilterParam

__all__ = ["AuditResource", "AsyncAuditResource"]


class AuditResource(SyncAPIResource):
    @cached_property
    def configs(self) -> ConfigsResource:
        return ConfigsResource(self._client)

    @cached_property
    def targets(self) -> TargetsResource:
        return TargetsResource(self._client)

    @cached_property
    def jobs(self) -> JobsResource:
        return JobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AuditResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AuditResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AuditResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AuditResourceWithStreamingResponse(self)

    def get_plugin_info(
        self,
        *,
        plugin_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Get detailed information about a specific Garak plugin.

        See
        https://reference.garak.ai/ for details

        Args:
          plugin_name: The name of the plugin to get information for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1beta1/audit/get-plugin-info",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"plugin_name": plugin_name}, audit_get_plugin_info_params.AuditGetPluginInfoParams
                ),
            ),
            cast_to=object,
        )

    def info(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Info"""
        return self._get(
            "/v1beta1/audit/info",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def list_plugins(
        self,
        *,
        filter: AuditPluginFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: AuditPluginSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDefaultPagination[AuditPlugin]:
        """Get supported Garak plugins list, filtered by type.

        See
        https://reference.garak.ai/ for details

        Args:
          filter: Filter results on various criteria.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in descending order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1beta1/audit/list-plugins",
            page=SyncDefaultPagination[AuditPlugin],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    audit_list_plugins_params.AuditListPluginsParams,
                ),
            ),
            model=AuditPlugin,
        )


class AsyncAuditResource(AsyncAPIResource):
    @cached_property
    def configs(self) -> AsyncConfigsResource:
        return AsyncConfigsResource(self._client)

    @cached_property
    def targets(self) -> AsyncTargetsResource:
        return AsyncTargetsResource(self._client)

    @cached_property
    def jobs(self) -> AsyncJobsResource:
        return AsyncJobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAuditResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncAuditResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAuditResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncAuditResourceWithStreamingResponse(self)

    async def get_plugin_info(
        self,
        *,
        plugin_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Get detailed information about a specific Garak plugin.

        See
        https://reference.garak.ai/ for details

        Args:
          plugin_name: The name of the plugin to get information for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1beta1/audit/get-plugin-info",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"plugin_name": plugin_name}, audit_get_plugin_info_params.AuditGetPluginInfoParams
                ),
            ),
            cast_to=object,
        )

    async def info(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Info"""
        return await self._get(
            "/v1beta1/audit/info",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def list_plugins(
        self,
        *,
        filter: AuditPluginFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: AuditPluginSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[AuditPlugin, AsyncDefaultPagination[AuditPlugin]]:
        """Get supported Garak plugins list, filtered by type.

        See
        https://reference.garak.ai/ for details

        Args:
          filter: Filter results on various criteria.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in descending order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1beta1/audit/list-plugins",
            page=AsyncDefaultPagination[AuditPlugin],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    audit_list_plugins_params.AuditListPluginsParams,
                ),
            ),
            model=AuditPlugin,
        )


class AuditResourceWithRawResponse:
    def __init__(self, audit: AuditResource) -> None:
        self._audit = audit

        self.get_plugin_info = to_raw_response_wrapper(
            audit.get_plugin_info,
        )
        self.info = to_raw_response_wrapper(
            audit.info,
        )
        self.list_plugins = to_raw_response_wrapper(
            audit.list_plugins,
        )

    @cached_property
    def configs(self) -> ConfigsResourceWithRawResponse:
        return ConfigsResourceWithRawResponse(self._audit.configs)

    @cached_property
    def targets(self) -> TargetsResourceWithRawResponse:
        return TargetsResourceWithRawResponse(self._audit.targets)

    @cached_property
    def jobs(self) -> JobsResourceWithRawResponse:
        return JobsResourceWithRawResponse(self._audit.jobs)


class AsyncAuditResourceWithRawResponse:
    def __init__(self, audit: AsyncAuditResource) -> None:
        self._audit = audit

        self.get_plugin_info = async_to_raw_response_wrapper(
            audit.get_plugin_info,
        )
        self.info = async_to_raw_response_wrapper(
            audit.info,
        )
        self.list_plugins = async_to_raw_response_wrapper(
            audit.list_plugins,
        )

    @cached_property
    def configs(self) -> AsyncConfigsResourceWithRawResponse:
        return AsyncConfigsResourceWithRawResponse(self._audit.configs)

    @cached_property
    def targets(self) -> AsyncTargetsResourceWithRawResponse:
        return AsyncTargetsResourceWithRawResponse(self._audit.targets)

    @cached_property
    def jobs(self) -> AsyncJobsResourceWithRawResponse:
        return AsyncJobsResourceWithRawResponse(self._audit.jobs)


class AuditResourceWithStreamingResponse:
    def __init__(self, audit: AuditResource) -> None:
        self._audit = audit

        self.get_plugin_info = to_streamed_response_wrapper(
            audit.get_plugin_info,
        )
        self.info = to_streamed_response_wrapper(
            audit.info,
        )
        self.list_plugins = to_streamed_response_wrapper(
            audit.list_plugins,
        )

    @cached_property
    def configs(self) -> ConfigsResourceWithStreamingResponse:
        return ConfigsResourceWithStreamingResponse(self._audit.configs)

    @cached_property
    def targets(self) -> TargetsResourceWithStreamingResponse:
        return TargetsResourceWithStreamingResponse(self._audit.targets)

    @cached_property
    def jobs(self) -> JobsResourceWithStreamingResponse:
        return JobsResourceWithStreamingResponse(self._audit.jobs)


class AsyncAuditResourceWithStreamingResponse:
    def __init__(self, audit: AsyncAuditResource) -> None:
        self._audit = audit

        self.get_plugin_info = async_to_streamed_response_wrapper(
            audit.get_plugin_info,
        )
        self.info = async_to_streamed_response_wrapper(
            audit.info,
        )
        self.list_plugins = async_to_streamed_response_wrapper(
            audit.list_plugins,
        )

    @cached_property
    def configs(self) -> AsyncConfigsResourceWithStreamingResponse:
        return AsyncConfigsResourceWithStreamingResponse(self._audit.configs)

    @cached_property
    def targets(self) -> AsyncTargetsResourceWithStreamingResponse:
        return AsyncTargetsResourceWithStreamingResponse(self._audit.targets)

    @cached_property
    def jobs(self) -> AsyncJobsResourceWithStreamingResponse:
        return AsyncJobsResourceWithStreamingResponse(self._audit.jobs)
