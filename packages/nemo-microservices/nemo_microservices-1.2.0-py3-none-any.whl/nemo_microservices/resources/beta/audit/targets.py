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
from ...._base_client import AsyncPaginator, make_request_options
from ....types.beta.audit import target_create_params, target_update_params, target_list_versions_params
from ....types.beta.audit_target import AuditTarget
from ....types.shared.delete_response import DeleteResponse
from ....types.shared_params.ownership import Ownership
from ....types.beta.audit.target_list_response import TargetListResponse

__all__ = ["TargetsResource", "AsyncTargetsResource"]


class TargetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TargetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return TargetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TargetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return TargetsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        model: str,
        type: str,
        id: str | NotGiven = NOT_GIVEN,
        created_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        entity_id: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        options: object | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        type_prefix: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditTarget:
        """Post Target

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
            "/v1beta1/audit/targets",
            body=maybe_transform(
                {
                    "model": model,
                    "type": type,
                    "id": id,
                    "created_at": created_at,
                    "custom_fields": custom_fields,
                    "description": description,
                    "entity_id": entity_id,
                    "name": name,
                    "namespace": namespace,
                    "options": options,
                    "ownership": ownership,
                    "project": project,
                    "schema_version": schema_version,
                    "type_prefix": type_prefix,
                    "updated_at": updated_at,
                },
                target_create_params.TargetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditTarget,
        )

    def retrieve(
        self,
        target_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditTarget:
        """
        Get Target

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._get(
            f"/v1beta1/audit/targets/{namespace}/{target_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditTarget,
        )

    def update(
        self,
        target_name: str,
        *,
        namespace: str,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        options: object | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditTarget:
        """
        Update Target

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
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._patch(
            f"/v1beta1/audit/targets/{namespace}/{target_name}",
            body=maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "model": model,
                    "options": options,
                    "ownership": ownership,
                    "project": project,
                    "schema_version": schema_version,
                    "type": type,
                },
                target_update_params.TargetUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditTarget,
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
    ) -> TargetListResponse:
        """Get Targets"""
        return self._get(
            "/v1beta1/audit/targets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TargetListResponse,
        )

    def delete(
        self,
        target_name: str,
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
        Delete Target

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._delete(
            f"/v1beta1/audit/targets/{namespace}/{target_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )

    def list_versions(
        self,
        target_name: str,
        *,
        namespace: str,
        filter: target_list_versions_params.Filter | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: Literal["created_at", "-created_at"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDefaultPagination[AuditTarget]:
        """
        Get all historical versions of a target

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
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._get_api_list(
            f"/v1beta1/audit/targets/{namespace}/{target_name}/versions",
            page=SyncDefaultPagination[AuditTarget],
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
                    target_list_versions_params.TargetListVersionsParams,
                ),
            ),
            model=AuditTarget,
        )


class AsyncTargetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTargetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncTargetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTargetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncTargetsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        model: str,
        type: str,
        id: str | NotGiven = NOT_GIVEN,
        created_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        entity_id: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        options: object | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        type_prefix: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditTarget:
        """Post Target

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
            "/v1beta1/audit/targets",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "type": type,
                    "id": id,
                    "created_at": created_at,
                    "custom_fields": custom_fields,
                    "description": description,
                    "entity_id": entity_id,
                    "name": name,
                    "namespace": namespace,
                    "options": options,
                    "ownership": ownership,
                    "project": project,
                    "schema_version": schema_version,
                    "type_prefix": type_prefix,
                    "updated_at": updated_at,
                },
                target_create_params.TargetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditTarget,
        )

    async def retrieve(
        self,
        target_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditTarget:
        """
        Get Target

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return await self._get(
            f"/v1beta1/audit/targets/{namespace}/{target_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditTarget,
        )

    async def update(
        self,
        target_name: str,
        *,
        namespace: str,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        options: object | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuditTarget:
        """
        Update Target

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
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return await self._patch(
            f"/v1beta1/audit/targets/{namespace}/{target_name}",
            body=await async_maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "model": model,
                    "options": options,
                    "ownership": ownership,
                    "project": project,
                    "schema_version": schema_version,
                    "type": type,
                },
                target_update_params.TargetUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuditTarget,
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
    ) -> TargetListResponse:
        """Get Targets"""
        return await self._get(
            "/v1beta1/audit/targets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TargetListResponse,
        )

    async def delete(
        self,
        target_name: str,
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
        Delete Target

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return await self._delete(
            f"/v1beta1/audit/targets/{namespace}/{target_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )

    def list_versions(
        self,
        target_name: str,
        *,
        namespace: str,
        filter: target_list_versions_params.Filter | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: Literal["created_at", "-created_at"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[AuditTarget, AsyncDefaultPagination[AuditTarget]]:
        """
        Get all historical versions of a target

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
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._get_api_list(
            f"/v1beta1/audit/targets/{namespace}/{target_name}/versions",
            page=AsyncDefaultPagination[AuditTarget],
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
                    target_list_versions_params.TargetListVersionsParams,
                ),
            ),
            model=AuditTarget,
        )


class TargetsResourceWithRawResponse:
    def __init__(self, targets: TargetsResource) -> None:
        self._targets = targets

        self.create = to_raw_response_wrapper(
            targets.create,
        )
        self.retrieve = to_raw_response_wrapper(
            targets.retrieve,
        )
        self.update = to_raw_response_wrapper(
            targets.update,
        )
        self.list = to_raw_response_wrapper(
            targets.list,
        )
        self.delete = to_raw_response_wrapper(
            targets.delete,
        )
        self.list_versions = to_raw_response_wrapper(
            targets.list_versions,
        )


class AsyncTargetsResourceWithRawResponse:
    def __init__(self, targets: AsyncTargetsResource) -> None:
        self._targets = targets

        self.create = async_to_raw_response_wrapper(
            targets.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            targets.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            targets.update,
        )
        self.list = async_to_raw_response_wrapper(
            targets.list,
        )
        self.delete = async_to_raw_response_wrapper(
            targets.delete,
        )
        self.list_versions = async_to_raw_response_wrapper(
            targets.list_versions,
        )


class TargetsResourceWithStreamingResponse:
    def __init__(self, targets: TargetsResource) -> None:
        self._targets = targets

        self.create = to_streamed_response_wrapper(
            targets.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            targets.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            targets.update,
        )
        self.list = to_streamed_response_wrapper(
            targets.list,
        )
        self.delete = to_streamed_response_wrapper(
            targets.delete,
        )
        self.list_versions = to_streamed_response_wrapper(
            targets.list_versions,
        )


class AsyncTargetsResourceWithStreamingResponse:
    def __init__(self, targets: AsyncTargetsResource) -> None:
        self._targets = targets

        self.create = async_to_streamed_response_wrapper(
            targets.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            targets.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            targets.update,
        )
        self.list = async_to_streamed_response_wrapper(
            targets.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            targets.delete,
        )
        self.list_versions = async_to_streamed_response_wrapper(
            targets.list_versions,
        )
