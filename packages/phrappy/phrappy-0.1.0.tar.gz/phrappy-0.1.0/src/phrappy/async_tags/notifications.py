from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import PageWithResponseTsDtoNotificationDto


class NotificationsOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def list_notifications_for_user(
        self,
        category: Optional[str] = None,
        created_after_date: Optional[str] = None,
        created_before_date: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 20,
        phrase_token: Optional[str] = None,
    ) -> PageWithResponseTsDtoNotificationDto:
        """
        Operation id: listNotificationsForUser
        List notifications

        :param category: Optional[str] = None (optional), query. Filtered by notification category.
        :param created_after_date: Optional[str] = None (optional), query. Filtered by create date time in ISO 8601 UTC format.
        :param created_before_date: Optional[str] = None (optional), query. Filtered by create date time in ISO 8601 UTC format.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 20 (optional), query. Page size, accepts values between 1 and 50, default 20.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageWithResponseTsDtoNotificationDto
        """

        endpoint = "/api2/v1/notifications"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "category": category,
            "createdBeforeDate": created_before_date,
            "createdAfterDate": created_after_date,
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

        return PageWithResponseTsDtoNotificationDto.model_validate(r.json())
