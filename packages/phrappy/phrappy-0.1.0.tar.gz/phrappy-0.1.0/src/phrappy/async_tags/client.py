from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import ClientDto, ClientEditDto, PageDtoClientDto


class ClientOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def create_client(
        self,
        client_edit_dto: ClientEditDto | dict,
        phrase_token: Optional[str] = None,
    ) -> ClientDto:
        """
        Operation id: createClient
        Create client

        :param client_edit_dto: ClientEditDto | dict (required), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ClientDto
        """

        endpoint = "/api2/v1/clients"
        if type(client_edit_dto) is dict:
            client_edit_dto = ClientEditDto.model_validate(client_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = client_edit_dto

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

        return ClientDto.model_validate(r.json())

    async def delete_client(
        self,
        client_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteClient
        Delete client

        :param client_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/clients/{client_uid}"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        await self.client.make_request(
            "DELETE",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return

    async def get_client(
        self,
        client_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ClientDto:
        """
        Operation id: getClient
        Get client

        :param client_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ClientDto
        """

        endpoint = f"/api2/v1/clients/{client_uid}"

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

        return ClientDto.model_validate(r.json())

    async def list_clients(
        self,
        created_by: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[str] = "ASC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
    ) -> PageDtoClientDto:
        """
        Operation id: listClients
        List clients

        :param created_by: Optional[str] = None (optional), query. Uid of user.
        :param name: Optional[str] = None (optional), query. Unique name of the Client.
        :param order: Optional[str] = "ASC" (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "NAME" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoClientDto
        """

        endpoint = "/api2/v1/clients"

        params = {
            "name": name,
            "createdBy": created_by,
            "sort": sort,
            "order": order,
            "pageNumber": page_number,
            "pageSize": page_size,
        }

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

        return PageDtoClientDto.model_validate(r.json())

    async def update_client(
        self,
        client_edit_dto: ClientEditDto | dict,
        client_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ClientDto:
        """
        Operation id: updateClient
        Edit client

        :param client_edit_dto: ClientEditDto | dict (required), body.
        :param client_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ClientDto
        """

        endpoint = f"/api2/v1/clients/{client_uid}"
        if type(client_edit_dto) is dict:
            client_edit_dto = ClientEditDto.model_validate(client_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = client_edit_dto

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

        return ClientDto.model_validate(r.json())
