from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import PageDtoXmlAssistantProfileListDto


class XMLAssistantOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def list_xml_assistant_profiles(
        self,
        created_at: Optional[str] = None,
        created_by: Optional[str] = None,
        description: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        search: Optional[str] = None,
        sort: Optional[str] = None,
        updated_at: Optional[str] = None,
        updated_by: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoXmlAssistantProfileListDto:
        """
        Operation id: listXmlAssistantProfiles
        Get XML assistant profiles for organization

        :param created_at: Optional[str] = None (optional), query.
        :param created_by: Optional[str] = None (optional), query.
        :param description: Optional[str] = None (optional), query.
        :param name: Optional[str] = None (optional), query.
        :param order: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query.
        :param search: Optional[str] = None (optional), query.
        :param sort: Optional[str] = None (optional), query.
        :param updated_at: Optional[str] = None (optional), query.
        :param updated_by: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoXmlAssistantProfileListDto
        """

        endpoint = "/api2/v1/xmlAssistantProfiles"

        params = {
            "name": name,
            "description": description,
            "createdBy": created_by,
            "updatedBy": updated_by,
            "createdAt": created_at,
            "updatedAt": updated_at,
            "search": search,
            "pageNumber": page_number,
            "pageSize": page_size,
            "sort": sort,
            "order": order,
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

        return PageDtoXmlAssistantProfileListDto.model_validate(r.json())
