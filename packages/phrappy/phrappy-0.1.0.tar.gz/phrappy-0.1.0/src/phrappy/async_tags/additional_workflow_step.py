from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    AdditionalWorkflowStepDto,
    AdditionalWorkflowStepRequestDto,
    PageDtoAdditionalWorkflowStepDto,
)


class AdditionalWorkflowStepOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def create_awf_step(
        self,
        additional_workflow_step_request_dto: Optional[
            AdditionalWorkflowStepRequestDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> AdditionalWorkflowStepDto:
        """
        Operation id: createAWFStep
        Create additional workflow step

        :param additional_workflow_step_request_dto: Optional[AdditionalWorkflowStepRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AdditionalWorkflowStepDto
        """

        endpoint = "/api2/v1/additionalWorkflowSteps"
        if type(additional_workflow_step_request_dto) is dict:
            additional_workflow_step_request_dto = (
                AdditionalWorkflowStepRequestDto.model_validate(
                    additional_workflow_step_request_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = additional_workflow_step_request_dto

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

        return AdditionalWorkflowStepDto.model_validate(r.json())

    async def delete_awf_step(
        self,
        id: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteAWFStep
        Delete additional workflow step

        :param id: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/additionalWorkflowSteps/{id}"

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

    async def list_awf_steps(
        self,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoAdditionalWorkflowStepDto:
        """
        Operation id: listAWFSteps
        List additional workflow steps

        :param name: Optional[str] = None (optional), query. Name of the additional workflow step to filter.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAdditionalWorkflowStepDto
        """

        endpoint = "/api2/v1/additionalWorkflowSteps"

        params = {"pageNumber": page_number, "pageSize": page_size, "name": name}

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

        return PageDtoAdditionalWorkflowStepDto.model_validate(r.json())
