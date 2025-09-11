from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import json

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    BackgroundTasksTbDto,
    BrowseRequestDto,
    BrowseResponseListDto,
    ConceptDto,
    ConceptEditDto,
    ConceptListReference,
    ConceptListResponseDto,
    ConceptWithMetadataDto,
    CreateTermsDto,
    ImportTermBaseResponseDto,
    MetadataTbDto,
    PageDtoTermBaseDto,
    ProjectTemplateTermBaseListDto,
    ProjectTermBaseListDto,
    SearchInTextResponseList2Dto,
    SearchResponseListTbDto,
    SearchTbByJobRequestDto,
    SearchTbInTextByJobRequestDto,
    SearchTbResponseListDto,
    SetProjectTemplateTermBaseDto,
    SetTermBaseDto,
    TermBaseCreateDto,
    TermBaseDto,
    TermBaseSearchRequestDto,
    TermBaseUpdateDto,
    TermCreateDto,
    TermDto,
    TermEditDto,
    TermPairDto,
    TranslationResourcesDto,
)


class TermBaseOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def browse_terms(
        self,
        term_base_uid: str,
        browse_request_dto: Optional[BrowseRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> BrowseResponseListDto:
        """
        Operation id: browseTerms
        Browse term base

        :param term_base_uid: str (required), path.
        :param browse_request_dto: Optional[BrowseRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: BrowseResponseListDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/browse"
        if type(browse_request_dto) is dict:
            browse_request_dto = BrowseRequestDto.model_validate(browse_request_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = browse_request_dto

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

        return BrowseResponseListDto.model_validate(r.json())

    async def clear_term_base(
        self,
        term_base_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: clearTermBase
        Clear term base
        Deletes all terms
        :param term_base_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/terms"

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

    async def create_concept(
        self,
        term_base_uid: str,
        concept_edit_dto: Optional[ConceptEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ConceptWithMetadataDto:
        """
        Operation id: createConcept
        Create concept

        :param term_base_uid: str (required), path.
        :param concept_edit_dto: Optional[ConceptEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConceptWithMetadataDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/concepts"
        if type(concept_edit_dto) is dict:
            concept_edit_dto = ConceptEditDto.model_validate(concept_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = concept_edit_dto

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

        return ConceptWithMetadataDto.model_validate(r.json())

    async def create_term(
        self,
        term_base_uid: str,
        term_create_dto: Optional[TermCreateDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> TermDto:
        """
        Operation id: createTerm
        Create term
        Set conceptId to assign the term to an existing concept, otherwise a new concept will be created.
        :param term_base_uid: str (required), path.
        :param term_create_dto: Optional[TermCreateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TermDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/terms"
        if type(term_create_dto) is dict:
            term_create_dto = TermCreateDto.model_validate(term_create_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = term_create_dto

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

        return TermDto.model_validate(r.json())

    async def create_term_base(
        self,
        term_base_create_dto: Optional[TermBaseCreateDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> TermBaseDto:
        """
        Operation id: createTermBase
        Create term base

        :param term_base_create_dto: Optional[TermBaseCreateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TermBaseDto
        """

        endpoint = "/api2/v1/termBases"
        if type(term_base_create_dto) is dict:
            term_base_create_dto = TermBaseCreateDto.model_validate(
                term_base_create_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = term_base_create_dto

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

        return TermBaseDto.model_validate(r.json())

    async def create_term_by_job(
        self,
        job_uid: str,
        project_uid: str,
        create_terms_dto: Optional[CreateTermsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> TermPairDto:
        """
        Operation id: createTermByJob
        Create term in job's term bases
        Create new term in the write term base assigned to the job
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param create_terms_dto: Optional[CreateTermsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TermPairDto
        """

        endpoint = (
            f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/termBases/createByJob"
        )
        if type(create_terms_dto) is dict:
            create_terms_dto = CreateTermsDto.model_validate(create_terms_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_terms_dto

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

        return TermPairDto.model_validate(r.json())

    async def delete_concept(
        self,
        concept_id: str,
        term_base_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteConcept
        Delete concept

        :param concept_id: str (required), path.
        :param term_base_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/concepts/{concept_id}"

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

    async def delete_concepts(
        self,
        term_base_uid: str,
        concept_list_reference: Optional[ConceptListReference | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteConcepts
        Delete concepts

        :param term_base_uid: str (required), path.
        :param concept_list_reference: Optional[ConceptListReference | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/concepts"
        if type(concept_list_reference) is dict:
            concept_list_reference = ConceptListReference.model_validate(
                concept_list_reference
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = concept_list_reference

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

    async def delete_term(
        self,
        term_base_uid: str,
        term_id: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteTerm
        Delete term

        :param term_base_uid: str (required), path.
        :param term_id: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/terms/{term_id}"

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

    async def delete_term_base(
        self,
        term_base_uid: str,
        purge: Optional[bool] = False,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteTermBase
        Delete term base

        :param term_base_uid: str (required), path.
        :param purge: Optional[bool] = False (optional), query. purge=false - the Termbase is can later be restored,
                            "purge=true - the Termbase is completely deleted and cannot be restored.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}"

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

    async def export_term_base(
        self,
        term_base_uid: str,
        charset: Optional[str] = "UTF-8",
        domain: Optional[str] = None,
        format: Optional[str] = "Tbx",
        sub_domain: Optional[str] = None,
        term_field: Optional[List[str]] = None,
        term_status: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: exportTermBase
        Export term base

        :param term_base_uid: str (required), path.
        :param charset: Optional[str] = "UTF-8" (optional), query.
        :param domain: Optional[str] = None (optional), query. Domain UID to filter by.
        :param format: Optional[str] = "Tbx" (optional), query.
        :param sub_domain: Optional[str] = None (optional), query. SubDomain UID to filter by.
        :param term_field: Optional[List[str]] = None (optional), query. List of term fields to export (applicable only for XLSX format).
        :param term_status: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/export"

        params = {
            "format": format,
            "charset": charset,
            "termStatus": term_status,
            "termField": term_field,
            "domain": domain,
            "subDomain": sub_domain,
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

        return await r.aread()

    async def get_concept(
        self,
        concept_id: str,
        term_base_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ConceptWithMetadataDto:
        """
        Operation id: getConcept
        Get concept

        :param concept_id: str (required), path.
        :param term_base_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConceptWithMetadataDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/concepts/{concept_id}"

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

        return ConceptWithMetadataDto.model_validate(r.json())

    async def get_last_background_task(
        self,
        term_base_uid: str,
        phrase_token: Optional[str] = None,
    ) -> BackgroundTasksTbDto:
        """
        Operation id: getLastBackgroundTask
        Last import status

        :param term_base_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: BackgroundTasksTbDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/lastBackgroundTask"

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

        return BackgroundTasksTbDto.model_validate(r.json())

    async def get_project_template_term_bases(
        self,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ProjectTemplateTermBaseListDto:
        """
        Operation id: getProjectTemplateTermBases
        Get term bases

        :param project_template_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplateTermBaseListDto
        """

        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/termBases"

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

        return ProjectTemplateTermBaseListDto.model_validate(r.json())

    async def get_project_term_bases(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ProjectTermBaseListDto:
        """
        Operation id: getProjectTermBases
        Get term bases

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTermBaseListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/termBases"

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

        return ProjectTermBaseListDto.model_validate(r.json())

    async def get_term(
        self,
        term_base_uid: str,
        term_id: str,
        phrase_token: Optional[str] = None,
    ) -> TermDto:
        """
        Operation id: getTerm
        Get term

        :param term_base_uid: str (required), path.
        :param term_id: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TermDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/terms/{term_id}"

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

        return TermDto.model_validate(r.json())

    async def get_term_base(
        self,
        term_base_uid: str,
        phrase_token: Optional[str] = None,
    ) -> TermBaseDto:
        """
        Operation id: getTermBase
        Get term base

        :param term_base_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TermBaseDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}"

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

        return TermBaseDto.model_validate(r.json())

    async def get_term_base_metadata(
        self,
        term_base_uid: str,
        phrase_token: Optional[str] = None,
    ) -> MetadataTbDto:
        """
        Operation id: getTermBaseMetadata
        Get term base metadata

        :param term_base_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MetadataTbDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/metadata"

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

        return MetadataTbDto.model_validate(r.json())

    async def get_translation_resources(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> TranslationResourcesDto:
        """
        Operation id: getTranslationResources
        Get translation resources

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationResourcesDto
        """

        endpoint = (
            f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/translationResources"
        )

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

        return TranslationResourcesDto.model_validate(r.json())

    async def import_term_base(
        self,
        content_disposition: str,
        term_base_uid: str,
        file_bytes: Optional[bytes] = None,
        charset: Optional[str] = "UTF-8",
        strict_lang_matching: Optional[bool] = False,
        update_terms: Optional[bool] = True,
        phrase_token: Optional[str] = None,
    ) -> ImportTermBaseResponseDto:
        """
        Operation id: importTermBase
        Upload term base

        Terms can be imported from XLS/XLSX and TBX file formats into a term base.
        See <a target="_blank" href="https://support.phrase.com/hc/en-us/articles/5709733372188">Phrase Help Center</a>

        :param content_disposition: str (required), header. must match pattern `((inline|attachment); )?filename\\*=UTF-8''(.+)`.
        :param term_base_uid: str (required), path.
        :param file_bytes: Optional[bytes] = None (optional), body.
        :param charset: Optional[str] = "UTF-8" (optional), query.
        :param strict_lang_matching: Optional[bool] = False (optional), query.
        :param update_terms: Optional[bool] = True (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportTermBaseResponseDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/upload"

        params = {
            "charset": charset,
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

        return ImportTermBaseResponseDto.model_validate(r.json())

    async def import_term_base_v2(
        self,
        content_disposition: str,
        term_base_uid: str,
        file_bytes: Optional[bytes] = None,
        charset: Optional[str] = "UTF-8",
        strict_lang_matching: Optional[bool] = False,
        update_terms: Optional[bool] = True,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: importTermBaseV2
        Upload term base

        Terms can be imported from XLS/XLSX and TBX file formats into a term base.
        See <a target="_blank" href="https://support.phrase.com/hc/en-us/articles/5709733372188">Phrase Help Center</a>

        :param content_disposition: str (required), header. must match pattern `((inline|attachment); )?filename\\*=UTF-8''(.+)`.
        :param term_base_uid: str (required), path.
        :param file_bytes: Optional[bytes] = None (optional), body.
        :param charset: Optional[str] = "UTF-8" (optional), query.
        :param strict_lang_matching: Optional[bool] = False (optional), query.
        :param update_terms: Optional[bool] = True (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        !!! N.B.: API docs have no 200 range response declared, so falling back to returning the raw bytes from the API response.

        :return: bytes
        """

        endpoint = f"/api2/v2/termBases/{term_base_uid}/upload"

        params = {
            "charset": charset,
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

        return await r.aread()

    async def list_concepts(
        self,
        term_base_uid: str,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> ConceptListResponseDto:
        """
        Operation id: listConcepts
        List concepts

        :param term_base_uid: str (required), path.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConceptListResponseDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/concepts"

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

        return ConceptListResponseDto.model_validate(r.json())

    async def list_term_bases(
        self,
        client_id: Optional[str] = None,
        domain_id: Optional[str] = None,
        lang: Optional[List[str]] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sub_domain_id: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoTermBaseDto:
        """
        Operation id: listTermBases
        List term bases

        :param client_id: Optional[str] = None (optional), query.
        :param domain_id: Optional[str] = None (optional), query.
        :param lang: Optional[List[str]] = None (optional), query. Language of the term base.
        :param name: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sub_domain_id: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTermBaseDto
        """

        endpoint = "/api2/v1/termBases"

        params = {
            "name": name,
            "lang": lang,
            "clientId": client_id,
            "domainId": domain_id,
            "subDomainId": sub_domain_id,
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

        return PageDtoTermBaseDto.model_validate(r.json())

    async def list_terms_of_concept(
        self,
        concept_id: str,
        term_base_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ConceptDto:
        """
        Operation id: listTermsOfConcept
        Get terms of concept

        :param concept_id: str (required), path.
        :param term_base_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConceptDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/concepts/{concept_id}/terms"

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

        return ConceptDto.model_validate(r.json())

    async def relevant_term_bases(
        self,
        project_uid: str,
        client_name: Optional[str] = None,
        domain_name: Optional[str] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        strict_lang_matching: Optional[bool] = False,
        sub_domain_name: Optional[str] = None,
        target_langs: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoTermBaseDto:
        """
        Operation id: relevantTermBases
        List project relevant term bases

        :param project_uid: str (required), path.
        :param client_name: Optional[str] = None (optional), query.
        :param domain_name: Optional[str] = None (optional), query.
        :param name: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param strict_lang_matching: Optional[bool] = False (optional), query.
        :param sub_domain_name: Optional[str] = None (optional), query.
        :param target_langs: Optional[List[str]] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTermBaseDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/termBases/relevant"

        params = {
            "name": name,
            "domainName": domain_name,
            "clientName": client_name,
            "subDomainName": sub_domain_name,
            "targetLangs": target_langs,
            "strictLangMatching": strict_lang_matching,
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

        return PageDtoTermBaseDto.model_validate(r.json())

    async def search_terms(
        self,
        term_base_uid: str,
        term_base_search_request_dto: Optional[TermBaseSearchRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchResponseListTbDto:
        """
        Operation id: searchTerms
        Search term base

        :param term_base_uid: str (required), path.
        :param term_base_search_request_dto: Optional[TermBaseSearchRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTbDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/search"
        if type(term_base_search_request_dto) is dict:
            term_base_search_request_dto = TermBaseSearchRequestDto.model_validate(
                term_base_search_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = term_base_search_request_dto

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

        return SearchResponseListTbDto.model_validate(r.json())

    async def search_terms_by_job_v2(
        self,
        job_uid: str,
        project_uid: str,
        search_tb_by_job_request_dto: Optional[SearchTbByJobRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchTbResponseListDto:
        """
        Operation id: searchTermsByJobV2
        Search job's term bases
        Search all read term bases assigned to the job
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param search_tb_by_job_request_dto: Optional[SearchTbByJobRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchTbResponseListDto
        """

        endpoint = (
            f"/api2/v2/projects/{project_uid}/jobs/{job_uid}/termBases/searchByJob"
        )
        if type(search_tb_by_job_request_dto) is dict:
            search_tb_by_job_request_dto = SearchTbByJobRequestDto.model_validate(
                search_tb_by_job_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = search_tb_by_job_request_dto

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

        return SearchTbResponseListDto.model_validate(r.json())

    async def search_terms_in_text_by_job_v2(
        self,
        job_uid: str,
        project_uid: str,
        search_tb_in_text_by_job_request_dto: Optional[
            SearchTbInTextByJobRequestDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchInTextResponseList2Dto:
        """
        Operation id: searchTermsInTextByJobV2
        Search terms in text
        Search in text in all read term bases assigned to the job
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param search_tb_in_text_by_job_request_dto: Optional[SearchTbInTextByJobRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchInTextResponseList2Dto
        """

        endpoint = f"/api2/v2/projects/{project_uid}/jobs/{job_uid}/termBases/searchInTextByJob"
        if type(search_tb_in_text_by_job_request_dto) is dict:
            search_tb_in_text_by_job_request_dto = (
                SearchTbInTextByJobRequestDto.model_validate(
                    search_tb_in_text_by_job_request_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = search_tb_in_text_by_job_request_dto

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

        return SearchInTextResponseList2Dto.model_validate(r.json())

    async def set_project_template_term_bases(
        self,
        project_template_uid: str,
        set_project_template_term_base_dto: Optional[
            SetProjectTemplateTermBaseDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectTemplateTermBaseListDto:
        """
        Operation id: setProjectTemplateTermBases
        Edit term bases in project template

        :param project_template_uid: str (required), path.
        :param set_project_template_term_base_dto: Optional[SetProjectTemplateTermBaseDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplateTermBaseListDto
        """

        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/termBases"
        if type(set_project_template_term_base_dto) is dict:
            set_project_template_term_base_dto = (
                SetProjectTemplateTermBaseDto.model_validate(
                    set_project_template_term_base_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = set_project_template_term_base_dto

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

        return ProjectTemplateTermBaseListDto.model_validate(r.json())

    async def set_project_term_bases(
        self,
        project_uid: str,
        set_term_base_dto: Optional[SetTermBaseDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectTermBaseListDto:
        """
        Operation id: setProjectTermBases
        Edit term bases

        :param project_uid: str (required), path.
        :param set_term_base_dto: Optional[SetTermBaseDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTermBaseListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/termBases"
        if type(set_term_base_dto) is dict:
            set_term_base_dto = SetTermBaseDto.model_validate(set_term_base_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = set_term_base_dto

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

        return ProjectTermBaseListDto.model_validate(r.json())

    async def update_concept(
        self,
        concept_id: str,
        term_base_uid: str,
        concept_edit_dto: Optional[ConceptEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ConceptWithMetadataDto:
        """
        Operation id: updateConcept
        Update concept

        :param concept_id: str (required), path.
        :param term_base_uid: str (required), path.
        :param concept_edit_dto: Optional[ConceptEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConceptWithMetadataDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/concepts/{concept_id}"
        if type(concept_edit_dto) is dict:
            concept_edit_dto = ConceptEditDto.model_validate(concept_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = concept_edit_dto

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

        return ConceptWithMetadataDto.model_validate(r.json())

    async def update_term(
        self,
        term_base_uid: str,
        term_id: str,
        term_edit_dto: Optional[TermEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> TermDto:
        """
        Operation id: updateTerm
        Edit term

        :param term_base_uid: str (required), path.
        :param term_id: str (required), path.
        :param term_edit_dto: Optional[TermEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TermDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}/terms/{term_id}"
        if type(term_edit_dto) is dict:
            term_edit_dto = TermEditDto.model_validate(term_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = term_edit_dto

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

        return TermDto.model_validate(r.json())

    async def update_term_base(
        self,
        term_base_uid: str,
        term_base_update_dto: Optional[TermBaseUpdateDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> TermBaseDto:
        """
        Operation id: updateTermBase
        Edit term base
        It is possible to add new languages only
        :param term_base_uid: str (required), path.
        :param term_base_update_dto: Optional[TermBaseUpdateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TermBaseDto
        """

        endpoint = f"/api2/v1/termBases/{term_base_uid}"
        if type(term_base_update_dto) is dict:
            term_base_update_dto = TermBaseUpdateDto.model_validate(
                term_base_update_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = term_base_update_dto

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

        return TermBaseDto.model_validate(r.json())
