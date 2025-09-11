from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import LanguageListDto


class SupportedLanguagesOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def list_of_languages(
        self,
        active: Optional[bool] = None,
        phrase_token: Optional[str] = None,
    ) -> LanguageListDto:
        """
        Operation id: listOfLanguages
        List supported languages

        :param active: Optional[bool] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LanguageListDto
        """

        endpoint = "/api2/v1/languages"

        params = {"active": active}

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

        return LanguageListDto.model_validate(r.json())
