from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import json

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    AsyncExportTMByQueryResponseDto,
    AsyncExportTMResponseDto,
    AsyncRequestWrapperDto,
    AsyncRequestWrapperV2Dto,
    BackgroundTasksTmDto,
    BulkDeleteTmDto,
    CleanedTransMemoriesDto,
    ExportByQueryDto,
    ExportTMDto,
    MetadataResponse2,
    PageDtoAbstractProjectDto,
    PageDtoTransMemoryDto,
    ProjectTemplateTransMemoryListDtoV3,
    SearchRequestDto,
    SearchResponseListTmDto,
    SearchResponseListTmDtoV3,
    SearchTMByJobRequestDto,
    SearchTMByJobRequestDtoV3,
    SearchTMRequestDto,
    SegmentDto,
    TargetLanguageDto,
    TransMemoryCreateDto,
    TransMemoryDto,
    TransMemoryEditDto,
    TranslationDto,
    TranslationResourcesDto,
    WildCardSearchByJobRequestDtoV3,
    WildCardSearchRequestDto,
)


class TranslationMemoryOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def add_target_lang_to_trans_memory(
        self,
        trans_memory_uid: str,
        target_language_dto: Optional[TargetLanguageDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> TransMemoryDto:
        """
        Operation id: addTargetLangToTransMemory
        Add target language to translation memory

        :param trans_memory_uid: str (required), path.
        :param target_language_dto: Optional[TargetLanguageDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TransMemoryDto
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/targetLanguages"
        if type(target_language_dto) is dict:
            target_language_dto = TargetLanguageDto.model_validate(target_language_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = target_language_dto

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

        return TransMemoryDto.model_validate(r.json())

    def bulk_delete_trans_memories(
        self,
        bulk_delete_tm_dto: Optional[BulkDeleteTmDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: bulkDeleteTransMemories
        Delete translation memories (batch)

        :param bulk_delete_tm_dto: Optional[BulkDeleteTmDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = "/api2/v1/transMemories/bulk"
        if type(bulk_delete_tm_dto) is dict:
            bulk_delete_tm_dto = BulkDeleteTmDto.model_validate(bulk_delete_tm_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = bulk_delete_tm_dto

        self.client.make_request(
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

    def clear_trans_memory(
        self,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: clearTransMemory
        Delete all segments

        :param trans_memory_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/segments"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        self.client.make_request(
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

    def clear_trans_memory_v2(
        self,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: clearTransMemoryV2
        Delete all segments.
        This call is **asynchronous**, use [this API](#operation/getAsyncRequest) to check the result
        :param trans_memory_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v2/transMemories/{trans_memory_uid}/segments"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = self.client.make_request(
            "DELETE",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return r.content

    def create_trans_memory(
        self,
        trans_memory_create_dto: Optional[TransMemoryCreateDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> TransMemoryDto:
        """
        Operation id: createTransMemory
        Create translation memory

        :param trans_memory_create_dto: Optional[TransMemoryCreateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TransMemoryDto
        """

        endpoint = "/api2/v1/transMemories"
        if type(trans_memory_create_dto) is dict:
            trans_memory_create_dto = TransMemoryCreateDto.model_validate(
                trans_memory_create_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = trans_memory_create_dto

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

        return TransMemoryDto.model_validate(r.json())

    def delete_source_and_translations(
        self,
        segment_id: str,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteSourceAndTranslations
        Delete both source and translation
        Not recommended for bulk removal of segments
        :param segment_id: str (required), path.
        :param trans_memory_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/segments/{segment_id}"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        self.client.make_request(
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

    def delete_trans_memory(
        self,
        trans_memory_uid: str,
        purge: Optional[bool] = False,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteTransMemory
        Delete translation memory

        :param trans_memory_uid: str (required), path.
        :param purge: Optional[bool] = False (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}"

        params = {"purge": purge}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        self.client.make_request(
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

    def delete_translation(
        self,
        lang: str,
        segment_id: str,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteTranslation
        Delete segment of given language
        Not recommended for bulk removal of segments
        :param lang: str (required), path.
        :param segment_id: str (required), path.
        :param trans_memory_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/segments/{segment_id}/lang/{lang}"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        self.client.make_request(
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

    def download_cleaned_tm(
        self,
        async_request_id: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: downloadCleanedTM
        Download cleaned TM

        :param async_request_id: str (required), path. Request ID.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/transMemories/downloadCleaned/{async_request_id}"

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

        return r.content

    def download_search_result(
        self,
        async_request_id: str,
        fields: Optional[List[str]] = None,
        format: Optional[str] = "TMX",
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: downloadSearchResult
        Download export

        :param async_request_id: str (required), path. Request ID.
        :param fields: Optional[List[str]] = None (optional), query. Fields to include in exported XLSX.
        :param format: Optional[str] = "TMX" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/transMemories/downloadExport/{async_request_id}"

        params = {"format": format, "fields": fields}

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

        return r.content

    def edit_trans_memory(
        self,
        trans_memory_uid: str,
        trans_memory_edit_dto: Optional[TransMemoryEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> TransMemoryDto:
        """
        Operation id: editTransMemory
        Edit translation memory

        :param trans_memory_uid: str (required), path.
        :param trans_memory_edit_dto: Optional[TransMemoryEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TransMemoryDto
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}"
        if type(trans_memory_edit_dto) is dict:
            trans_memory_edit_dto = TransMemoryEditDto.model_validate(
                trans_memory_edit_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = trans_memory_edit_dto

        r = self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return TransMemoryDto.model_validate(r.json())

    def export_by_query_async(
        self,
        trans_memory_uid: str,
        export_by_query_dto: Optional[ExportByQueryDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AsyncExportTMByQueryResponseDto:
        """
        Operation id: exportByQueryAsync
        Search translation memory
        Use [this API](#operation/downloadSearchResult) to download result
        :param trans_memory_uid: str (required), path.
        :param export_by_query_dto: Optional[ExportByQueryDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncExportTMByQueryResponseDto
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/exportByQueryAsync"
        if type(export_by_query_dto) is dict:
            export_by_query_dto = ExportByQueryDto.model_validate(export_by_query_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = export_by_query_dto

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

        return AsyncExportTMByQueryResponseDto.model_validate(r.json())

    def export_cleaned_t_ms(
        self,
        cleaned_trans_memories_dto: Optional[CleanedTransMemoriesDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AsyncRequestWrapperDto:
        """
        Operation id: exportCleanedTMs
        Extract cleaned translation memory
        Returns a ZIP file containing the cleaned translation memories in the specified outputFormat.
        :param cleaned_trans_memories_dto: Optional[CleanedTransMemoriesDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperDto
        """

        endpoint = "/api2/v1/transMemories/extractCleaned"
        if type(cleaned_trans_memories_dto) is dict:
            cleaned_trans_memories_dto = CleanedTransMemoriesDto.model_validate(
                cleaned_trans_memories_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = cleaned_trans_memories_dto

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

        return AsyncRequestWrapperDto.model_validate(r.json())

    def export_v2(
        self,
        trans_memory_uid: str,
        export_tm_dto: Optional[ExportTMDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AsyncExportTMResponseDto:
        """
        Operation id: exportV2
        Export translation memory
        Use [this API](#operation/downloadSearchResult) to download result
        :param trans_memory_uid: str (required), path.
        :param export_tm_dto: Optional[ExportTMDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncExportTMResponseDto
        """

        endpoint = f"/api2/v2/transMemories/{trans_memory_uid}/export"
        if type(export_tm_dto) is dict:
            export_tm_dto = ExportTMDto.model_validate(export_tm_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = export_tm_dto

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

        return AsyncExportTMResponseDto.model_validate(r.json())

    def get_background_tasks_for_trans_mems(
        self,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
    ) -> BackgroundTasksTmDto:
        """
        Operation id: getBackgroundTasksForTransMems
        Get last task information

        :param trans_memory_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: BackgroundTasksTmDto
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/lastBackgroundTask"

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

        return BackgroundTasksTmDto.model_validate(r.json())

    def get_metadata(
        self,
        trans_memory_uid: str,
        by_language: Optional[bool] = False,
        phrase_token: Optional[str] = None,
    ) -> MetadataResponse2:
        """
        Operation id: getMetadata
        Get translation memory metadata

        :param trans_memory_uid: str (required), path.
        :param by_language: Optional[bool] = False (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MetadataResponse2
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/metadata"

        params = {"byLanguage": by_language}

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

        return MetadataResponse2.model_validate(r.json())

    def get_project_template_trans_memories_2(
        self,
        project_template_uid: str,
        target_lang: Optional[str] = None,
        wf_step_uid: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectTemplateTransMemoryListDtoV3:
        """
        Operation id: getProjectTemplateTransMemories_2
        Get translation memories

        :param project_template_uid: str (required), path.
        :param target_lang: Optional[str] = None (optional), query. Filter project translation memories by target language.
        :param wf_step_uid: Optional[str] = None (optional), query. Filter project translation memories by workflow step.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplateTransMemoryListDtoV3
        """

        endpoint = f"/api2/v3/projectTemplates/{project_template_uid}/transMemories"

        params = {"targetLang": target_lang, "wfStepUid": wf_step_uid}

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

        return ProjectTemplateTransMemoryListDtoV3.model_validate(r.json())

    def get_related_projects(
        self,
        trans_memory_uid: str,
        name: Optional[str] = None,
        order: Optional[List[str]] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoAbstractProjectDto:
        """
        Operation id: getRelatedProjects
        List related projects

        :param trans_memory_uid: str (required), path.
        :param name: Optional[str] = None (optional), query. Project name to filter by.
        :param order: Optional[List[str]] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[List[str]] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAbstractProjectDto
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/relatedProjects"

        params = {
            "name": name,
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

        return PageDtoAbstractProjectDto.model_validate(r.json())

    def get_trans_memory(
        self,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
    ) -> TransMemoryDto:
        """
        Operation id: getTransMemory
        Get translation memory

        :param trans_memory_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TransMemoryDto
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}"

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

        return TransMemoryDto.model_validate(r.json())

    def get_translation_resources(
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

        return TranslationResourcesDto.model_validate(r.json())

    def import_trans_memory_v2(
        self,
        content_disposition: str,
        trans_memory_uid: str,
        content_length: Optional[int] = None,
        file_bytes: Optional[bytes] = None,
        exclude_not_confirmed_segments: Optional[bool] = False,
        strict_lang_matching: Optional[bool] = False,
        strip_native_codes: Optional[bool] = True,
        phrase_token: Optional[str] = None,
    ) -> AsyncRequestWrapperV2Dto:
        """
        Operation id: importTransMemoryV2
        Import TMX

        :param content_disposition: str (required), header. must match pattern `((inline|attachment); )?filename\\*=UTF-8''(.+)`.
        :param trans_memory_uid: str (required), path.
        :param content_length: Optional[int] = None (optional), header.
        :param file_bytes: Optional[bytes] = None (optional), body.
        :param exclude_not_confirmed_segments: Optional[bool] = False (optional), query.
        :param strict_lang_matching: Optional[bool] = False (optional), query.
        :param strip_native_codes: Optional[bool] = True (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperV2Dto
        """

        endpoint = f"/api2/v2/transMemories/{trans_memory_uid}/import"

        params = {
            "strictLangMatching": strict_lang_matching,
            "stripNativeCodes": strip_native_codes,
            "excludeNotConfirmedSegments": exclude_not_confirmed_segments,
        }

        headers = {
            "Content-Length": (
                content_length.model_dump_json()
                if hasattr(content_length, "model_dump_json")
                else (
                    json.dumps(content_length)
                    if False and not isinstance(content_length, str)
                    else str(content_length)
                )
            ),
            "Content-Disposition": (
                content_disposition.model_dump_json()
                if hasattr(content_disposition, "model_dump_json")
                else (
                    json.dumps(content_disposition)
                    if False and not isinstance(content_disposition, str)
                    else str(content_disposition)
                )
            ),
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        payload = None
        content = file_bytes

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

        return AsyncRequestWrapperV2Dto.model_validate(r.json())

    def insert_to_trans_memory(
        self,
        trans_memory_uid: str,
        segment_dto: Optional[SegmentDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: insertToTransMemory
        Insert segment

        :param trans_memory_uid: str (required), path.
        :param segment_dto: Optional[SegmentDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/segments"
        if type(segment_dto) is dict:
            segment_dto = SegmentDto.model_validate(segment_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = segment_dto

        self.client.make_request(
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

    def list_trans_memories(
        self,
        business_unit_id: Optional[str] = None,
        client_id: Optional[str] = None,
        domain_id: Optional[str] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        source_lang: Optional[str] = None,
        sub_domain_id: Optional[str] = None,
        target_lang: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoTransMemoryDto:
        """
        Operation id: listTransMemories
        List translation memories

        :param business_unit_id: Optional[str] = None (optional), query.
        :param client_id: Optional[str] = None (optional), query.
        :param domain_id: Optional[str] = None (optional), query.
        :param name: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param source_lang: Optional[str] = None (optional), query.
        :param sub_domain_id: Optional[str] = None (optional), query.
        :param target_lang: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTransMemoryDto
        """

        endpoint = "/api2/v1/transMemories"

        params = {
            "name": name,
            "sourceLang": source_lang,
            "targetLang": target_lang,
            "clientId": client_id,
            "domainId": domain_id,
            "subDomainId": sub_domain_id,
            "businessUnitId": business_unit_id,
            "pageNumber": page_number,
            "pageSize": page_size,
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

        return PageDtoTransMemoryDto.model_validate(r.json())

    def relevant_trans_memories_for_project(
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
    ) -> PageDtoTransMemoryDto:
        """
        Operation id: relevantTransMemoriesForProject
        List project relevant translation memories

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

        :return: PageDtoTransMemoryDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/transMemories/relevant"

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

        return PageDtoTransMemoryDto.model_validate(r.json())

    def relevant_trans_memories_for_project_template(
        self,
        project_template_uid: str,
        client_name: Optional[str] = None,
        domain_name: Optional[str] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        strict_lang_matching: Optional[bool] = False,
        sub_domain_name: Optional[str] = None,
        target_langs: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoTransMemoryDto:
        """
        Operation id: relevantTransMemoriesForProjectTemplate
        List project template relevant translation memories

        :param project_template_uid: str (required), path.
        :param client_name: Optional[str] = None (optional), query.
        :param domain_name: Optional[str] = None (optional), query.
        :param name: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param strict_lang_matching: Optional[bool] = False (optional), query.
        :param sub_domain_name: Optional[str] = None (optional), query.
        :param target_langs: Optional[List[str]] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTransMemoryDto
        """

        endpoint = (
            f"/api2/v1/projectTemplates/{project_template_uid}/transMemories/relevant"
        )

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

        return PageDtoTransMemoryDto.model_validate(r.json())

    def search(
        self,
        trans_memory_uid: str,
        search_request_dto: Optional[SearchRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchResponseListTmDto:
        """
        Operation id: search
        Search translation memory (sync)

        :param trans_memory_uid: str (required), path.
        :param search_request_dto: Optional[SearchRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDto
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/search"
        if type(search_request_dto) is dict:
            search_request_dto = SearchRequestDto.model_validate(search_request_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = search_request_dto

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

        return SearchResponseListTmDto.model_validate(r.json())

    def search_by_job3(
        self,
        job_uid: str,
        project_uid: str,
        search_tm_by_job_request_dto_v3: Optional[
            SearchTMByJobRequestDtoV3 | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchResponseListTmDtoV3:
        """
        Operation id: searchByJob3
        Search job's translation memories

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param search_tm_by_job_request_dto_v3: Optional[SearchTMByJobRequestDtoV3 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDtoV3
        """

        endpoint = (
            f"/api2/v3/projects/{project_uid}/jobs/{job_uid}/transMemories/search"
        )
        if type(search_tm_by_job_request_dto_v3) is dict:
            search_tm_by_job_request_dto_v3 = SearchTMByJobRequestDtoV3.model_validate(
                search_tm_by_job_request_dto_v3
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = search_tm_by_job_request_dto_v3

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

        return SearchResponseListTmDtoV3.model_validate(r.json())

    def search_segment_by_job(
        self,
        job_uid: str,
        project_uid: str,
        search_tm_by_job_request_dto: Optional[SearchTMByJobRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchResponseListTmDto:
        """
        Operation id: searchSegmentByJob
        Search translation memory for segment by job
        Returns at most <i>maxSegments</i>
                    records with <i>score >= scoreThreshold</i> and at most <i>maxSubsegments</i> records which are subsegment,
                    i.e. the source text is substring of the query text.
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param search_tm_by_job_request_dto: Optional[SearchTMByJobRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/transMemories/searchSegment"
        if type(search_tm_by_job_request_dto) is dict:
            search_tm_by_job_request_dto = SearchTMByJobRequestDto.model_validate(
                search_tm_by_job_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = search_tm_by_job_request_dto

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

        return SearchResponseListTmDto.model_validate(r.json())

    def search_tm_segment(
        self,
        project_uid: str,
        search_tm_request_dto: Optional[SearchTMRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchResponseListTmDto:
        """
        Operation id: searchTmSegment
        Search translation memory for segment in the project
        Returns at most <i>maxSegments</i>
                    records with <i>score >= scoreThreshold</i> and at most <i>maxSubsegments</i> records which are subsegment,
                    i.e. the source text is substring of the query text.
        :param project_uid: str (required), path.
        :param search_tm_request_dto: Optional[SearchTMRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDto
        """

        endpoint = (
            f"/api2/v1/projects/{project_uid}/transMemories/searchSegmentInProject"
        )
        if type(search_tm_request_dto) is dict:
            search_tm_request_dto = SearchTMRequestDto.model_validate(
                search_tm_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = search_tm_request_dto

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

        return SearchResponseListTmDto.model_validate(r.json())

    def update_translation(
        self,
        segment_id: str,
        trans_memory_uid: str,
        translation_dto: Optional[TranslationDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: updateTranslation
        Edit segment

        :param segment_id: str (required), path.
        :param trans_memory_uid: str (required), path.
        :param translation_dto: Optional[TranslationDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/segments/{segment_id}"
        if type(translation_dto) is dict:
            translation_dto = TranslationDto.model_validate(translation_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = translation_dto

        self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return

    def wild_card_search_by_job3(
        self,
        job_uid: str,
        project_uid: str,
        wild_card_search_by_job_request_dto_v3: Optional[
            WildCardSearchByJobRequestDtoV3 | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchResponseListTmDtoV3:
        """
        Operation id: wildCardSearchByJob3
        Wildcard search job's translation memories

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param wild_card_search_by_job_request_dto_v3: Optional[WildCardSearchByJobRequestDtoV3 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDtoV3
        """

        endpoint = f"/api2/v3/projects/{project_uid}/jobs/{job_uid}/transMemories/wildCardSearch"
        if type(wild_card_search_by_job_request_dto_v3) is dict:
            wild_card_search_by_job_request_dto_v3 = (
                WildCardSearchByJobRequestDtoV3.model_validate(
                    wild_card_search_by_job_request_dto_v3
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = wild_card_search_by_job_request_dto_v3

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

        return SearchResponseListTmDtoV3.model_validate(r.json())

    def wildcard_search(
        self,
        trans_memory_uid: str,
        wild_card_search_request_dto: Optional[WildCardSearchRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchResponseListTmDto:
        """
        Operation id: wildcardSearch
        Wildcard search

        :param trans_memory_uid: str (required), path.
        :param wild_card_search_request_dto: Optional[WildCardSearchRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDto
        """

        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/wildCardSearch"
        if type(wild_card_search_request_dto) is dict:
            wild_card_search_request_dto = WildCardSearchRequestDto.model_validate(
                wild_card_search_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = wild_card_search_request_dto

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

        return SearchResponseListTmDto.model_validate(r.json())
