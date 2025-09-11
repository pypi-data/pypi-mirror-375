from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import DeleteServicesDto, PageDtoServiceListEntryDto


class ServiceOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def delete_services(
        self,
        delete_services_dto: Optional[DeleteServicesDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteServices
        Delete services (batch)

        :param delete_services_dto: Optional[DeleteServicesDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = "/api2/v1/services"
        if type(delete_services_dto) is dict:
            delete_services_dto = DeleteServicesDto.model_validate(delete_services_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = delete_services_dto

        self.client.make_request(
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

    def list_services(
        self,
        order: Optional[str] = "desc",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
    ) -> PageDtoServiceListEntryDto:
        """
        Operation id: listServices
        List services

        :param order: Optional[str] = "desc" (optional), query. Sorting order.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "NAME" (optional), query. Sorting field.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoServiceListEntryDto
        """

        endpoint = "/api2/v1/services"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sort": sort,
            "order": order,
        }

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return PageDtoServiceListEntryDto.model_validate(r.json())
