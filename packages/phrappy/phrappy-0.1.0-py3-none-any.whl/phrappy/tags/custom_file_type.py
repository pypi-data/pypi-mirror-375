from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    CreateCustomFileTypeDto,
    CustomFileTypeDto,
    DeleteCustomFileTypeDto,
    PageDtoCustomFileTypeDto,
    UpdateCustomFileTypeDto,
)


class CustomFileTypeOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def create_custom_file_types(
        self,
        create_custom_file_type_dto: Optional[CreateCustomFileTypeDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFileTypeDto:
        """
        Operation id: createCustomFileTypes
        Create custom file type

        :param create_custom_file_type_dto: Optional[CreateCustomFileTypeDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFileTypeDto
        """

        endpoint = "/api2/v1/customFileTypes"
        if type(create_custom_file_type_dto) is dict:
            create_custom_file_type_dto = CreateCustomFileTypeDto.model_validate(
                create_custom_file_type_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_custom_file_type_dto

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

        return CustomFileTypeDto.model_validate(r.json())

    def delete_batch_custom_file_type(
        self,
        delete_custom_file_type_dto: Optional[DeleteCustomFileTypeDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteBatchCustomFileType
        Delete multiple Custom file type

        :param delete_custom_file_type_dto: Optional[DeleteCustomFileTypeDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = "/api2/v1/customFileTypes"
        if type(delete_custom_file_type_dto) is dict:
            delete_custom_file_type_dto = DeleteCustomFileTypeDto.model_validate(
                delete_custom_file_type_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = delete_custom_file_type_dto

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

    def delete_custom_file_type(
        self,
        custom_file_type_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteCustomFileType
        Delete Custom file type

        :param custom_file_type_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/customFileTypes/{custom_file_type_uid}"

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

    def find_custom_file_type(
        self,
        file_name: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFileTypeDto:
        """
        Operation id: findCustomFileType
        Find custom file type
        If no matching custom file type is found it returns status 200 and empty body.
        :param file_name: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFileTypeDto
        """

        endpoint = "/api2/v1/customFileTypes/find"

        params = {"fileName": file_name}

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

        return CustomFileTypeDto.model_validate(r.json())

    def get_all_custom_file_type(
        self,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoCustomFileTypeDto:
        """
        Operation id: getAllCustomFileType
        Get All Custom file type

        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCustomFileTypeDto
        """

        endpoint = "/api2/v1/customFileTypes"

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

        return PageDtoCustomFileTypeDto.model_validate(r.json())

    def get_custom_file_type(
        self,
        custom_file_type_uid: str,
        phrase_token: Optional[str] = None,
    ) -> CustomFileTypeDto:
        """
        Operation id: getCustomFileType
        Get Custom file type

        :param custom_file_type_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFileTypeDto
        """

        endpoint = f"/api2/v1/customFileTypes/{custom_file_type_uid}"

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

        return CustomFileTypeDto.model_validate(r.json())

    def update_custom_file_type(
        self,
        custom_file_type_uid: str,
        update_custom_file_type_dto: Optional[UpdateCustomFileTypeDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFileTypeDto:
        """
        Operation id: updateCustomFileType
        Update Custom file type

        :param custom_file_type_uid: str (required), path.
        :param update_custom_file_type_dto: Optional[UpdateCustomFileTypeDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFileTypeDto
        """

        endpoint = f"/api2/v1/customFileTypes/{custom_file_type_uid}"
        if type(update_custom_file_type_dto) is dict:
            update_custom_file_type_dto = UpdateCustomFileTypeDto.model_validate(
                update_custom_file_type_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = update_custom_file_type_dto

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

        return CustomFileTypeDto.model_validate(r.json())
