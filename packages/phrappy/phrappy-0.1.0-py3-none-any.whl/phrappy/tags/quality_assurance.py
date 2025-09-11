from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    CreateLqaProfileDto,
    LqaProfileDetailDto,
    LqaProfileReferenceDto,
    PageDtoLqaProfileReferenceDto,
    PageDtoUserReference2,
    QualityAssuranceBatchRunDtoV3,
    QualityAssuranceChecksDtoV2,
    QualityAssuranceChecksDtoV4,
    QualityAssuranceResponseDto,
    QualityAssuranceRunDtoV3,
    QualityAssuranceSegmentsRunDtoV3,
    UpdateIgnoredChecksDto,
    UpdateIgnoredWarningsDto,
    UpdateIgnoredWarningsDto2,
    UpdateLqaProfileDto,
    UserReference,
)


class QualityAssuranceOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def add_ignored_warnings(
        self,
        job_uid: str,
        project_uid: str,
        update_ignored_warnings_dto: Optional[UpdateIgnoredWarningsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> UpdateIgnoredWarningsDto:
        """
        Operation id: addIgnoredWarnings
        Add ignored warnings

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param update_ignored_warnings_dto: Optional[UpdateIgnoredWarningsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UpdateIgnoredWarningsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/ignoredWarnings"
        if type(update_ignored_warnings_dto) is dict:
            update_ignored_warnings_dto = UpdateIgnoredWarningsDto.model_validate(
                update_ignored_warnings_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = update_ignored_warnings_dto

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

        return UpdateIgnoredWarningsDto.model_validate(r.json())

    def add_ignored_warnings_v2(
        self,
        project_uid: str,
        update_ignored_warnings_dto2: Optional[UpdateIgnoredWarningsDto2 | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> UpdateIgnoredWarningsDto2:
        """
        Operation id: addIgnoredWarningsV2
        Add ignored warnings

        :param project_uid: str (required), path.
        :param update_ignored_warnings_dto2: Optional[UpdateIgnoredWarningsDto2 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UpdateIgnoredWarningsDto2
        """

        endpoint = (
            f"/api2/v2/projects/{project_uid}/jobs/qualityAssurances/ignoredWarnings"
        )
        if type(update_ignored_warnings_dto2) is dict:
            update_ignored_warnings_dto2 = UpdateIgnoredWarningsDto2.model_validate(
                update_ignored_warnings_dto2
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = update_ignored_warnings_dto2

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

        return UpdateIgnoredWarningsDto2.model_validate(r.json())

    def create_lqa_profile(
        self,
        create_lqa_profile_dto: Optional[CreateLqaProfileDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LqaProfileDetailDto:
        """
        Operation id: createLqaProfile
        Create LQA profile

        :param create_lqa_profile_dto: Optional[CreateLqaProfileDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileDetailDto
        """

        endpoint = "/api2/v1/lqa/profiles"
        if type(create_lqa_profile_dto) is dict:
            create_lqa_profile_dto = CreateLqaProfileDto.model_validate(
                create_lqa_profile_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_lqa_profile_dto

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

        return LqaProfileDetailDto.model_validate(r.json())

    def delete_ignored_warnings(
        self,
        job_uid: str,
        project_uid: str,
        update_ignored_warnings_dto: Optional[UpdateIgnoredWarningsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteIgnoredWarnings
        Delete ignored warnings

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param update_ignored_warnings_dto: Optional[UpdateIgnoredWarningsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/ignoredWarnings"
        if type(update_ignored_warnings_dto) is dict:
            update_ignored_warnings_dto = UpdateIgnoredWarningsDto.model_validate(
                update_ignored_warnings_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = update_ignored_warnings_dto

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

    def delete_ignored_warnings_v2(
        self,
        project_uid: str,
        update_ignored_warnings_dto2: Optional[UpdateIgnoredWarningsDto2 | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteIgnoredWarningsV2
        Delete ignored warnings

        :param project_uid: str (required), path.
        :param update_ignored_warnings_dto2: Optional[UpdateIgnoredWarningsDto2 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = (
            f"/api2/v2/projects/{project_uid}/jobs/qualityAssurances/ignoredWarnings"
        )
        if type(update_ignored_warnings_dto2) is dict:
            update_ignored_warnings_dto2 = UpdateIgnoredWarningsDto2.model_validate(
                update_ignored_warnings_dto2
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = update_ignored_warnings_dto2

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

    def delete_lqa_profile(
        self,
        profile_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteLqaProfile
        Delete LQA profile

        :param profile_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/lqa/profiles/{profile_uid}"

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

    def duplicate_profile(
        self,
        profile_uid: str,
        phrase_token: Optional[str] = None,
    ) -> LqaProfileReferenceDto:
        """
        Operation id: duplicateProfile
        Duplicate LQA profile

        :param profile_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileReferenceDto
        """

        endpoint = f"/api2/v1/lqa/profiles/{profile_uid}/duplicate"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

        return LqaProfileReferenceDto.model_validate(r.json())

    def enabled_quality_checks_for_job(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceChecksDtoV2:
        """
        Operation id: enabledQualityChecksForJob
        Get QA settings for job
        Returns enabled quality assurance checks and settings for job.
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceChecksDtoV2
        """

        endpoint = (
            f"/api2/v2/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/settings"
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

        return QualityAssuranceChecksDtoV2.model_validate(r.json())

    def enabled_quality_checks_for_project(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceChecksDtoV2:
        """
        Operation id: enabledQualityChecksForProject
        Get QA settings
        Returns enabled quality assurance checks and settings.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceChecksDtoV2
        """

        endpoint = f"/api2/v2/projects/{project_uid}/jobs/qualityAssurances/settings"

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

        return QualityAssuranceChecksDtoV2.model_validate(r.json())

    def get_lqa_profile(
        self,
        profile_uid: str,
        phrase_token: Optional[str] = None,
    ) -> LqaProfileDetailDto:
        """
        Operation id: getLqaProfile
        Get LQA profile details

        :param profile_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileDetailDto
        """

        endpoint = f"/api2/v1/lqa/profiles/{profile_uid}"

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

        return LqaProfileDetailDto.model_validate(r.json())

    def get_lqa_profile_authors(
        self,
        phrase_token: Optional[str] = None,
    ) -> UserReference:
        """
        Operation id: getLqaProfileAuthors
        Get list of LQA profile authors


        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UserReference
        """

        endpoint = "/api2/v1/lqa/profiles/authors"

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

        return UserReference.model_validate(r.json())

    def get_lqa_profile_authors_v2(
        self,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 20,
        phrase_token: Optional[str] = None,
    ) -> PageDtoUserReference2:
        """
        Operation id: getLqaProfileAuthorsV2
        Get list of LQA profile authors

        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 20 (optional), query. Page size, accepts values between 1 and 50, default 20.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoUserReference2
        """

        endpoint = "/api2/v2/lqa/profiles/authors"

        params = {"pageNumber": page_number, "pageSize": page_size}

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

        return PageDtoUserReference2.model_validate(r.json())

    def get_lqa_profile_default_values(
        self,
        phrase_token: Optional[str] = None,
    ) -> LqaProfileDetailDto:
        """
        Operation id: getLqaProfileDefaultValues
        Get LQA profile default values


        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileDetailDto
        """

        endpoint = "/api2/v1/lqa/profiles/defaultValues"

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

        return LqaProfileDetailDto.model_validate(r.json())

    def get_lqa_profiles(
        self,
        created_by: Optional[str] = None,
        date_created: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[List[str]] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 20,
        sort: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoLqaProfileReferenceDto:
        """
        Operation id: getLqaProfiles
        GET list LQA profiles

        :param created_by: Optional[str] = None (optional), query. It is used for filter the list by who created the profile.
        :param date_created: Optional[str] = None (optional), query. It is used for filter the list by date created.
        :param name: Optional[str] = None (optional), query. Name of LQA profiles, it is used for filter the list by name.
        :param order: Optional[List[str]] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 20 (optional), query. Page size, accepts values between 1 and 50, default 20.
        :param sort: Optional[List[str]] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoLqaProfileReferenceDto
        """

        endpoint = "/api2/v1/lqa/profiles"

        params = {
            "name": name,
            "createdBy": created_by,
            "dateCreated": date_created,
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

        return PageDtoLqaProfileReferenceDto.model_validate(r.json())

    def get_qa_settings_for_job_part_v4(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceChecksDtoV4:
        """
        Operation id: getQaSettingsForJobPartV4
        Get QA settings for job part
        Returns enabled quality assurance checks and settings for job.
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceChecksDtoV4
        """

        endpoint = (
            f"/api2/v4/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/settings"
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

        return QualityAssuranceChecksDtoV4.model_validate(r.json())

    def get_qa_settings_for_project_v4(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceChecksDtoV4:
        """
        Operation id: getQaSettingsForProjectV4
        Get QA settings for project
        Returns enabled quality assurance checks and settings.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceChecksDtoV4
        """

        endpoint = f"/api2/v4/projects/{project_uid}/jobs/qualityAssurances/settings"

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

        return QualityAssuranceChecksDtoV4.model_validate(r.json())

    def make_default(
        self,
        profile_uid: str,
        phrase_token: Optional[str] = None,
    ) -> LqaProfileReferenceDto:
        """
        Operation id: makeDefault
        Make LQA profile default

        :param profile_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileReferenceDto
        """

        endpoint = f"/api2/v1/lqa/profiles/{profile_uid}/default"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

        return LqaProfileReferenceDto.model_validate(r.json())

    def run_qa_and_save_v4(
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

        return QualityAssuranceResponseDto.model_validate(r.json())

    def run_qa_for_job_part_v3(
        self,
        job_uid: str,
        project_uid: str,
        quality_assurance_run_dto_v3: Optional[QualityAssuranceRunDtoV3 | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForJobPartV3
        Run quality assurance
        Call "Get QA settings" endpoint to get the list of enabled QA checks
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param quality_assurance_run_dto_v3: Optional[QualityAssuranceRunDtoV3 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """

        endpoint = (
            f"/api2/v3/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/run"
        )
        if type(quality_assurance_run_dto_v3) is dict:
            quality_assurance_run_dto_v3 = QualityAssuranceRunDtoV3.model_validate(
                quality_assurance_run_dto_v3
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = quality_assurance_run_dto_v3

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

        return QualityAssuranceResponseDto.model_validate(r.json())

    def run_qa_for_job_part_v4(
        self,
        job_uid: str,
        project_uid: str,
        quality_assurance_run_dto_v3: Optional[QualityAssuranceRunDtoV3 | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForJobPartV4
        Run quality assurance
        Call "Get QA settings" endpoint to get the list of enabled QA checks
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param quality_assurance_run_dto_v3: Optional[QualityAssuranceRunDtoV3 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """

        endpoint = (
            f"/api2/v4/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/run"
        )
        if type(quality_assurance_run_dto_v3) is dict:
            quality_assurance_run_dto_v3 = QualityAssuranceRunDtoV3.model_validate(
                quality_assurance_run_dto_v3
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = quality_assurance_run_dto_v3

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

        return QualityAssuranceResponseDto.model_validate(r.json())

    def run_qa_for_job_parts_v3(
        self,
        project_uid: str,
        quality_assurance_batch_run_dto_v3: Optional[
            QualityAssuranceBatchRunDtoV3 | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForJobPartsV3
        Run quality assurance (batch)
        Call "Get QA settings" endpoint to get the list of enabled QA checks
        :param project_uid: str (required), path.
        :param quality_assurance_batch_run_dto_v3: Optional[QualityAssuranceBatchRunDtoV3 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """

        endpoint = f"/api2/v3/projects/{project_uid}/jobs/qualityAssurances/run"
        if type(quality_assurance_batch_run_dto_v3) is dict:
            quality_assurance_batch_run_dto_v3 = (
                QualityAssuranceBatchRunDtoV3.model_validate(
                    quality_assurance_batch_run_dto_v3
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = quality_assurance_batch_run_dto_v3

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

        return QualityAssuranceResponseDto.model_validate(r.json())

    def run_qa_for_job_parts_v4(
        self,
        project_uid: str,
        quality_assurance_batch_run_dto_v3: Optional[
            QualityAssuranceBatchRunDtoV3 | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForJobPartsV4
        Run quality assurance (batch)
        Call "Get QA settings" endpoint to get the list of enabled QA checks
        :param project_uid: str (required), path.
        :param quality_assurance_batch_run_dto_v3: Optional[QualityAssuranceBatchRunDtoV3 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """

        endpoint = f"/api2/v4/projects/{project_uid}/jobs/qualityAssurances/run"
        if type(quality_assurance_batch_run_dto_v3) is dict:
            quality_assurance_batch_run_dto_v3 = (
                QualityAssuranceBatchRunDtoV3.model_validate(
                    quality_assurance_batch_run_dto_v3
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = quality_assurance_batch_run_dto_v3

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

        return QualityAssuranceResponseDto.model_validate(r.json())

    def run_qa_for_segments_v3(
        self,
        project_uid: str,
        quality_assurance_segments_run_dto_v3: Optional[
            QualityAssuranceSegmentsRunDtoV3 | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForSegmentsV3
        Run quality assurance on selected segments
        By default runs only fast running checks. Source and target language of jobs have to match.
        :param project_uid: str (required), path.
        :param quality_assurance_segments_run_dto_v3: Optional[QualityAssuranceSegmentsRunDtoV3 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """

        endpoint = (
            f"/api2/v3/projects/{project_uid}/jobs/qualityAssurances/segments/run"
        )
        if type(quality_assurance_segments_run_dto_v3) is dict:
            quality_assurance_segments_run_dto_v3 = (
                QualityAssuranceSegmentsRunDtoV3.model_validate(
                    quality_assurance_segments_run_dto_v3
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = quality_assurance_segments_run_dto_v3

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

        return QualityAssuranceResponseDto.model_validate(r.json())

    def run_qa_for_segments_v4(
        self,
        project_uid: str,
        quality_assurance_segments_run_dto_v3: Optional[
            QualityAssuranceSegmentsRunDtoV3 | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForSegmentsV4
        Run quality assurance on selected segments
        By default runs only fast running checks. Source and target language of jobs have to match.
        :param project_uid: str (required), path.
        :param quality_assurance_segments_run_dto_v3: Optional[QualityAssuranceSegmentsRunDtoV3 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """

        endpoint = (
            f"/api2/v4/projects/{project_uid}/jobs/qualityAssurances/segments/run"
        )
        if type(quality_assurance_segments_run_dto_v3) is dict:
            quality_assurance_segments_run_dto_v3 = (
                QualityAssuranceSegmentsRunDtoV3.model_validate(
                    quality_assurance_segments_run_dto_v3
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = quality_assurance_segments_run_dto_v3

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

        return QualityAssuranceResponseDto.model_validate(r.json())

    def update_ignored_checks(
        self,
        job_uid: str,
        project_uid: str,
        update_ignored_checks_dto: Optional[UpdateIgnoredChecksDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: updateIgnoredChecks
        Edit ignored checks

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param update_ignored_checks_dto: Optional[UpdateIgnoredChecksDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/ignoreChecks"
        if type(update_ignored_checks_dto) is dict:
            update_ignored_checks_dto = UpdateIgnoredChecksDto.model_validate(
                update_ignored_checks_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = update_ignored_checks_dto

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

    def update_lqa_profile(
        self,
        profile_uid: str,
        update_lqa_profile_dto: Optional[UpdateLqaProfileDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LqaProfileDetailDto:
        """
        Operation id: updateLqaProfile
        Update LQA profile

        :param profile_uid: str (required), path.
        :param update_lqa_profile_dto: Optional[UpdateLqaProfileDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileDetailDto
        """

        endpoint = f"/api2/v1/lqa/profiles/{profile_uid}"
        if type(update_lqa_profile_dto) is dict:
            update_lqa_profile_dto = UpdateLqaProfileDto.model_validate(
                update_lqa_profile_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = update_lqa_profile_dto

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

        return LqaProfileDetailDto.model_validate(r.json())
