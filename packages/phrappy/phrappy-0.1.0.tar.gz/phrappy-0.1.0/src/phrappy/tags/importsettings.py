from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    ImportSettingsCreateDto,
    ImportSettingsDto,
    ImportSettingsEditDto,
    PageDtoImportSettingsReference,
)


class ImportsettingsOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def create_import_settings(
        self,
        import_settings_create_dto: Optional[ImportSettingsCreateDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ImportSettingsDto:
        """
        Operation id: createImportSettings
        Create import settings
        Pre-defined import settings is handy for [Create Job](#operation/createJob).
                          See [supported file types](https://wiki.memsource.com/wiki/API_File_Type_List)
        :param import_settings_create_dto: Optional[ImportSettingsCreateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportSettingsDto
        """

        endpoint = "/api2/v1/importSettings"
        if type(import_settings_create_dto) is dict:
            import_settings_create_dto = ImportSettingsCreateDto.model_validate(
                import_settings_create_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = import_settings_create_dto

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

        return ImportSettingsDto.model_validate(r.json())

    def delete_import_settings(
        self,
        uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteImportSettings
        Delete import settings

        :param uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/importSettings/{uid}"

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

    def edit_default_import_settings(
        self,
        import_settings_edit_dto: Optional[ImportSettingsEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ImportSettingsDto:
        """
        Operation id: editDefaultImportSettings
        Edit organization's default import settings

        :param import_settings_edit_dto: Optional[ImportSettingsEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportSettingsDto
        """

        endpoint = "/api2/v1/importSettings/default"
        if type(import_settings_edit_dto) is dict:
            import_settings_edit_dto = ImportSettingsEditDto.model_validate(
                import_settings_edit_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = import_settings_edit_dto

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

        return ImportSettingsDto.model_validate(r.json())

    def edit_import_settings(
        self,
        import_settings_edit_dto: Optional[ImportSettingsEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ImportSettingsDto:
        """
        Operation id: editImportSettings
        Edit import settings

        :param import_settings_edit_dto: Optional[ImportSettingsEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportSettingsDto
        """

        endpoint = "/api2/v1/importSettings"
        if type(import_settings_edit_dto) is dict:
            import_settings_edit_dto = ImportSettingsEditDto.model_validate(
                import_settings_edit_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = import_settings_edit_dto

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

        return ImportSettingsDto.model_validate(r.json())

    def get_import_settings_by_uid(
        self,
        uid: str,
        phrase_token: Optional[str] = None,
    ) -> ImportSettingsDto:
        """
        Operation id: getImportSettingsByUid
        Get import settings

        :param uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportSettingsDto
        """

        endpoint = f"/api2/v1/importSettings/{uid}"

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

        return ImportSettingsDto.model_validate(r.json())

    def get_import_settings_default(
        self,
        phrase_token: Optional[str] = None,
    ) -> ImportSettingsDto:
        """
        Operation id: getImportSettingsDefault
        Get organization's default import settings


        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportSettingsDto
        """

        endpoint = "/api2/v1/importSettings/default"

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

        return ImportSettingsDto.model_validate(r.json())

    def list_import_settings(
        self,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoImportSettingsReference:
        """
        Operation id: listImportSettings
        List import settings

        :param name: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoImportSettingsReference
        """

        endpoint = "/api2/v1/importSettings"

        params = {"name": name, "pageNumber": page_number, "pageSize": page_size}

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

        return PageDtoImportSettingsReference.model_validate(r.json())
