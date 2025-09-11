from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import BuyerDto, BuyerEditDto, PageDtoBuyerDto


class BuyerOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def list_buyers(
        self,
        order: Optional[str] = "ASC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
    ) -> PageDtoBuyerDto:
        """
        Operation id: listBuyers
        List buyers

        :param order: Optional[str] = "ASC" (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "NAME" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoBuyerDto
        """

        endpoint = "/api2/v1/buyers"

        params = {
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

        return PageDtoBuyerDto.model_validate(r.json())

    async def update_buyer(
        self,
        buyer_uid: str,
        buyer_edit_dto: Optional[BuyerEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> BuyerDto:
        """
        Operation id: updateBuyer
        Edit buyer

        :param buyer_uid: str (required), path.
        :param buyer_edit_dto: Optional[BuyerEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: BuyerDto
        """

        endpoint = f"/api2/v1/buyers/{buyer_uid}"
        if type(buyer_edit_dto) is dict:
            buyer_edit_dto = BuyerEditDto.model_validate(buyer_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = buyer_edit_dto

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

        return BuyerDto.model_validate(r.json())
