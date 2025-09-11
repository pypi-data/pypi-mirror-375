from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import PageDtoSubDomainDto, SubDomainDto, SubDomainEditDto


class SubDomainOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def create_sub_domain(
        self,
        sub_domain_edit_dto: Optional[SubDomainEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SubDomainDto:
        """
        Operation id: createSubDomain
        Create subdomain

        :param sub_domain_edit_dto: Optional[SubDomainEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SubDomainDto
        """

        endpoint = "/api2/v1/subDomains"
        if type(sub_domain_edit_dto) is dict:
            sub_domain_edit_dto = SubDomainEditDto.model_validate(sub_domain_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = sub_domain_edit_dto

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

        return SubDomainDto.model_validate(r.json())

    def delete_sub_domain(
        self,
        sub_domain_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteSubDomain
        Delete subdomain

        :param sub_domain_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/subDomains/{sub_domain_uid}"

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

    def get_sub_domain(
        self,
        sub_domain_uid: str,
        phrase_token: Optional[str] = None,
    ) -> SubDomainDto:
        """
        Operation id: getSubDomain
        Get subdomain

        :param sub_domain_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SubDomainDto
        """

        endpoint = f"/api2/v1/subDomains/{sub_domain_uid}"

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

        return SubDomainDto.model_validate(r.json())

    def list_sub_domains(
        self,
        created_by: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[str] = "ASC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
    ) -> PageDtoSubDomainDto:
        """
        Operation id: listSubDomains
        List subdomains

        :param created_by: Optional[str] = None (optional), query. Uid of user.
        :param name: Optional[str] = None (optional), query.
        :param order: Optional[str] = "ASC" (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "NAME" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoSubDomainDto
        """

        endpoint = "/api2/v1/subDomains"

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

        return PageDtoSubDomainDto.model_validate(r.json())

    def update_sub_domain(
        self,
        sub_domain_uid: str,
        sub_domain_edit_dto: Optional[SubDomainEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SubDomainDto:
        """
        Operation id: updateSubDomain
        Edit subdomain

        :param sub_domain_uid: str (required), path.
        :param sub_domain_edit_dto: Optional[SubDomainEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SubDomainDto
        """

        endpoint = f"/api2/v1/subDomains/{sub_domain_uid}"
        if type(sub_domain_edit_dto) is dict:
            sub_domain_edit_dto = SubDomainEditDto.model_validate(sub_domain_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = sub_domain_edit_dto

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

        return SubDomainDto.model_validate(r.json())
