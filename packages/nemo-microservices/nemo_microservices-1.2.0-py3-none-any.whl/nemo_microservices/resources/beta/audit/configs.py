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

from typing import Dict, Union
from datetime import datetime
from typing_extensions import Literal

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....pagination import SyncDefaultPagination, AsyncDefaultPagination
from ....types.beta import AuditPluginsDataParam
from ...._base_client import AsyncPaginator, make_request_options
from ....types.beta.audit import config_create_params, config_update_params, config_list_versions_params
from ....types.shared.delete_response import DeleteResponse
from ....types.beta.audit.audit_config import AuditConfig
from ....types.shared_params.ownership import Ownership
from ....types.beta.audit_run_data_param import AuditRunDataParam
from ....types.beta.audit_report_data_param import AuditReportDataParam
from ....types.beta.audit_system_data_param import AuditSystemDataParam
from ....types.beta.audit_plugins_data_param import AuditPluginsDataParam
from ....types.beta.audit.config_list_response import ConfigListResponse

__all__ = ["ConfigsResource", "AsyncConfigsResource"]


class ConfigsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return ConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return ConfigsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        id: str | NotGiven = NOT_GIVEN,
        created_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        entity_id: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        plugins: AuditPluginsDataParam | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        reporting: AuditReportDataParam | NotGiven = NOT_GIVEN,
        run: AuditRunDataParam | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        system: AuditSystemDataParam | NotGiven = NOT_GIVEN,
        type_prefix: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditConfig:
        """Post Config

        Args:
          id: The ID of the entity.

        With the exception of namespaces, this is always a
              semantically-prefixed base58-encoded uuid4 [<prefix>-base58(uuid4())].

          created_at: Timestamp for when the entity was created.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          entity_id: The entity id. If first version, it will match version id

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          schema_version: The version of the schema for the object. Internal use only.

          type_prefix: The type prefix of the entity ID. If not specified, it will be inferred from the
              entity type name, but this will likely result in long prefixes.

          updated_at: Timestamp for when the entity was last updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1beta1/audit/configs",
            body=maybe_transform(
                {
                    "id": id,
                    "created_at": created_at,
                    "custom_fields": custom_fields,
                    "description": description,
                    "entity_id": entity_id,
                    "name": name,
                    "namespace": namespace,
                    "ownership": ownership,
                    "plugins": plugins,
                    "project": project,
                    "reporting": reporting,
                    "run": run,
                    "schema_version": schema_version,
                    "system": system,
                    "type_prefix": type_prefix,
                    "updated_at": updated_at,
                },
                config_create_params.ConfigCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditConfig,
        )

    def retrieve(
        self,
        config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditConfig:
        """
        Get Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return self._get(
            f"/v1beta1/audit/configs/{namespace}/{config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditConfig,
        )

    def update(
        self,
        config_name: str,
        *,
        namespace: str,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        plugins: AuditPluginsDataParam | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        reporting: AuditReportDataParam | NotGiven = NOT_GIVEN,
        run: AuditRunDataParam | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        system: AuditSystemDataParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditConfig:
        """
        Update Config

        Args:
          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          schema_version: The version of the schema for the object. Internal use only.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return self._patch(
            f"/v1beta1/audit/configs/{namespace}/{config_name}",
            body=maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "ownership": ownership,
                    "plugins": plugins,
                    "project": project,
                    "reporting": reporting,
                    "run": run,
                    "schema_version": schema_version,
                    "system": system,
                },
                config_update_params.ConfigUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditConfig,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConfigListResponse:
        """Get Configs"""
        return self._get(
            "/v1beta1/audit/configs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigListResponse,
        )

    def delete(
        self,
        config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        Delete Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return self._delete(
            f"/v1beta1/audit/configs/{namespace}/{config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )

    def list_versions(
        self,
        config_name: str,
        *,
        namespace: str,
        filter: config_list_versions_params.Filter | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: Literal["created_at", "-created_at"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDefaultPagination[AuditConfig]:
        """
        Get all historical versions of a config

        Args:
          filter: Filter versions on various criteria.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in descending order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return self._get_api_list(
            f"/v1beta1/audit/configs/{namespace}/{config_name}/versions",
            page=SyncDefaultPagination[AuditConfig],
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
                    config_list_versions_params.ConfigListVersionsParams,
                ),
            ),
            model=AuditConfig,
        )


class AsyncConfigsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncConfigsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        id: str | NotGiven = NOT_GIVEN,
        created_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        entity_id: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        plugins: AuditPluginsDataParam | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        reporting: AuditReportDataParam | NotGiven = NOT_GIVEN,
        run: AuditRunDataParam | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        system: AuditSystemDataParam | NotGiven = NOT_GIVEN,
        type_prefix: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditConfig:
        """Post Config

        Args:
          id: The ID of the entity.

        With the exception of namespaces, this is always a
              semantically-prefixed base58-encoded uuid4 [<prefix>-base58(uuid4())].

          created_at: Timestamp for when the entity was created.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          entity_id: The entity id. If first version, it will match version id

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          schema_version: The version of the schema for the object. Internal use only.

          type_prefix: The type prefix of the entity ID. If not specified, it will be inferred from the
              entity type name, but this will likely result in long prefixes.

          updated_at: Timestamp for when the entity was last updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1beta1/audit/configs",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "created_at": created_at,
                    "custom_fields": custom_fields,
                    "description": description,
                    "entity_id": entity_id,
                    "name": name,
                    "namespace": namespace,
                    "ownership": ownership,
                    "plugins": plugins,
                    "project": project,
                    "reporting": reporting,
                    "run": run,
                    "schema_version": schema_version,
                    "system": system,
                    "type_prefix": type_prefix,
                    "updated_at": updated_at,
                },
                config_create_params.ConfigCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditConfig,
        )

    async def retrieve(
        self,
        config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditConfig:
        """
        Get Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return await self._get(
            f"/v1beta1/audit/configs/{namespace}/{config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditConfig,
        )

    async def update(
        self,
        config_name: str,
        *,
        namespace: str,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        plugins: AuditPluginsDataParam | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        reporting: AuditReportDataParam | NotGiven = NOT_GIVEN,
        run: AuditRunDataParam | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        system: AuditSystemDataParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditConfig:
        """
        Update Config

        Args:
          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          schema_version: The version of the schema for the object. Internal use only.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return await self._patch(
            f"/v1beta1/audit/configs/{namespace}/{config_name}",
            body=await async_maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "ownership": ownership,
                    "plugins": plugins,
                    "project": project,
                    "reporting": reporting,
                    "run": run,
                    "schema_version": schema_version,
                    "system": system,
                },
                config_update_params.ConfigUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditConfig,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConfigListResponse:
        """Get Configs"""
        return await self._get(
            "/v1beta1/audit/configs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigListResponse,
        )

    async def delete(
        self,
        config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        Delete Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return await self._delete(
            f"/v1beta1/audit/configs/{namespace}/{config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )

    def list_versions(
        self,
        config_name: str,
        *,
        namespace: str,
        filter: config_list_versions_params.Filter | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: Literal["created_at", "-created_at"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[AuditConfig, AsyncDefaultPagination[AuditConfig]]:
        """
        Get all historical versions of a config

        Args:
          filter: Filter versions on various criteria.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in descending order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return self._get_api_list(
            f"/v1beta1/audit/configs/{namespace}/{config_name}/versions",
            page=AsyncDefaultPagination[AuditConfig],
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
                    config_list_versions_params.ConfigListVersionsParams,
                ),
            ),
            model=AuditConfig,
        )


class ConfigsResourceWithRawResponse:
    def __init__(self, configs: ConfigsResource) -> None:
        self._configs = configs

        self.create = to_raw_response_wrapper(
            configs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            configs.retrieve,
        )
        self.update = to_raw_response_wrapper(
            configs.update,
        )
        self.list = to_raw_response_wrapper(
            configs.list,
        )
        self.delete = to_raw_response_wrapper(
            configs.delete,
        )
        self.list_versions = to_raw_response_wrapper(
            configs.list_versions,
        )


class AsyncConfigsResourceWithRawResponse:
    def __init__(self, configs: AsyncConfigsResource) -> None:
        self._configs = configs

        self.create = async_to_raw_response_wrapper(
            configs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            configs.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            configs.update,
        )
        self.list = async_to_raw_response_wrapper(
            configs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            configs.delete,
        )
        self.list_versions = async_to_raw_response_wrapper(
            configs.list_versions,
        )


class ConfigsResourceWithStreamingResponse:
    def __init__(self, configs: ConfigsResource) -> None:
        self._configs = configs

        self.create = to_streamed_response_wrapper(
            configs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            configs.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            configs.update,
        )
        self.list = to_streamed_response_wrapper(
            configs.list,
        )
        self.delete = to_streamed_response_wrapper(
            configs.delete,
        )
        self.list_versions = to_streamed_response_wrapper(
            configs.list_versions,
        )


class AsyncConfigsResourceWithStreamingResponse:
    def __init__(self, configs: AsyncConfigsResource) -> None:
        self._configs = configs

        self.create = async_to_streamed_response_wrapper(
            configs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            configs.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            configs.update,
        )
        self.list = async_to_streamed_response_wrapper(
            configs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            configs.delete,
        )
        self.list_versions = async_to_streamed_response_wrapper(
            configs.list_versions,
        )
