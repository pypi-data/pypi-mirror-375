from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    CreateWorkflowStepDto,
    EditWorkflowStepDto,
    PageDtoWorkflowStepDto,
    PageDtoWorkflowStepReference,
    WorkflowStepDto,
)


class WorkflowStepOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def create_wf_step(
        self,
        create_workflow_step_dto: Optional[CreateWorkflowStepDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> WorkflowStepDto:
        """
        Operation id: createWFStep
        Create workflow step

        :param create_workflow_step_dto: Optional[CreateWorkflowStepDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: WorkflowStepDto
        """

        endpoint = "/api2/v1/workflowSteps"
        if type(create_workflow_step_dto) is dict:
            create_workflow_step_dto = CreateWorkflowStepDto.model_validate(
                create_workflow_step_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_workflow_step_dto

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

        return WorkflowStepDto.model_validate(r.json())

    async def delete_wf_step(
        self,
        workflow_step_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteWFStep
        Delete workflow step

        :param workflow_step_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/workflowSteps/{workflow_step_uid}"

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

    async def edit_wf_step(
        self,
        workflow_step_uid: str,
        edit_workflow_step_dto: Optional[EditWorkflowStepDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> WorkflowStepDto:
        """
        Operation id: editWFStep
        Edit workflow step

        :param workflow_step_uid: str (required), path.
        :param edit_workflow_step_dto: Optional[EditWorkflowStepDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: WorkflowStepDto
        """

        endpoint = f"/api2/v1/workflowSteps/{workflow_step_uid}"
        if type(edit_workflow_step_dto) is dict:
            edit_workflow_step_dto = EditWorkflowStepDto.model_validate(
                edit_workflow_step_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = edit_workflow_step_dto

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

        return WorkflowStepDto.model_validate(r.json())

    async def get_wf_step(
        self,
        workflow_step_uid: str,
        phrase_token: Optional[str] = None,
    ) -> WorkflowStepDto:
        """
        Operation id: getWFStep
        Get workflow step

        :param workflow_step_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: WorkflowStepDto
        """

        endpoint = f"/api2/v1/workflowSteps/{workflow_step_uid}"

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

        return WorkflowStepDto.model_validate(r.json())

    async def list_wf_steps(
        self,
        abbr: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[str] = "ASC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "ID",
        phrase_token: Optional[str] = None,
    ) -> PageDtoWorkflowStepDto:
        """
        Operation id: listWFSteps
        List workflow steps

        :param abbr: Optional[str] = None (optional), query. Abbreviation of workflow step.
        :param name: Optional[str] = None (optional), query. Name of the workflow step.
        :param order: Optional[str] = "ASC" (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "ID" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoWorkflowStepDto
        """

        endpoint = "/api2/v1/workflowSteps"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sort": sort,
            "order": order,
            "name": name,
            "abbr": abbr,
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

        return PageDtoWorkflowStepDto.model_validate(r.json())

    async def list_workflow_steps(
        self,
        user_uid: str,
        due_in_hours: Optional[int] = None,
        filename: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        project_uid: Optional[str] = None,
        status: Optional[List[str]] = None,
        target_lang: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoWorkflowStepReference:
        """
        Operation id: listWorkflowSteps
        List assigned workflow steps

        :param user_uid: str (required), path.
        :param due_in_hours: Optional[int] = None (optional), query. -1 for jobs that are overdue.
        :param filename: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query.
        :param project_uid: Optional[str] = None (optional), query.
        :param status: Optional[List[str]] = None (optional), query.
        :param target_lang: Optional[List[str]] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoWorkflowStepReference
        """

        endpoint = f"/api2/v1/users/{user_uid}/workflowSteps"

        params = {
            "status": status,
            "projectUid": project_uid,
            "targetLang": target_lang,
            "dueInHours": due_in_hours,
            "filename": filename,
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

        return PageDtoWorkflowStepReference.model_validate(r.json())
