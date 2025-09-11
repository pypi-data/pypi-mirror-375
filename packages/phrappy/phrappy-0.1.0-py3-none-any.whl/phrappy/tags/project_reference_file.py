from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    ProjectReferenceFilesRequestDto,
    ReferenceFilePageDto,
    ReferenceFilesDto,
    UserReferencesDto,
)


class ProjectReferenceFileOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def batch_delete_reference_files(
        self,
        project_uid: str,
        project_reference_files_request_dto: Optional[
            ProjectReferenceFilesRequestDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: batchDeleteReferenceFiles
        Delete project reference files (batch)

        :param project_uid: str (required), path.
        :param project_reference_files_request_dto: Optional[ProjectReferenceFilesRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/references"
        if type(project_reference_files_request_dto) is dict:
            project_reference_files_request_dto = (
                ProjectReferenceFilesRequestDto.model_validate(
                    project_reference_files_request_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = project_reference_files_request_dto

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

    def batch_download_reference_files(
        self,
        project_uid: str,
        project_reference_files_request_dto: Optional[
            ProjectReferenceFilesRequestDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: batchDownloadReferenceFiles
        Download project reference files (batch)

        :param project_uid: str (required), path.
        :param project_reference_files_request_dto: Optional[ProjectReferenceFilesRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/projects/{project_uid}/references/download"
        if type(project_reference_files_request_dto) is dict:
            project_reference_files_request_dto = (
                ProjectReferenceFilesRequestDto.model_validate(
                    project_reference_files_request_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = project_reference_files_request_dto

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

    def create_reference_files(
        self,
        file: bytes,
        project_uid: str,
        filename: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> ReferenceFilesDto:
        """
        Operation id: createReferenceFiles
        Create project reference files

        The `json` request part allows sending additional data as JSON,
        such as a text note that will be used for all the given reference files.
        In case no `file` parts are sent, only 1 reference is created with the given note.
        Either at least one file must be sent or the note must be specified.
        Example:

        ```
        {
            "note": "Sample text"
        }
        ```

        :param file: bytes (required), formData.
        :param project_uid: str (required), path.

        :param filename: Optional name for the uploaded file; defaults to field name.
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ReferenceFilesDto
        """

        endpoint = f"/api2/v2/projects/{project_uid}/references"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = {"file": (filename or "file", file)}
        payload = None
        content = None

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

        return ReferenceFilesDto.model_validate(r.json())

    def download_reference(
        self,
        project_uid: str,
        reference_file_id: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: downloadReference
        Download project reference file

        :param project_uid: str (required), path.
        :param reference_file_id: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/projects/{project_uid}/references/{reference_file_id}"

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

    def list_reference_file_creators(
        self,
        project_uid: str,
        user_name: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> UserReferencesDto:
        """
        Operation id: listReferenceFileCreators
        List project reference file creators
        The result is not paged and returns up to 50 users.
                        If the requested user is not included, the search can be narrowed down with the `userName` parameter.

        :param project_uid: str (required), path.
        :param user_name: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UserReferencesDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/references/creators"

        params = {"userName": user_name}

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

        return UserReferencesDto.model_validate(r.json())

    def list_reference_files(
        self,
        project_uid: str,
        created_by: Optional[str] = None,
        date_created_since: Optional[str] = None,
        filename: Optional[str] = None,
        order: Optional[str] = "DESC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "DATE_CREATED",
        phrase_token: Optional[str] = None,
    ) -> ReferenceFilePageDto:
        """
        Operation id: listReferenceFiles
        List project reference files

        :param project_uid: str (required), path.
        :param created_by: Optional[str] = None (optional), query. UID of user.
        :param date_created_since: Optional[str] = None (optional), query. date time in ISO 8601 UTC format.
        :param filename: Optional[str] = None (optional), query.
        :param order: Optional[str] = "DESC" (optional), query.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query.
        :param sort: Optional[str] = "DATE_CREATED" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ReferenceFilePageDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/references"

        params = {
            "filename": filename,
            "dateCreatedSince": date_created_since,
            "createdBy": created_by,
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

        return ReferenceFilePageDto.model_validate(r.json())
