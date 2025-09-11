from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import CostCenterDto, CostCenterEditDto, PageDtoCostCenterDto


class CostCenterOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def create_cost_center(
        self,
        cost_center_edit_dto: CostCenterEditDto | dict,
        phrase_token: Optional[str] = None,
    ) -> CostCenterDto:
        """
        Operation id: createCostCenter
        Create cost center

        :param cost_center_edit_dto: CostCenterEditDto | dict (required), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CostCenterDto
        """

        endpoint = "/api2/v1/costCenters"
        if type(cost_center_edit_dto) is dict:
            cost_center_edit_dto = CostCenterEditDto.model_validate(
                cost_center_edit_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = cost_center_edit_dto

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

        return CostCenterDto.model_validate(r.json())

    async def delete_cost_center(
        self,
        cost_center_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteCostCenter
        Delete cost center

        :param cost_center_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/costCenters/{cost_center_uid}"

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

    async def get_cost_center(
        self,
        cost_center_uid: str,
        phrase_token: Optional[str] = None,
    ) -> CostCenterDto:
        """
        Operation id: getCostCenter
        Get cost center

        :param cost_center_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CostCenterDto
        """

        endpoint = f"/api2/v1/costCenters/{cost_center_uid}"

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

        return CostCenterDto.model_validate(r.json())

    async def list_cost_centers(
        self,
        created_by: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[str] = "ASC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
    ) -> PageDtoCostCenterDto:
        """
        Operation id: listCostCenters
        List of cost centers

        :param created_by: Optional[str] = None (optional), query. Uid of user.
        :param name: Optional[str] = None (optional), query.
        :param order: Optional[str] = "ASC" (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "NAME" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCostCenterDto
        """

        endpoint = "/api2/v1/costCenters"

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

        return PageDtoCostCenterDto.model_validate(r.json())

    async def update_cost_center(
        self,
        cost_center_uid: str,
        cost_center_edit_dto: Optional[CostCenterEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> CostCenterDto:
        """
        Operation id: updateCostCenter
        Edit cost center

        :param cost_center_uid: str (required), path.
        :param cost_center_edit_dto: Optional[CostCenterEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CostCenterDto
        """

        endpoint = f"/api2/v1/costCenters/{cost_center_uid}"
        if type(cost_center_edit_dto) is dict:
            cost_center_edit_dto = CostCenterEditDto.model_validate(
                cost_center_edit_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = cost_center_edit_dto

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

        return CostCenterDto.model_validate(r.json())
