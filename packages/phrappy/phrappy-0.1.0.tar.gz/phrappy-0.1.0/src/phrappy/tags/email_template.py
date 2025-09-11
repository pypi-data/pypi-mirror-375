from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import OrganizationEmailTemplateDto, PageDtoOrganizationEmailTemplateDto


class EmailTemplateOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def get_org_email_template(
        self,
        template_uid: str,
        phrase_token: Optional[str] = None,
    ) -> OrganizationEmailTemplateDto:
        """
        Operation id: getOrgEmailTemplate
        Get email template

        :param template_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: OrganizationEmailTemplateDto
        """

        endpoint = f"/api2/v1/emailTemplates/{template_uid}"

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

        return OrganizationEmailTemplateDto.model_validate(r.json())

    def list_org_email_templates(
        self,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        type: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoOrganizationEmailTemplateDto:
        """
        Operation id: listOrgEmailTemplates
        List email templates

        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param type: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoOrganizationEmailTemplateDto
        """

        endpoint = "/api2/v1/emailTemplates"

        params = {"type": type, "pageNumber": page_number, "pageSize": page_size}

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

        return PageDtoOrganizationEmailTemplateDto.model_validate(r.json())
