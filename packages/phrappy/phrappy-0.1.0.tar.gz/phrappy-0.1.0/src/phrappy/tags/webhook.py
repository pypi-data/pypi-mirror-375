from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    CreateWebHookDto,
    PageDtoWebHookDtoV2,
    PageDtoWebhookCallDto,
    ReplayRequestDto,
    WebHookDtoV2,
    WebhookPreviewsDto,
)


class WebhookOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def create_web_hook_v2(
        self,
        create_web_hook_dto: Optional[CreateWebHookDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> WebHookDtoV2:
        """
        Operation id: createWebHookV2
        Create webhook

        :param create_web_hook_dto: Optional[CreateWebHookDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: WebHookDtoV2
        """

        endpoint = "/api2/v2/webhooks"
        if type(create_web_hook_dto) is dict:
            create_web_hook_dto = CreateWebHookDto.model_validate(create_web_hook_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_web_hook_dto

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

        return WebHookDtoV2.model_validate(r.json())

    def delete_web_hook_v2(
        self,
        web_hook_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteWebHookV2
        Delete webhook

        :param web_hook_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v2/webhooks/{web_hook_uid}"

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

    def get_web_hook_list_v2(
        self,
        created_by: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        modified_by: Optional[List[str]] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort_field: Optional[str] = None,
        sort_trend: Optional[str] = "ASC",
        status: Optional[str] = None,
        url: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoWebHookDtoV2:
        """
        Operation id: getWebHookListV2
        Lists webhooks

        :param created_by: Optional[List[str]] = None (optional), query. Filter by webhook creators UIDs.
        :param events: Optional[List[str]] = None (optional), query. Filter by webhook events, any match is included.
        :param modified_by: Optional[List[str]] = None (optional), query. Filter by webhook updaters UIDs.
        :param name: Optional[str] = None (optional), query. Filter by webhook name.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort_field: Optional[str] = None (optional), query. Sort by this field.
        :param sort_trend: Optional[str] = "ASC" (optional), query. Sort direction.
        :param status: Optional[str] = None (optional), query. Filter by enabled/disabled status.
        :param url: Optional[str] = None (optional), query. Filter by webhook URL.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoWebHookDtoV2
        """

        endpoint = "/api2/v2/webhooks"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "name": name,
            "status": status,
            "url": url,
            "events": events,
            "createdBy": created_by,
            "modifiedBy": modified_by,
            "sortField": sort_field,
            "sortTrend": sort_trend,
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

        return PageDtoWebHookDtoV2.model_validate(r.json())

    def get_web_hook_v2(
        self,
        web_hook_uid: str,
        phrase_token: Optional[str] = None,
    ) -> WebHookDtoV2:
        """
        Operation id: getWebHookV2
        Get webhook

        :param web_hook_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: WebHookDtoV2
        """

        endpoint = f"/api2/v2/webhooks/{web_hook_uid}"

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

        return WebHookDtoV2.model_validate(r.json())

    def get_webhook_calls_list(
        self,
        events: Optional[List[str]] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        parent_uid: Optional[str] = None,
        status: Optional[str] = None,
        webhook_event_uid: Optional[str] = None,
        webhook_uid: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoWebhookCallDto:
        """
        Operation id: getWebhookCallsList
        Lists webhook calls

        :param events: Optional[List[str]] = None (optional), query. List of Webhook events to filter by.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param parent_uid: Optional[str] = None (optional), query. UID of parent webhook call to filter by.
        :param status: Optional[str] = None (optional), query. Status of Webhook calls to filter by.
        :param webhook_event_uid: Optional[str] = None (optional), query. UID of Webhook event to filter by.
        :param webhook_uid: Optional[str] = None (optional), query. UID of Webhook to filter by.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoWebhookCallDto
        """

        endpoint = "/api2/v1/webhooksCalls"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "events": events,
            "status": status,
            "webhookUid": webhook_uid,
            "parentUid": parent_uid,
            "webhookEventUid": webhook_event_uid,
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

        return PageDtoWebhookCallDto.model_validate(r.json())

    def get_webhook_previews(
        self,
        events: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> WebhookPreviewsDto:
        """
        Operation id: getWebhookPreviews
        Get webhook body previews

        :param events: Optional[List[str]] = None (optional), query. Filter by webhook events.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: WebhookPreviewsDto
        """

        endpoint = "/api2/v2/webhooks/previews"

        params = {"events": events}

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

        return WebhookPreviewsDto.model_validate(r.json())

    def replay_last(
        self,
        events: Optional[List[str]] = None,
        number_of_calls: Optional[int] = 5,
        status: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: replayLast
        Replay last webhook calls
        Replays specified number of last Webhook calls from oldest to the newest one
        :param events: Optional[List[str]] = None (optional), query. List of Webhook events to filter by.
        :param number_of_calls: Optional[int] = 5 (optional), query. Number of calls to be replayed.
        :param status: Optional[str] = None (optional), query. Status of Webhook calls to filter by.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = "/api2/v1/webhooksCalls/replay/latest"

        params = {"numberOfCalls": number_of_calls, "events": events, "status": status}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

        return r.content

    def replay_webhook_calls(
        self,
        replay_request_dto: Optional[ReplayRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: replayWebhookCalls
        Replay webhook calls
        Replays given list of Webhook Calls in specified order in the request
        :param replay_request_dto: Optional[ReplayRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = "/api2/v1/webhooksCalls/replay"
        if type(replay_request_dto) is dict:
            replay_request_dto = ReplayRequestDto.model_validate(replay_request_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = replay_request_dto

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

        return r.content

    def send_test_webhook(
        self,
        event: str,
        webhook_uid: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: sendTestWebhook
        Send test webhook

        :param event: str (required), query. Event of test webhook.
        :param webhook_uid: str (required), path. UID of the webhook.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v2/webhooks/{webhook_uid}/test"

        params = {"event": event}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

        return r.content

    def update_web_hook_v2(
        self,
        web_hook_uid: str,
        create_web_hook_dto: Optional[CreateWebHookDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> WebHookDtoV2:
        """
        Operation id: updateWebHookV2
        Edit webhook

        :param web_hook_uid: str (required), path.
        :param create_web_hook_dto: Optional[CreateWebHookDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: WebHookDtoV2
        """

        endpoint = f"/api2/v2/webhooks/{web_hook_uid}"
        if type(create_web_hook_dto) is dict:
            create_web_hook_dto = CreateWebHookDto.model_validate(create_web_hook_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_web_hook_dto

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

        return WebHookDtoV2.model_validate(r.json())
