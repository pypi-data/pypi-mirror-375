from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import json

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    GlossaryActivationDto,
    GlossaryDto,
    GlossaryEditDto,
    ImportGlossaryResponseDto,
    PageDtoGlossaryDto,
)


class GlossaryOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def activate_glossary(
        self,
        glossary_uid: str,
        glossary_activation_dto: Optional[GlossaryActivationDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> GlossaryDto:
        """
        Operation id: activateGlossary
        Activate/Deactivate glossary

        :param glossary_uid: str (required), path.
        :param glossary_activation_dto: Optional[GlossaryActivationDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: GlossaryDto
        """

        endpoint = f"/api2/v1/glossaries/{glossary_uid}/activate"
        if type(glossary_activation_dto) is dict:
            glossary_activation_dto = GlossaryActivationDto.model_validate(
                glossary_activation_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = glossary_activation_dto

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

        return GlossaryDto.model_validate(r.json())

    async def create_glossary(
        self,
        glossary_edit_dto: Optional[GlossaryEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> GlossaryDto:
        """
        Operation id: createGlossary
        Create glossary

        :param glossary_edit_dto: Optional[GlossaryEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: GlossaryDto
        """

        endpoint = "/api2/v1/glossaries"
        if type(glossary_edit_dto) is dict:
            glossary_edit_dto = GlossaryEditDto.model_validate(glossary_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = glossary_edit_dto

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

        return GlossaryDto.model_validate(r.json())

    async def delete_glossary(
        self,
        glossary_uid: str,
        purge: Optional[bool] = False,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteGlossary
        Delete glossary

        :param glossary_uid: str (required), path.
        :param purge: Optional[bool] = False (optional), query. purge=false - the Glossary can later be restored,
                            'purge=true - the Glossary is completely deleted and cannot be restored.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/glossaries/{glossary_uid}"

        params = {"purge": purge}

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

    async def export_glossary(
        self,
        glossary_uid: str,
        format: Optional[str] = "Tbx",
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: exportGlossary
        Export glossary

        This API endpoint is still limited access, and only available to customers on the Enterprise plans on request.
        Please contact support or your customer success manager if you are interested.

        :param glossary_uid: str (required), path.
        :param format: Optional[str] = "Tbx" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/glossaries/{glossary_uid}/export"

        params = {"format": format}

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

        return await r.aread()

    async def get_glossary(
        self,
        glossary_uid: str,
        phrase_token: Optional[str] = None,
    ) -> GlossaryDto:
        """
        Operation id: getGlossary
        Get glossary

        :param glossary_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: GlossaryDto
        """

        endpoint = f"/api2/v1/glossaries/{glossary_uid}"

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

        return GlossaryDto.model_validate(r.json())

    async def list_glossaries(
        self,
        lang: Optional[List[str]] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoGlossaryDto:
        """
        Operation id: listGlossaries
        List glossaries

        :param lang: Optional[List[str]] = None (optional), query. Language of the glossary.
        :param name: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoGlossaryDto
        """

        endpoint = "/api2/v1/glossaries"

        params = {
            "name": name,
            "lang": lang,
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

        return PageDtoGlossaryDto.model_validate(r.json())

    async def purge_glossary(
        self,
        glossary_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: purgeGlossary
        Purge glossary

        This API endpoint is still limited access, and only available to customers on the Enterprise plans on request.
        Please contact support or your customer success manager if you are interested.

        :param glossary_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/glossaries/{glossary_uid}/purge"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        await self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return

    async def update_glossary(
        self,
        glossary_uid: str,
        glossary_edit_dto: Optional[GlossaryEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> GlossaryDto:
        """
        Operation id: updateGlossary
        Edit glossary
        Languages can only be added, their removal is not supported
        :param glossary_uid: str (required), path.
        :param glossary_edit_dto: Optional[GlossaryEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: GlossaryDto
        """

        endpoint = f"/api2/v1/glossaries/{glossary_uid}"
        if type(glossary_edit_dto) is dict:
            glossary_edit_dto = GlossaryEditDto.model_validate(glossary_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = glossary_edit_dto

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

        return GlossaryDto.model_validate(r.json())

    async def upload_glossary(
        self,
        content_disposition: str,
        glossary_uid: str,
        file_bytes: Optional[bytes] = None,
        strict_lang_matching: Optional[bool] = False,
        update_terms: Optional[bool] = True,
        phrase_token: Optional[str] = None,
    ) -> ImportGlossaryResponseDto:
        """
        Operation id: uploadGlossary
        Upload glossary

        This API endpoint is still limited access, and only available to customers on the Enterprise plans on request.
        Please contact support or your customer success manager if you are interested.

        Glossaries can be imported from XLS/XLSX and TBX file formats.

        :param content_disposition: str (required), header. must match pattern `((inline|attachment); )?filename\\*=UTF-8''(.+)`.
        :param glossary_uid: str (required), path.
        :param file_bytes: Optional[bytes] = None (optional), body.
        :param strict_lang_matching: Optional[bool] = False (optional), query.
        :param update_terms: Optional[bool] = True (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportGlossaryResponseDto
        """

        endpoint = f"/api2/v1/glossaries/{glossary_uid}/upload"

        params = {
            "strictLangMatching": strict_lang_matching,
            "updateTerms": update_terms,
        }

        headers = {
            "Content-Disposition": (
                content_disposition.model_dump_json()
                if hasattr(content_disposition, "model_dump_json")
                else (
                    json.dumps(content_disposition)
                    if False and not isinstance(content_disposition, str)
                    else str(content_disposition)
                )
            )
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        payload = None
        content = file_bytes

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

        return ImportGlossaryResponseDto.model_validate(r.json())
