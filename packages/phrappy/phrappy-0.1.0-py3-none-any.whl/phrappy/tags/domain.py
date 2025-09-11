from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import DomainDto, DomainEditDto, PageDtoDomainDto


class DomainOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def create_domain(
        self,
        domain_edit_dto: Optional[DomainEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> DomainDto:
        """
        Operation id: createDomain
        Create domain

        :param domain_edit_dto: Optional[DomainEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: DomainDto
        """

        endpoint = "/api2/v1/domains"
        if type(domain_edit_dto) is dict:
            domain_edit_dto = DomainEditDto.model_validate(domain_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = domain_edit_dto

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return DomainDto.model_validate(r.json())

    def delete_domain(
        self,
        domain_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteDomain
        Delete domain

        :param domain_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/domains/{domain_uid}"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

    def get_domain(
        self,
        domain_uid: str,
        phrase_token: Optional[str] = None,
    ) -> DomainDto:
        """
        Operation id: getDomain
        Get domain

        :param domain_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: DomainDto
        """

        endpoint = f"/api2/v1/domains/{domain_uid}"

        params = {}

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

        return DomainDto.model_validate(r.json())

    def list_domains(
        self,
        created_by: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[str] = "ASC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
    ) -> PageDtoDomainDto:
        """
        Operation id: listDomains
        List of domains

        :param created_by: Optional[str] = None (optional), query. Uid of user.
        :param name: Optional[str] = None (optional), query.
        :param order: Optional[str] = "ASC" (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "NAME" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoDomainDto
        """

        endpoint = "/api2/v1/domains"

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

        return PageDtoDomainDto.model_validate(r.json())

    def update_domain(
        self,
        domain_uid: str,
        domain_edit_dto: Optional[DomainEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> DomainDto:
        """
        Operation id: updateDomain
        Edit domain

        :param domain_uid: str (required), path.
        :param domain_edit_dto: Optional[DomainEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: DomainDto
        """

        endpoint = f"/api2/v1/domains/{domain_uid}"
        if type(domain_edit_dto) is dict:
            domain_edit_dto = DomainEditDto.model_validate(domain_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = domain_edit_dto

        r = self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return DomainDto.model_validate(r.json())
