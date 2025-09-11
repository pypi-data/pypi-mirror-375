from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import BusinessUnitDto, BusinessUnitEditDto, PageDtoBusinessUnitDto


class BusinessUnitOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def create_business_unit(
        self,
        business_unit_edit_dto: Optional[BusinessUnitEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> BusinessUnitDto:
        """
        Operation id: createBusinessUnit
        Create business unit

        :param business_unit_edit_dto: Optional[BusinessUnitEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: BusinessUnitDto
        """

        endpoint = "/api2/v1/businessUnits"
        if type(business_unit_edit_dto) is dict:
            business_unit_edit_dto = BusinessUnitEditDto.model_validate(
                business_unit_edit_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = business_unit_edit_dto

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

        return BusinessUnitDto.model_validate(r.json())

    def delete_business_unit(
        self,
        business_unit_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteBusinessUnit
        Delete business unit

        :param business_unit_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/businessUnits/{business_unit_uid}"

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

    def get_business_unit(
        self,
        business_unit_uid: str,
        phrase_token: Optional[str] = None,
    ) -> BusinessUnitDto:
        """
        Operation id: getBusinessUnit
        Get business unit

        :param business_unit_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: BusinessUnitDto
        """

        endpoint = f"/api2/v1/businessUnits/{business_unit_uid}"

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

        return BusinessUnitDto.model_validate(r.json())

    def list_business_units(
        self,
        created_by: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[str] = "ASC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
    ) -> PageDtoBusinessUnitDto:
        """
        Operation id: listBusinessUnits
        List business units

        :param created_by: Optional[str] = None (optional), query. Uid of user.
        :param name: Optional[str] = None (optional), query. Unique name of the business unit.
        :param order: Optional[str] = "ASC" (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "NAME" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoBusinessUnitDto
        """

        endpoint = "/api2/v1/businessUnits"

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

        return PageDtoBusinessUnitDto.model_validate(r.json())

    def update_business_unit(
        self,
        business_unit_uid: str,
        business_unit_edit_dto: Optional[BusinessUnitEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> BusinessUnitDto:
        """
        Operation id: updateBusinessUnit
        Edit business unit

        :param business_unit_uid: str (required), path.
        :param business_unit_edit_dto: Optional[BusinessUnitEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: BusinessUnitDto
        """

        endpoint = f"/api2/v1/businessUnits/{business_unit_uid}"
        if type(business_unit_edit_dto) is dict:
            business_unit_edit_dto = BusinessUnitEditDto.model_validate(
                business_unit_edit_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = business_unit_edit_dto

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

        return BusinessUnitDto.model_validate(r.json())
