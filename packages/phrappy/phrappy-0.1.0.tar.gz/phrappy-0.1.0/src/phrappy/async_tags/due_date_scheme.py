from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import DueDateSchemeListEntryDto


class DueDateSchemeOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def list_due_date_schemes(
        self,
        order: Optional[str] = "asc",
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
    ) -> DueDateSchemeListEntryDto:
        """
        Operation id: listDueDateSchemes
        List due date schemes

        :param order: Optional[str] = "asc" (optional), query. Sorting order.
        :param sort: Optional[str] = "NAME" (optional), query. Sorting field.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: DueDateSchemeListEntryDto
        """

        endpoint = "/api2/v1/dueDateSchemes"

        params = {"sort": sort, "order": order}

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

        return DueDateSchemeListEntryDto.model_validate(r.json())
