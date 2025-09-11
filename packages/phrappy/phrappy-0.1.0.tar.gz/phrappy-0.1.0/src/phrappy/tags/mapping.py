from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import TaskMappingDto


class MappingOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def get_mapping_for_task(
        self,
        id: str,
        workflow_level: Optional[int] = 1,
        phrase_token: Optional[str] = None,
    ) -> TaskMappingDto:
        """
        Operation id: getMappingForTask
        Returns mapping for taskId (mxliff)

        :param id: str (required), path.
        :param workflow_level: Optional[int] = 1 (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TaskMappingDto
        """

        endpoint = f"/api2/v1/mappings/tasks/{id}"

        params = {"workflowLevel": workflow_level}

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

        return TaskMappingDto.model_validate(r.json())
