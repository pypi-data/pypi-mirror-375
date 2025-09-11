from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import json

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    AsyncFileOpResponseDto,
    ConnectorAsyncTaskStatesDto,
    ConnectorDto,
    ConnectorListDto,
    FileListDto,
    GetFileRequestParamsDto,
    InputStreamLength,
    UploadFileV2Meta,
    UploadResultDto,
)


class ConnectorOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def get_connector(
        self,
        connector_id: str,
        phrase_token: Optional[str] = None,
    ) -> ConnectorDto:
        """
        Operation id: getConnector
        Get a connector

        :param connector_id: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConnectorDto
        """

        endpoint = f"/api2/v1/connectors/{connector_id}"

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

        return ConnectorDto.model_validate(r.json())

    def get_connector_async_task_states(
        self,
        project_uid: str,
        date_created_from: Optional[str] = None,
        date_created_to: Optional[str] = None,
        date_processed_from: Optional[str] = None,
        date_processed_to: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 100,
        task_processing_type: Optional[List[str]] = None,
        task_type: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> ConnectorAsyncTaskStatesDto:
        """
        Operation id: getConnectorAsyncTaskStates
        Get Connector async task states.

        :param project_uid: str (required), query. Filter by projectUid.
        :param date_created_from: Optional[str] = None (optional), query. Date range from, based on dateCreated, default current time minus 24h.
        :param date_created_to: Optional[str] = None (optional), query. Date range to, based on dateCreated, default current time plus 1h.
        :param date_processed_from: Optional[str] = None (optional), query. Date range from, based on dateProcessed.
        :param date_processed_to: Optional[str] = None (optional), query. Date range to, based on dateProcessed.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 100 (optional), query. Page size, accepts values between 1 and 1000, default 50.
        :param task_processing_type: Optional[List[str]] = None (optional), query.
        :param task_type: Optional[List[str]] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConnectorAsyncTaskStatesDto
        """

        endpoint = "/api2/v1/connectorAsyncTasks"

        params = {
            "projectUid": project_uid,
            "taskType": task_type,
            "taskProcessingType": task_processing_type,
            "dateCreatedFrom": date_created_from,
            "dateCreatedTo": date_created_to,
            "pageNumber": page_number,
            "pageSize": page_size,
            "dateProcessedFrom": date_processed_from,
            "dateProcessedTo": date_processed_to,
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

        return ConnectorAsyncTaskStatesDto.model_validate(r.json())

    def get_connector_list(
        self,
        type: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> ConnectorListDto:
        """
        Operation id: getConnectorList
        List connectors

        :param type: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConnectorListDto
        """

        endpoint = "/api2/v1/connectors"

        params = {"type": type}

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

        return ConnectorListDto.model_validate(r.json())

    def get_file_for_connector(
        self,
        connector_id: str,
        file: str,
        folder: str,
        phrase_token: Optional[str] = None,
    ) -> InputStreamLength:
        """
        Operation id: getFileForConnector
        Download file
        Download a file from a subfolder of the selected connector
        :param connector_id: str (required), path.
        :param file: str (required), path.
        :param folder: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: InputStreamLength
        """

        endpoint = f"/api2/v1/connectors/{connector_id}/folders/{folder}/files/{file}"

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

        return InputStreamLength.model_validate(r.json())

    def get_file_for_connector_v2(
        self,
        connector_id: str,
        file: str,
        folder: str,
        get_file_request_params_dto: Optional[GetFileRequestParamsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AsyncFileOpResponseDto:
        """
        Operation id: getFileForConnectorV2
        Download file (async)

        Create an asynchronous request to download a file from a (sub)folder of the selected connector.
        After a callback with successful response is received, prepared file can be downloaded by [Download prepared file](#operation/getPreparedFile)
        or [Create job from connector asynchronous download task](#operation/createJobFromAsyncDownloadTask).

        :param connector_id: str (required), path.
        :param file: str (required), path.
        :param folder: str (required), path.
        :param get_file_request_params_dto: Optional[GetFileRequestParamsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncFileOpResponseDto
        """

        endpoint = f"/api2/v2/connectors/{connector_id}/folders/{folder}/files/{file}"
        if type(get_file_request_params_dto) is dict:
            get_file_request_params_dto = GetFileRequestParamsDto.model_validate(
                get_file_request_params_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = get_file_request_params_dto

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

        return AsyncFileOpResponseDto.model_validate(r.json())

    def get_folder(
        self,
        connector_id: str,
        folder: str,
        direction: Optional[str] = "ASCENDING",
        file_type: Optional[str] = "ALL",
        project_uid: Optional[str] = None,
        sort: Optional[str] = "NAME",
        source_locale: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> FileListDto:
        """
        Operation id: getFolder
        List files in a subfolder
        List files in a subfolder of the selected connector
        :param connector_id: str (required), path.
        :param folder: str (required), path.
        :param direction: Optional[str] = "ASCENDING" (optional), query.
        :param file_type: Optional[str] = "ALL" (optional), query.
        :param project_uid: Optional[str] = None (optional), query.
        :param sort: Optional[str] = "NAME" (optional), query.
        :param source_locale: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileListDto
        """

        endpoint = f"/api2/v1/connectors/{connector_id}/folders/{folder}"

        params = {
            "projectUid": project_uid,
            "sourceLocale": source_locale,
            "fileType": file_type,
            "sort": sort,
            "direction": direction,
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

        return FileListDto.model_validate(r.json())

    def get_prepared_file(
        self,
        connector_id: str,
        file: str,
        folder: str,
        task_id: str,
        phrase_token: Optional[str] = None,
    ) -> InputStreamLength:
        """
        Operation id: getPreparedFile
        Download prepared file
        Download the file by referencing successfully finished async download request [Connector - Download file (async)](#operation/getFile_1).
        :param connector_id: str (required), path.
        :param file: str (required), path.
        :param folder: str (required), path.
        :param task_id: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: InputStreamLength
        """

        endpoint = f"/api2/v2/connectors/{connector_id}/folders/{folder}/files/{file}/tasks/{task_id}"

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

        return InputStreamLength.model_validate(r.json())

    def get_root_folder(
        self,
        connector_id: str,
        direction: Optional[str] = "ASCENDING",
        file_type: Optional[str] = "ALL",
        project_uid: Optional[str] = None,
        sort: Optional[str] = "NAME",
        source_locale: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> FileListDto:
        """
        Operation id: getRootFolder
        List files in root
        List files in a root folder of the selected connector
        :param connector_id: str (required), path.
        :param direction: Optional[str] = "ASCENDING" (optional), query.
        :param file_type: Optional[str] = "ALL" (optional), query.
        :param project_uid: Optional[str] = None (optional), query.
        :param sort: Optional[str] = "NAME" (optional), query.
        :param source_locale: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileListDto
        """

        endpoint = f"/api2/v1/connectors/{connector_id}/folders"

        params = {
            "projectUid": project_uid,
            "sourceLocale": source_locale,
            "fileType": file_type,
            "sort": sort,
            "direction": direction,
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

        return FileListDto.model_validate(r.json())

    def upload_file(
        self,
        connector_id: str,
        file: bytes,
        folder: str,
        content_type: str = "multipart/form-data",
        filename: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> UploadResultDto:
        """
        Operation id: uploadFile
        Upload a file to a subfolder of the selected connector
        Upload a file to a subfolder of the selected connector
        :param connector_id: str (required), path.
        :param file: bytes (required), formData.
        :param folder: str (required), path.
        :param content_type: str = "multipart/form-data" (required), header.

        :param filename: Optional name for the uploaded file; defaults to field name.
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UploadResultDto
        """

        endpoint = f"/api2/v1/connectors/{connector_id}/folders/{folder}"

        params = {}

        headers = {
            "Content-Type": (
                content_type.model_dump_json()
                if hasattr(content_type, "model_dump_json")
                else (
                    json.dumps(content_type)
                    if False and not isinstance(content_type, str)
                    else str(content_type)
                )
            )
        }
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

        return UploadResultDto.model_validate(r.json())

    def upload_file_v2(
        self,
        memsource: UploadFileV2Meta | dict,
        connector_id: str,
        file: bytes,
        file_name: str,
        folder: str,
        content_type: str = "multipart/form-data",
        mime_type: Optional[str] = None,
        filename: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> AsyncFileOpResponseDto:
        """
        Operation id: uploadFileV2
        Upload file (async)
        Upload a file to a subfolder of the selected connector
        :param memsource: UploadFileV2Meta | dict (required), header.
        :param connector_id: str (required), path.
        :param file: bytes (required), formData.
        :param file_name: str (required), path.
        :param folder: str (required), path.
        :param content_type: str = "multipart/form-data" (required), header.
        :param mime_type: Optional[str] = None (optional), query. Mime type of the file to upload.

        :param filename: Optional name for the uploaded file; defaults to field name.
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncFileOpResponseDto
        """

        endpoint = f"/api2/v2/connectors/{connector_id}/folders/{folder}/files/{file_name}/upload"
        if type(memsource) is dict:
            memsource = UploadFileV2Meta.model_validate(memsource)

        params = {"mimeType": mime_type}

        headers = {
            "Memsource": (
                memsource.model_dump_json()
                if hasattr(memsource, "model_dump_json")
                else (
                    json.dumps(memsource)
                    if True and not isinstance(memsource, str)
                    else str(memsource)
                )
            ),
            "Content-Type": (
                content_type.model_dump_json()
                if hasattr(content_type, "model_dump_json")
                else (
                    json.dumps(content_type)
                    if False and not isinstance(content_type, str)
                    else str(content_type)
                )
            ),
        }
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

        return AsyncFileOpResponseDto.model_validate(r.json())
