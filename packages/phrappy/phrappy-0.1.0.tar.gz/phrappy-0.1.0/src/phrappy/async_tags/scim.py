from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import json

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    ScimResourceSchema,
    ScimResourceTypeSchema,
    ScimUserCoreDto,
    ServiceProviderConfigDto,
)


class SCIMOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def create_user_scim(
        self,
        authorization: Optional[str] = None,
        scim_user_core_dto: Optional[ScimUserCoreDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ScimUserCoreDto:
        """
        Operation id: createUserSCIM
        Create user using SCIM

        Supported schema: `"urn:ietf:params:scim:schemas:core:2.0:User"`

        Create active user:
        ```
        {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User"
            ],
            "active": true,
            "userName": "john.doe",
            "emails": [
                {
                    "primary": true,
                    "value": "john.doe@example.com",
                    "type": "work"
                }
            ],
            "name": {
                "givenName": "John",
                "familyName": "Doe"
            }
        }
        ```

        :param authorization: Optional[str] = None (optional), header.
        :param scim_user_core_dto: Optional[ScimUserCoreDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimUserCoreDto
        """

        endpoint = "/api2/v1/scim/Users"
        if type(scim_user_core_dto) is dict:
            scim_user_core_dto = ScimUserCoreDto.model_validate(scim_user_core_dto)

        params = {}

        headers = {
            "Authorization": (
                authorization.model_dump_json()
                if hasattr(authorization, "model_dump_json")
                else (
                    json.dumps(authorization)
                    if False and not isinstance(authorization, str)
                    else str(authorization)
                )
            )
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = scim_user_core_dto

        r = await self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return ScimUserCoreDto.model_validate(r.json())

    async def delete_user_scim(
        self,
        user_id: int,
        authorization: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: deleteUserScim
        Delete user using SCIM

        :param user_id: int (required), path.
        :param authorization: Optional[str] = None (optional), header.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/scim/Users/{user_id}"

        params = {}

        headers = {
            "Authorization": (
                authorization.model_dump_json()
                if hasattr(authorization, "model_dump_json")
                else (
                    json.dumps(authorization)
                    if False and not isinstance(authorization, str)
                    else str(authorization)
                )
            )
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = await self.client.make_request(
            "DELETE",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return await r.aread()

    async def edit_user(
        self,
        user_id: int,
        authorization: Optional[str] = None,
        scim_user_core_dto: Optional[ScimUserCoreDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ScimUserCoreDto:
        """
        Operation id: editUser
        Edit user using SCIM

        :param user_id: int (required), path.
        :param authorization: Optional[str] = None (optional), header.
        :param scim_user_core_dto: Optional[ScimUserCoreDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimUserCoreDto
        """

        endpoint = f"/api2/v1/scim/Users/{user_id}"
        if type(scim_user_core_dto) is dict:
            scim_user_core_dto = ScimUserCoreDto.model_validate(scim_user_core_dto)

        params = {}

        headers = {
            "Authorization": (
                authorization.model_dump_json()
                if hasattr(authorization, "model_dump_json")
                else (
                    json.dumps(authorization)
                    if False and not isinstance(authorization, str)
                    else str(authorization)
                )
            )
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = scim_user_core_dto

        r = await self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return ScimUserCoreDto.model_validate(r.json())

    async def get_resource_types(
        self,
        phrase_token: Optional[str] = None,
    ) -> ScimResourceTypeSchema:
        """
        Operation id: getResourceTypes
        List the types of SCIM Resources available


        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimResourceTypeSchema
        """

        endpoint = "/api2/v1/scim/ResourceTypes"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return ScimResourceTypeSchema.model_validate(r.json())

    async def get_schema_by_urn(
        self,
        schema_urn: str,
        phrase_token: Optional[str] = None,
    ) -> ScimResourceSchema:
        """
        Operation id: getSchemaByUrn
        Get supported SCIM Schema by urn

        :param schema_urn: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimResourceSchema
        """

        endpoint = f"/api2/v1/scim/Schemas/{schema_urn}"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return ScimResourceSchema.model_validate(r.json())

    async def get_schemas(
        self,
        phrase_token: Optional[str] = None,
    ) -> ScimResourceSchema:
        """
        Operation id: getSchemas
        Get supported SCIM Schemas


        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimResourceSchema
        """

        endpoint = "/api2/v1/scim/Schemas"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return ScimResourceSchema.model_validate(r.json())

    async def get_scim_user(
        self,
        user_id: int,
        authorization: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> ScimUserCoreDto:
        """
        Operation id: getScimUser
        Get user

        :param user_id: int (required), path.
        :param authorization: Optional[str] = None (optional), header.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimUserCoreDto
        """

        endpoint = f"/api2/v1/scim/Users/{user_id}"

        params = {}

        headers = {
            "Authorization": (
                authorization.model_dump_json()
                if hasattr(authorization, "model_dump_json")
                else (
                    json.dumps(authorization)
                    if False and not isinstance(authorization, str)
                    else str(authorization)
                )
            )
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return ScimUserCoreDto.model_validate(r.json())

    async def get_service_provider_config_dto(
        self,
        phrase_token: Optional[str] = None,
    ) -> ServiceProviderConfigDto:
        """
        Operation id: getServiceProviderConfigDto
        Retrieve the Service Provider's Configuration


        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ServiceProviderConfigDto
        """

        endpoint = "/api2/v1/scim/ServiceProviderConfig"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return ServiceProviderConfigDto.model_validate(r.json())

    async def patch_user(
        self,
        user_id: int,
        authorization: Optional[str] = None,
        dict: Optional[dict | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ScimUserCoreDto:
        """
        Operation id: patchUser
        Patch user using SCIM

        :param user_id: int (required), path.
        :param authorization: Optional[str] = None (optional), header.
        :param dict: Optional[dict | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimUserCoreDto
        """

        endpoint = f"/api2/v1/scim/Users/{user_id}"
        if type(dict) is dict:
            dict = dict.model_validate(dict)

        params = {}

        headers = {
            "Authorization": (
                authorization.model_dump_json()
                if hasattr(authorization, "model_dump_json")
                else (
                    json.dumps(authorization)
                    if False and not isinstance(authorization, str)
                    else str(authorization)
                )
            )
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = dict

        r = await self.client.make_request(
            "PATCH",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return ScimUserCoreDto.model_validate(r.json())

    async def search_users(
        self,
        authorization: Optional[str] = None,
        attributes: Optional[str] = None,
        count: Optional[int] = 50,
        filter: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "ascending",
        start_index: Optional[int] = 1,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: searchUsers
        Search users

        This operation supports <a href="http://ldapwiki.com/wiki/SCIM%20Filtering" target="_blank">SCIM Filter</a>,
        <a href="http://ldapwiki.com/wiki/SCIM%20Search%20Request" target="_blank">SCIM attributes</a> and
        <a href="http://ldapwiki.com/wiki/SCIM%20Sorting" target="_blank">SCIM sort</a>

        Supported attributes:
          - `id`
          - `active`
          - `userName`
          - `name.givenName`
          - `name.familyName`
          - `emails.value`
          - `meta.created`

        :param authorization: Optional[str] = None (optional), header.
        :param attributes: Optional[str] = None (optional), query. See method description.
        :param count: Optional[int] = 50 (optional), query. Non-negative Integer. Specifies the desired maximum number of search results per page; e.g., 10..
        :param filter: Optional[str] = None (optional), query. See method description.
        :param sort_by: Optional[str] = None (optional), query. See method description.
        :param sort_order: Optional[str] = "ascending" (optional), query. See method description.
        :param start_index: Optional[int] = 1 (optional), query. The 1-based index of the first search result. Default 1.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        !!! N.B.: API docs have no 200 range response declared, so falling back to returning the raw bytes from the API response.

        :return: bytes
        """

        endpoint = "/api2/v1/scim/Users"

        params = {
            "filter": filter,
            "attributes": attributes,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "startIndex": start_index,
            "count": count,
        }

        headers = {
            "Authorization": (
                authorization.model_dump_json()
                if hasattr(authorization, "model_dump_json")
                else (
                    json.dumps(authorization)
                    if False and not isinstance(authorization, str)
                    else str(authorization)
                )
            )
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return await r.aread()
