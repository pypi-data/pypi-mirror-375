from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    EmailQuotesRequestDto,
    EmailQuotesResponseDto,
    QuoteCreateV2Dto,
    QuoteDto,
    QuoteV2Dto,
)


class QuoteOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def create_quote_v2(
        self,
        quote_create_v2_dto: Optional[QuoteCreateV2Dto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> QuoteV2Dto:
        """
        Operation id: createQuoteV2
        Create quote
        Either WorkflowSettings or Units must be sent for billingUnit "Hour".
        :param quote_create_v2_dto: Optional[QuoteCreateV2Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QuoteV2Dto
        """

        endpoint = "/api2/v2/quotes"
        if type(quote_create_v2_dto) is dict:
            quote_create_v2_dto = QuoteCreateV2Dto.model_validate(quote_create_v2_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = quote_create_v2_dto

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

        return QuoteV2Dto.model_validate(r.json())

    async def delete_quote(
        self,
        quote_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteQuote
        Delete quote

        :param quote_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/quotes/{quote_uid}"

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

    async def email_quotes(
        self,
        email_quotes_request_dto: Optional[EmailQuotesRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> EmailQuotesResponseDto:
        """
        Operation id: emailQuotes
        Email quotes

        :param email_quotes_request_dto: Optional[EmailQuotesRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: EmailQuotesResponseDto
        """

        endpoint = "/api2/v1/quotes/email"
        if type(email_quotes_request_dto) is dict:
            email_quotes_request_dto = EmailQuotesRequestDto.model_validate(
                email_quotes_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = email_quotes_request_dto

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

        return EmailQuotesResponseDto.model_validate(r.json())

    async def get_3(
        self,
        quote_uid: str,
        phrase_token: Optional[str] = None,
    ) -> QuoteDto:
        """
        Operation id: get_3
        Get quote

        :param quote_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QuoteDto
        """

        endpoint = f"/api2/v1/quotes/{quote_uid}"

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

        return QuoteDto.model_validate(r.json())
