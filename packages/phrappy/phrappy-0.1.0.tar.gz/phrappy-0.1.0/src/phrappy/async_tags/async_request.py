from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import AsyncRequestDto, AsyncRequestStatusDto, PageDtoAsyncRequestDto


class AsyncRequestOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def get_async_request(
        self,
        async_request_id: int,
        phrase_token: Optional[str] = None,
    ) -> AsyncRequestDto:
        """
        Operation id: getAsyncRequest
        Get asynchronous request

        This API call will return information about the specified
        [asynchronous request](https://support.phrase.com/hc/en-us/articles/5709706916124-API-TMS-#asynchronous-apis-0-2).

        Apart from basic information about the asynchronous operation such as who created it and for what action, the response
        will contain a subset of [Get project](#operation/getProject) information.

        The response contains an `asyncResponse` field which will remain `null` until the async request has finished processing.
        If any errors occurred during processing of the request, this field will contain such errors or warnings.

        _Note_: It is important to keep track of the number of pending asynchronous requests as these are subject to [Phrase
        limits](https://support.phrase.com/hc/en-us/articles/5784117234972-Phrase-TMS-Limits#api-limits-async-requests-0-2).

        :param async_request_id: int (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestDto
        """

        endpoint = f"/api2/v1/async/{async_request_id}"

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

        return AsyncRequestDto.model_validate(r.json())

    async def get_current_limit_status(
        self,
        phrase_token: Optional[str] = None,
    ) -> AsyncRequestStatusDto:
        """
        Operation id: getCurrentLimitStatus
        Get current limits


        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestStatusDto
        """

        endpoint = "/api2/v1/async/status"

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

        return AsyncRequestStatusDto.model_validate(r.json())

    async def list_pending_requests(
        self,
        all: Optional[bool] = False,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoAsyncRequestDto:
        """
        Operation id: listPendingRequests
        List pending requests

        API call to return a list of pending asynchronous requests.

        Some operations within Phrase TMS are performed
        [asynchronously](https://support.phrase.com/hc/en-us/articles/5784117234972-Phrase-TMS-Limits#api-limits-async-requests-0-2)
        and their response only serves as an acknowledgement of receipt, not an actual completion of such request.
        Since Phrase  imposes restrictions on the number of pending asynchronous
        requests within an organization, this API call provides the means to check the number of such
        pending requests.

        When processing a large number of asynchronous operations, Phrase recommends periodically checking this list of
        pending requests in order to not receive an error code during the actual processing of the requests.

        _Note: Only actions triggered via the APIs are counted towards this limit, the same type of operation carried out via the
        UI is not taken into account. This means that even with 200 pending requests, users can still create jobs via the UI._

        :param all: Optional[bool] = False (optional), query. Pending requests for organization instead of current user. Only for ADMIN..
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAsyncRequestDto
        """

        endpoint = "/api2/v1/async"

        params = {"all": all, "pageNumber": page_number, "pageSize": page_size}

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

        return PageDtoAsyncRequestDto.model_validate(r.json())
