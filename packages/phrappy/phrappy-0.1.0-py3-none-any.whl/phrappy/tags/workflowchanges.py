from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import WorkflowChangesDto


class WorkflowchangesOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def download_workflow_changes(
        self,
        workflow_changes_dto: Optional[WorkflowChangesDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: downloadWorkflowChanges
        Download workflow changes report

        :param workflow_changes_dto: Optional[WorkflowChangesDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        !!! N.B.: API docs have no 200 range response declared, so falling back to returning the raw bytes from the API response.

        :return: bytes
        """

        endpoint = "/api2/v2/jobs/workflowChanges"
        if type(workflow_changes_dto) is dict:
            workflow_changes_dto = WorkflowChangesDto.model_validate(
                workflow_changes_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = workflow_changes_dto

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
