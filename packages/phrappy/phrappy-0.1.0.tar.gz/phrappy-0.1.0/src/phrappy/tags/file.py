from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import json

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import PageDtoUploadedFileDto, RemoteUploadedFileDto, UploadedFileDto


class FileOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def create_url_file(
        self,
        content_disposition: str,
        remote_uploaded_file_dto: RemoteUploadedFileDto | dict,
        phrase_token: Optional[str] = None,
    ) -> UploadedFileDto:
        """
        Operation id: createUrlFile
        Upload file
        Accepts multipart/form-data, application/octet-stream or application/json.
        :param content_disposition: str (required), header. must match pattern `((inline|attachment); )?filename\\*=UTF-8''(.+)`.
        :param remote_uploaded_file_dto: RemoteUploadedFileDto | dict (required), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UploadedFileDto
        """

        endpoint = "/api2/v1/files"
        if type(remote_uploaded_file_dto) is dict:
            remote_uploaded_file_dto = RemoteUploadedFileDto.model_validate(
                remote_uploaded_file_dto
            )

        params = {}

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
        content = None
        payload = remote_uploaded_file_dto

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

        return UploadedFileDto.model_validate(r.json())

    def deletes_file(
        self,
        file_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deletesFile
        Delete file

        :param file_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/files/{file_uid}"

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

    def get_file_json(
        self,
        file_uid: str,
        phrase_token: Optional[str] = None,
    ) -> UploadedFileDto:
        """
        Operation id: getFileJson
        Get file
        Get uploaded file as <b>octet-stream</b> or as <b>json</b> based on 'Accept' header
        :param file_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UploadedFileDto
        """

        endpoint = f"/api2/v1/files/{file_uid}"

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

        return UploadedFileDto.model_validate(r.json())

    def get_files(
        self,
        bigger_than: Optional[int] = None,
        created_by: Optional[int] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        types: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoUploadedFileDto:
        """
        Operation id: getFiles
        List files

        :param bigger_than: Optional[int] = None (optional), query. Size in bytes.
        :param created_by: Optional[int] = None (optional), query.
        :param name: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param types: Optional[List[str]] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoUploadedFileDto
        """

        endpoint = "/api2/v1/files"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "name": name,
            "types": types,
            "createdBy": created_by,
            "biggerThan": bigger_than,
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

        return PageDtoUploadedFileDto.model_validate(r.json())
