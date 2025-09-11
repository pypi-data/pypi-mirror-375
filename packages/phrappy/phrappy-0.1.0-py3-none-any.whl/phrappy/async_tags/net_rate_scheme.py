from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    DiscountSchemeCreateDto,
    NetRateScheme,
    NetRateSchemeEdit,
    NetRateSchemeWorkflowStep,
    NetRateSchemeWorkflowStepEdit,
    PageDtoNetRateSchemeReference,
    PageDtoNetRateSchemeWorkflowStepReference,
)


class NetRateSchemeOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def clone_discount_scheme(
        self,
        net_rate_scheme_uid: str,
        phrase_token: Optional[str] = None,
    ) -> NetRateScheme:
        """
        Operation id: cloneDiscountScheme
        Clone net rate scheme

        :param net_rate_scheme_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateScheme
        """

        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}/clone"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

        return NetRateScheme.model_validate(r.json())

    async def create_discount_scheme(
        self,
        discount_scheme_create_dto: Optional[DiscountSchemeCreateDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> NetRateScheme:
        """
        Operation id: createDiscountScheme
        Create net rate scheme

        :param discount_scheme_create_dto: Optional[DiscountSchemeCreateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateScheme
        """

        endpoint = "/api2/v1/netRateSchemes"
        if type(discount_scheme_create_dto) is dict:
            discount_scheme_create_dto = DiscountSchemeCreateDto.model_validate(
                discount_scheme_create_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = discount_scheme_create_dto

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

        return NetRateScheme.model_validate(r.json())

    async def delete_discount_scheme(
        self,
        net_rate_scheme_uid: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: deleteDiscountScheme
        Delete net rate scheme

        :param net_rate_scheme_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        !!! N.B.: API docs have no 200 range response declared, so falling back to returning the raw bytes from the API response.

        :return: bytes
        """

        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = await self.client.make_request(
            "DELETE",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return await r.aread()

    async def edit_discount_scheme_workflow_step(
        self,
        net_rate_scheme_uid: str,
        net_rate_scheme_workflow_step_id: int,
        net_rate_scheme_workflow_step_edit: Optional[
            NetRateSchemeWorkflowStepEdit | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> NetRateSchemeWorkflowStep:
        """
        Operation id: editDiscountSchemeWorkflowStep
        Edit scheme for workflow step

        :param net_rate_scheme_uid: str (required), path.
        :param net_rate_scheme_workflow_step_id: int (required), path.
        :param net_rate_scheme_workflow_step_edit: Optional[NetRateSchemeWorkflowStepEdit | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateSchemeWorkflowStep
        """

        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}/workflowStepNetSchemes/{net_rate_scheme_workflow_step_id}"
        if type(net_rate_scheme_workflow_step_edit) is dict:
            net_rate_scheme_workflow_step_edit = (
                NetRateSchemeWorkflowStepEdit.model_validate(
                    net_rate_scheme_workflow_step_edit
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = net_rate_scheme_workflow_step_edit

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

        return NetRateSchemeWorkflowStep.model_validate(r.json())

    async def get_discount_scheme(
        self,
        net_rate_scheme_uid: str,
        phrase_token: Optional[str] = None,
    ) -> NetRateScheme:
        """
        Operation id: getDiscountScheme
        Get net rate scheme

        :param net_rate_scheme_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateScheme
        """

        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}"

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

        return NetRateScheme.model_validate(r.json())

    async def get_discount_scheme_workflow_step(
        self,
        net_rate_scheme_uid: str,
        net_rate_scheme_workflow_step_id: int,
        phrase_token: Optional[str] = None,
    ) -> NetRateSchemeWorkflowStep:
        """
        Operation id: getDiscountSchemeWorkflowStep
        Get scheme for workflow step

        :param net_rate_scheme_uid: str (required), path.
        :param net_rate_scheme_workflow_step_id: int (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateSchemeWorkflowStep
        """

        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}/workflowStepNetSchemes/{net_rate_scheme_workflow_step_id}"

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

        return NetRateSchemeWorkflowStep.model_validate(r.json())

    async def get_discount_scheme_workflow_steps(
        self,
        net_rate_scheme_uid: str,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoNetRateSchemeWorkflowStepReference:
        """
        Operation id: getDiscountSchemeWorkflowSteps
        List schemes for workflow step

        :param net_rate_scheme_uid: str (required), path.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoNetRateSchemeWorkflowStepReference
        """

        endpoint = (
            f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}/workflowStepNetSchemes"
        )

        params = {"pageNumber": page_number, "pageSize": page_size}

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

        return PageDtoNetRateSchemeWorkflowStepReference.model_validate(r.json())

    async def get_discount_schemes(
        self,
        created_in_last_hours: Optional[int] = None,
        is_default: Optional[bool] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoNetRateSchemeReference:
        """
        Operation id: getDiscountSchemes
        List net rate schemes

        :param created_in_last_hours: Optional[int] = None (optional), query. Filter for those created within given hours.
        :param is_default: Optional[bool] = None (optional), query. Filter for default attribute.
        :param name: Optional[str] = None (optional), query. Filter by name.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoNetRateSchemeReference
        """

        endpoint = "/api2/v1/netRateSchemes"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "name": name,
            "isDefault": is_default,
            "createdInLastHours": created_in_last_hours,
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

        return PageDtoNetRateSchemeReference.model_validate(r.json())

    async def update_discount_scheme(
        self,
        net_rate_scheme_uid: str,
        net_rate_scheme_edit: Optional[NetRateSchemeEdit | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> NetRateScheme:
        """
        Operation id: updateDiscountScheme
        Edit net rate scheme

        :param net_rate_scheme_uid: str (required), path.
        :param net_rate_scheme_edit: Optional[NetRateSchemeEdit | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateScheme
        """

        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}"
        if type(net_rate_scheme_edit) is dict:
            net_rate_scheme_edit = NetRateSchemeEdit.model_validate(
                net_rate_scheme_edit
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = net_rate_scheme_edit

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

        return NetRateScheme.model_validate(r.json())
