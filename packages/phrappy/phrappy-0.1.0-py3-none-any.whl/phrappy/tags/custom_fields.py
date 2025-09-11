from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    CreateCustomFieldDto,
    CreateCustomFieldInstancesDto,
    CustomFieldDeprecateDto,
    CustomFieldDto,
    CustomFieldInstanceDto,
    CustomFieldInstancesDto,
    PageDtoCustomFieldDto,
    PageDtoCustomFieldInstanceDto,
    PageDtoCustomFieldOptionDto,
    UpdateCustomFieldDto,
    UpdateCustomFieldInstanceDto,
    UpdateCustomFieldInstancesDto,
)


class CustomFieldsOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def create_custom_field(
        self,
        create_custom_field_dto: Optional[CreateCustomFieldDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldDto:
        """
        Operation id: createCustomField
        Create custom field

        :param create_custom_field_dto: Optional[CreateCustomFieldDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldDto
        """

        endpoint = "/api2/v1/customFields"
        if type(create_custom_field_dto) is dict:
            create_custom_field_dto = CreateCustomFieldDto.model_validate(
                create_custom_field_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_custom_field_dto

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

        return CustomFieldDto.model_validate(r.json())

    def create_custom_fields_job(
        self,
        job_part_uid: str,
        project_uid: str,
        create_custom_field_instances_dto: Optional[
            CreateCustomFieldInstancesDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldInstancesDto:
        """
        Operation id: createCustomFieldsJob
        Create custom field instances

        :param job_part_uid: str (required), path.
        :param project_uid: str (required), path.
        :param create_custom_field_instances_dto: Optional[CreateCustomFieldInstancesDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstancesDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_part_uid}/customFields"
        if type(create_custom_field_instances_dto) is dict:
            create_custom_field_instances_dto = (
                CreateCustomFieldInstancesDto.model_validate(
                    create_custom_field_instances_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_custom_field_instances_dto

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

        return CustomFieldInstancesDto.model_validate(r.json())

    def delete_custom_field(
        self,
        field_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteCustomField
        Delete custom field

        :param field_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/customFields/{field_uid}"

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

    def delete_custom_field_job(
        self,
        instance_uid: str,
        job_part_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteCustomFieldJob
        Delete custom field

        :param instance_uid: str (required), path.
        :param job_part_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_part_uid}/customFields/{instance_uid}"

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

    def deprecate_custom_field(
        self,
        field_uid: str,
        option_uid: str,
        custom_field_deprecate_dto: Optional[CustomFieldDeprecateDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deprecateCustomField
        Deprecate custom field option

        :param field_uid: str (required), path.
        :param option_uid: str (required), path.
        :param custom_field_deprecate_dto: Optional[CustomFieldDeprecateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/customFields/{field_uid}/options/{option_uid}/deprecate"
        if type(custom_field_deprecate_dto) is dict:
            custom_field_deprecate_dto = CustomFieldDeprecateDto.model_validate(
                custom_field_deprecate_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = custom_field_deprecate_dto

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

    def edit_custom_field_job(
        self,
        instance_uid: str,
        job_part_uid: str,
        project_uid: str,
        update_custom_field_instance_dto: Optional[
            UpdateCustomFieldInstanceDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldInstanceDto:
        """
        Operation id: editCustomFieldJob
        Edit custom field

        :param instance_uid: str (required), path.
        :param job_part_uid: str (required), path.
        :param project_uid: str (required), path.
        :param update_custom_field_instance_dto: Optional[UpdateCustomFieldInstanceDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstanceDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_part_uid}/customFields/{instance_uid}"
        if type(update_custom_field_instance_dto) is dict:
            update_custom_field_instance_dto = (
                UpdateCustomFieldInstanceDto.model_validate(
                    update_custom_field_instance_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = update_custom_field_instance_dto

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

        return CustomFieldInstanceDto.model_validate(r.json())

    def edit_custom_fields_job(
        self,
        job_part_uid: str,
        project_uid: str,
        update_custom_field_instances_dto: Optional[
            UpdateCustomFieldInstancesDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldInstancesDto:
        """
        Operation id: editCustomFieldsJob
        Edit custom fields (batch)

        :param job_part_uid: str (required), path.
        :param project_uid: str (required), path.
        :param update_custom_field_instances_dto: Optional[UpdateCustomFieldInstancesDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstancesDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_part_uid}/customFields"
        if type(update_custom_field_instances_dto) is dict:
            update_custom_field_instances_dto = (
                UpdateCustomFieldInstancesDto.model_validate(
                    update_custom_field_instances_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = update_custom_field_instances_dto

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

        return CustomFieldInstancesDto.model_validate(r.json())

    def get_custom_field(
        self,
        field_uid: str,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldDto:
        """
        Operation id: getCustomField
        Get custom field

        :param field_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldDto
        """

        endpoint = f"/api2/v1/customFields/{field_uid}"

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

        return CustomFieldDto.model_validate(r.json())

    def get_custom_field_job(
        self,
        instance_uid: str,
        job_part_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldInstanceDto:
        """
        Operation id: getCustomFieldJob
        Get custom field

        :param instance_uid: str (required), path.
        :param job_part_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstanceDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_part_uid}/customFields/{instance_uid}"

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

        return CustomFieldInstanceDto.model_validate(r.json())

    def get_custom_field_list(
        self,
        allowed_entities: Optional[List[str]] = None,
        created_by: Optional[List[str]] = None,
        modified_by: Optional[List[str]] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        required: Optional[bool] = None,
        sort_field: Optional[str] = None,
        sort_trend: Optional[str] = "ASC",
        types: Optional[List[str]] = None,
        uids: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoCustomFieldDto:
        """
        Operation id: getCustomFieldList
        Lists custom fields

        :param allowed_entities: Optional[List[str]] = None (optional), query. Filter by custom field allowed entities.
        :param created_by: Optional[List[str]] = None (optional), query. Filter by custom field creators UIDs.
        :param modified_by: Optional[List[str]] = None (optional), query. Filter by custom field updaters UIDs.
        :param name: Optional[str] = None (optional), query. Filter by custom field name.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param required: Optional[bool] = None (optional), query. Filter by custom field required parameter.
        :param sort_field: Optional[str] = None (optional), query. Sort by this field.
        :param sort_trend: Optional[str] = "ASC" (optional), query. Sort direction.
        :param types: Optional[List[str]] = None (optional), query. Filter by custom field types.
        :param uids: Optional[List[str]] = None (optional), query. Filter by custom field UIDs.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCustomFieldDto
        """

        endpoint = "/api2/v1/customFields"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "name": name,
            "allowedEntities": allowed_entities,
            "types": types,
            "createdBy": created_by,
            "modifiedBy": modified_by,
            "uids": uids,
            "required": required,
            "sortField": sort_field,
            "sortTrend": sort_trend,
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

        return PageDtoCustomFieldDto.model_validate(r.json())

    def get_custom_field_option_list(
        self,
        field_uid: str,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort_field: Optional[str] = None,
        sort_trend: Optional[str] = "ASC",
        phrase_token: Optional[str] = None,
    ) -> PageDtoCustomFieldOptionDto:
        """
        Operation id: getCustomFieldOptionList
        Lists options of custom field

        :param field_uid: str (required), path.
        :param name: Optional[str] = None (optional), query. Filter by option name.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort_field: Optional[str] = None (optional), query. Sort by this field.
        :param sort_trend: Optional[str] = "ASC" (optional), query. Sort direction.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCustomFieldOptionDto
        """

        endpoint = f"/api2/v1/customFields/{field_uid}/options"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "name": name,
            "sortField": sort_field,
            "sortTrend": sort_trend,
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

        return PageDtoCustomFieldOptionDto.model_validate(r.json())

    def get_custom_fields_job(
        self,
        job_part_uid: str,
        project_uid: str,
        created_by: Optional[List[str]] = None,
        modified_by: Optional[List[str]] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 20,
        sort_field: Optional[str] = None,
        sort_trend: Optional[str] = "ASC",
        phrase_token: Optional[str] = None,
    ) -> PageDtoCustomFieldInstanceDto:
        """
        Operation id: getCustomFieldsJob
        Get custom fields

        :param job_part_uid: str (required), path.
        :param project_uid: str (required), path.
        :param created_by: Optional[List[str]] = None (optional), query. Filter creators UIDs.
        :param modified_by: Optional[List[str]] = None (optional), query. Filter updaters UIDs.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 20 (optional), query. Page size, accepts values between 1 and 50, default 20.
        :param sort_field: Optional[str] = None (optional), query. Sort by this field.
        :param sort_trend: Optional[str] = "ASC" (optional), query. Sort direction.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCustomFieldInstanceDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_part_uid}/customFields"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "createdBy": created_by,
            "modifiedBy": modified_by,
            "sortField": sort_field,
            "sortTrend": sort_trend,
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

        return PageDtoCustomFieldInstanceDto.model_validate(r.json())

    def update_custom_field(
        self,
        field_uid: str,
        update_custom_field_dto: Optional[UpdateCustomFieldDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldDto:
        """
        Operation id: updateCustomField
        Edit custom field

        :param field_uid: str (required), path.
        :param update_custom_field_dto: Optional[UpdateCustomFieldDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldDto
        """

        endpoint = f"/api2/v1/customFields/{field_uid}"
        if type(update_custom_field_dto) is dict:
            update_custom_field_dto = UpdateCustomFieldDto.model_validate(
                update_custom_field_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = update_custom_field_dto

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

        return CustomFieldDto.model_validate(r.json())
