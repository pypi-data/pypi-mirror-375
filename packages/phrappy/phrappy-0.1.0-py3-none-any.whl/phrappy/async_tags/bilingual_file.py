from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    ComparedSegmentsDto,
    GetBilingualFileDto,
    ProjectJobPartsDto,
    QualityAssuranceResponseDto,
)


class BilingualFileOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def compare_bilingual_file(
        self,
        file_bytes: Optional[bytes] = None,
        workflow_level: Optional[int] = 1,
        phrase_token: Optional[str] = None,
    ) -> ComparedSegmentsDto:
        """
        Operation id: compareBilingualFile
        Compare bilingual file
        Compares bilingual file to job state. Returns list of compared segments.
        :param file_bytes: Optional[bytes] = None (optional), body.
        :param workflow_level: Optional[int] = 1 (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ComparedSegmentsDto
        """

        endpoint = "/api2/v1/bilingualFiles/compare"

        params = {"workflowLevel": workflow_level}

        headers = {}
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

        return ComparedSegmentsDto.model_validate(r.json())

    async def convert_bilingual_file(
        self,
        frm: str,
        to: str,
        file_bytes: Optional[bytes] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: convertBilingualFile
        Convert bilingual file

        :param frm: str (required), query.
        :param to: str (required), query.
        :param file_bytes: Optional[bytes] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = "/api2/v1/bilingualFiles/convert"

        params = {"from": frm, "to": to}

        headers = {}
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

    async def get_bilingual_file(
        self,
        project_uid: str,
        get_bilingual_file_dto: Optional[GetBilingualFileDto | dict] = None,
        format: Optional[str] = "MXLF",
        preview: Optional[bool] = True,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: getBilingualFile
        Download bilingual file

        This API call generates a bilingual file in the chosen format by merging all submitted jobs together.
        Note that all submitted jobs must belong to the same project; it's not feasible to merge jobs from multiple projects.

        When dealing with MXLIFF or DOCX files, modifications made externally can be imported back into the Phrase TMS project.
        Any changes will be synchronized into the editor, allowing actions like confirming or locking segments.

        Unlike the user interface (UI), the APIs also support XLIFF as a bilingual format.

        While MXLIFF files are editable using various means, their primary intended use is with the
        [CAT Desktop Editor](https://support.phrase.com/hc/en-us/articles/5709683873052-CAT-Desktop-Editor-TMS-).
        It's crucial to note that alterations to the file incompatible with the CAT Desktop Editor's features may result in
        a corrupted file, leading to potential loss or duplication of work.

        :param project_uid: str (required), path.
        :param get_bilingual_file_dto: Optional[GetBilingualFileDto | dict] = None (optional), body.
        :param format: Optional[str] = "MXLF" (optional), query.
        :param preview: Optional[bool] = True (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/bilingualFile"
        if type(get_bilingual_file_dto) is dict:
            get_bilingual_file_dto = GetBilingualFileDto.model_validate(
                get_bilingual_file_dto
            )

        params = {"format": format, "preview": preview}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = get_bilingual_file_dto

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

    async def get_preview_file(
        self,
        file_bytes: Optional[bytes] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: getPreviewFile
        Download preview
        Supports mxliff format
        :param file_bytes: Optional[bytes] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = "/api2/v1/bilingualFiles/preview"

        params = {}

        headers = {}
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

    async def run_qa_and_save_v4(
        self,
        project_uid: str,
        segment_id: str,
        file_bytes: Optional[bytes] = None,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaAndSaveV4
        Run quality assurance on selected segments and save segments
        By default runs only fast running checks.
        :param project_uid: str (required), path.
        :param segment_id: str (required), path.
        :param file_bytes: Optional[bytes] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """

        endpoint = f"/api2/v4/projects/{project_uid}/jobs/qualityAssurances/segments/{segment_id}/runWithUpdate"

        params = {}

        headers = {}
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

        return QualityAssuranceResponseDto.model_validate(r.json())

    async def upload_bilingual_file_v2(
        self,
        file: bytes,
        save_to_trans_memory: Optional[str] = "Confirmed",
        set_completed: Optional[bool] = False,
        filename: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectJobPartsDto:
        """
        Operation id: uploadBilingualFileV2
        Upload bilingual file
        Returns updated job parts and projects
        :param file: bytes (required), formData.
        :param save_to_trans_memory: Optional[str] = "Confirmed" (optional), query.
        :param set_completed: Optional[bool] = False (optional), query.

        :param filename: Optional name for the uploaded file; defaults to field name.
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectJobPartsDto
        """

        endpoint = "/api2/v2/bilingualFiles"

        params = {
            "saveToTransMemory": save_to_trans_memory,
            "setCompleted": set_completed,
        }

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = {"file": (filename or "file", file)}
        payload = None
        content = None

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

        return ProjectJobPartsDto.model_validate(r.json())
