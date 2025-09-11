from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import json

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    AddTargetLangDto,
    AddWorkflowStepsDto,
    AnalyseSettingsDto,
    AssignVendorDto,
    AssignableTemplatesDto,
    AsyncRequestWrapperV2Dto,
    CloneProjectDto,
    CreateCustomFieldInstancesDto,
    CreateProjectFromTemplateAsyncV2Dto,
    CreateProjectFromTemplateV2Dto,
    CreateProjectV3Dto,
    CustomFieldInstanceDto,
    CustomFieldInstancesDto,
    EditProjectMTSettPerLangListDto,
    EditProjectMTSettingsDto,
    EditProjectSecuritySettingsDtoV2,
    EditProjectV2Dto,
    EditProjectV3Dto,
    EditQASettingsDtoV2,
    EnabledQualityChecksDto,
    FileImportSettingsCreateDto,
    FileImportSettingsDto,
    FileNamingSettingsDto,
    FinancialSettingsDto2,
    JobPartReferences,
    JobPartsDto,
    JobPreviewPackageDto,
    LqaSettingsDto,
    MTSettingsPerLanguageListDto,
    PageDtoAbstractProjectDto,
    PageDtoAnalyseReference,
    PageDtoCustomFieldInstanceDto,
    PageDtoProjectReference,
    PageDtoProviderReference,
    PageDtoQuoteDto,
    PageDtoTermBaseDto,
    PageDtoTransMemoryDto,
    PatchProjectDto,
    PreTranslateSettingsV4Dto,
    ProjectDto,
    ProjectDtoV2,
    ProjectSecuritySettingsDtoV2,
    ProjectTermBaseListDto,
    ProjectTransMemoryListDtoV3,
    ProjectWorkflowStepListDtoV2,
    ProviderListDtoV2,
    QASettingsDtoV2,
    SearchResponseListTmDto,
    SearchTMRequestDto,
    SetFinancialSettingsDto,
    SetProjectStatusDto,
    SetProjectTransMemoriesV3Dto,
    SetTermBaseDto,
    UpdateCustomFieldInstanceDto,
    UpdateCustomFieldInstancesDto,
)


class ProjectOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def add_target_language_to_project(
        self,
        project_uid: str,
        add_target_lang_dto: Optional[AddTargetLangDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: addTargetLanguageToProject
        Add target languages
        Add target languages to project
        :param project_uid: str (required), path.
        :param add_target_lang_dto: Optional[AddTargetLangDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/targetLangs"
        if type(add_target_lang_dto) is dict:
            add_target_lang_dto = AddTargetLangDto.model_validate(add_target_lang_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = add_target_lang_dto

        await self.client.make_request(
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

    async def add_workflow_steps(
        self,
        project_uid: str,
        add_workflow_steps_dto: Optional[AddWorkflowStepsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: addWorkflowSteps
        Add workflow steps

        :param project_uid: str (required), path.
        :param add_workflow_steps_dto: Optional[AddWorkflowStepsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/workflowSteps"
        if type(add_workflow_steps_dto) is dict:
            add_workflow_steps_dto = AddWorkflowStepsDto.model_validate(
                add_workflow_steps_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = add_workflow_steps_dto

        await self.client.make_request(
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

    async def assign_linguists_from_template(
        self,
        project_uid: str,
        template_uid: str,
        phrase_token: Optional[str] = None,
    ) -> JobPartsDto:
        """
        Operation id: assignLinguistsFromTemplate
        Assigns providers from template

        Jobs that will be skipped:
        * jobs in Assigned status
        * jobs that already has assignments
        * jobs that are not ready yet (import or update source is in progress)

        :param project_uid: str (required), path.
        :param template_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/applyTemplate/{template_uid}/assignProviders"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

        return JobPartsDto.model_validate(r.json())

    async def assign_linguists_from_template_to_job_parts(
        self,
        project_uid: str,
        template_uid: str,
        job_part_references: Optional[JobPartReferences | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> JobPartsDto:
        """
        Operation id: assignLinguistsFromTemplateToJobParts
        Assigns providers from template (specific jobs)

        Jobs that will be skipped:
        * jobs in Assigned status
        * jobs that already has assignments

        :param project_uid: str (required), path.
        :param template_uid: str (required), path.
        :param job_part_references: Optional[JobPartReferences | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/applyTemplate/{template_uid}/assignProviders/forJobParts"
        if type(job_part_references) is dict:
            job_part_references = JobPartReferences.model_validate(job_part_references)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_references

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

        return JobPartsDto.model_validate(r.json())

    async def assign_vendor_to_project(
        self,
        project_uid: str,
        assign_vendor_dto: Optional[AssignVendorDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: assignVendorToProject
        Assign vendor

        To unassign Vendor from Project, use empty body:
        ```
        {}
        ```

        :param project_uid: str (required), path.
        :param assign_vendor_dto: Optional[AssignVendorDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/assignVendor"
        if type(assign_vendor_dto) is dict:
            assign_vendor_dto = AssignVendorDto.model_validate(assign_vendor_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = assign_vendor_dto

        await self.client.make_request(
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

    async def assignable_templates(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> AssignableTemplatesDto:
        """
        Operation id: assignableTemplates
        List assignable templates

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssignableTemplatesDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/assignableTemplates"

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

        return AssignableTemplatesDto.model_validate(r.json())

    async def clone_project(
        self,
        project_uid: str,
        clone_project_dto: Optional[CloneProjectDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectDto:
        """
        Operation id: cloneProject
        Clone project

        :param project_uid: str (required), path.
        :param clone_project_dto: Optional[CloneProjectDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/clone"
        if type(clone_project_dto) is dict:
            clone_project_dto = CloneProjectDto.model_validate(clone_project_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = clone_project_dto

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

        _u = ProjectDto.model_validate(r.json())
        return getattr(_u, "root", _u)

    async def create_custom_fields_on_project(
        self,
        project_uid: str,
        create_custom_field_instances_dto: Optional[
            CreateCustomFieldInstancesDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldInstancesDto:
        """
        Operation id: createCustomFieldsOnProject
        Create custom field instances

        :param project_uid: str (required), path.
        :param create_custom_field_instances_dto: Optional[CreateCustomFieldInstancesDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstancesDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/customFields"
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

        return CustomFieldInstancesDto.model_validate(r.json())

    async def create_project_from_template_v2(
        self,
        template_uid: str,
        create_project_from_template_v2_dto: Optional[
            CreateProjectFromTemplateV2Dto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectDtoV2:
        """
        Operation id: createProjectFromTemplateV2
        Create project from template

        :param template_uid: str (required), path.
        :param create_project_from_template_v2_dto: Optional[CreateProjectFromTemplateV2Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectDtoV2
        """

        endpoint = f"/api2/v2/projects/applyTemplate/{template_uid}"
        if type(create_project_from_template_v2_dto) is dict:
            create_project_from_template_v2_dto = (
                CreateProjectFromTemplateV2Dto.model_validate(
                    create_project_from_template_v2_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_project_from_template_v2_dto

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

        try:
            _u = ProjectDtoV2.model_validate(r.json())
        except Exception:
            data = r.json()
            if isinstance(data, dict):
                disc = "userRole"
                if disc not in data or data.get(disc) in (None, ""):
                    data[disc] = "PROJECT_MANAGER"
                _u = ProjectDtoV2.model_validate(data)
            else:
                raise
        return getattr(_u, "root", _u)

    async def create_project_from_template_v2_async(
        self,
        template_uid: str,
        create_project_from_template_async_v2_dto: Optional[
            CreateProjectFromTemplateAsyncV2Dto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> AsyncRequestWrapperV2Dto:
        """
        Operation id: createProjectFromTemplateV2Async
        Create project from template (async)

        :param template_uid: str (required), path.
        :param create_project_from_template_async_v2_dto: Optional[CreateProjectFromTemplateAsyncV2Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperV2Dto
        """

        endpoint = f"/api2/v2/projects/applyTemplate/async/{template_uid}"
        if type(create_project_from_template_async_v2_dto) is dict:
            create_project_from_template_async_v2_dto = (
                CreateProjectFromTemplateAsyncV2Dto.model_validate(
                    create_project_from_template_async_v2_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_project_from_template_async_v2_dto

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

        return AsyncRequestWrapperV2Dto.model_validate(r.json())

    async def create_project_v3(
        self,
        create_project_v3_dto: Optional[CreateProjectV3Dto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectDtoV2:
        """
        Operation id: createProjectV3
        Create project

        :param create_project_v3_dto: Optional[CreateProjectV3Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectDtoV2
        """

        endpoint = "/api2/v3/projects"
        if type(create_project_v3_dto) is dict:
            create_project_v3_dto = CreateProjectV3Dto.model_validate(
                create_project_v3_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_project_v3_dto

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

        try:
            _u = ProjectDtoV2.model_validate(r.json())
        except Exception:
            data = r.json()
            if isinstance(data, dict):
                disc = "userRole"
                if disc not in data or data.get(disc) in (None, ""):
                    data[disc] = "PROJECT_MANAGER"
                _u = ProjectDtoV2.model_validate(data)
            else:
                raise
        return getattr(_u, "root", _u)

    async def delete_custom_field_of_project(
        self,
        field_instance_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteCustomFieldOfProject
        Delete custom field of project

        :param field_instance_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/customFields/{field_instance_uid}"

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

    async def delete_project(
        self,
        project_uid: str,
        purge: Optional[bool] = False,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteProject
        Delete project

        :param project_uid: str (required), path.
        :param purge: Optional[bool] = False (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}"

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

    async def edit_custom_field_on_project(
        self,
        field_instance_uid: str,
        project_uid: str,
        update_custom_field_instance_dto: Optional[
            UpdateCustomFieldInstanceDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldInstanceDto:
        """
        Operation id: editCustomFieldOnProject
        Edit custom field of project

        :param field_instance_uid: str (required), path.
        :param project_uid: str (required), path.
        :param update_custom_field_instance_dto: Optional[UpdateCustomFieldInstanceDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstanceDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/customFields/{field_instance_uid}"
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

        return CustomFieldInstanceDto.model_validate(r.json())

    async def edit_custom_fields_on_project(
        self,
        project_uid: str,
        update_custom_field_instances_dto: Optional[
            UpdateCustomFieldInstancesDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldInstancesDto:
        """
        Operation id: editCustomFieldsOnProject
        Edit custom fields of the project (batch)

        :param project_uid: str (required), path.
        :param update_custom_field_instances_dto: Optional[UpdateCustomFieldInstancesDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstancesDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/customFields"
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

        return CustomFieldInstancesDto.model_validate(r.json())

    async def edit_import_settings_of_project(
        self,
        project_uid: str,
        file_import_settings_create_dto: Optional[
            FileImportSettingsCreateDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> FileImportSettingsDto:
        """
        Operation id: editImportSettingsOfProject
        Edit project import settings

        :param project_uid: str (required), path.
        :param file_import_settings_create_dto: Optional[FileImportSettingsCreateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileImportSettingsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/importSettings"
        if type(file_import_settings_create_dto) is dict:
            file_import_settings_create_dto = (
                FileImportSettingsCreateDto.model_validate(
                    file_import_settings_create_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = file_import_settings_create_dto

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

        return FileImportSettingsDto.model_validate(r.json())

    async def edit_project_access_settings_v2(
        self,
        project_uid: str,
        edit_project_security_settings_dto_v2: Optional[
            EditProjectSecuritySettingsDtoV2 | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectSecuritySettingsDtoV2:
        """
        Operation id: editProjectAccessSettingsV2
        Edit access and security settings

        :param project_uid: str (required), path.
        :param edit_project_security_settings_dto_v2: Optional[EditProjectSecuritySettingsDtoV2 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectSecuritySettingsDtoV2
        """

        endpoint = f"/api2/v2/projects/{project_uid}/accessSettings"
        if type(edit_project_security_settings_dto_v2) is dict:
            edit_project_security_settings_dto_v2 = (
                EditProjectSecuritySettingsDtoV2.model_validate(
                    edit_project_security_settings_dto_v2
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = edit_project_security_settings_dto_v2

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

        return ProjectSecuritySettingsDtoV2.model_validate(r.json())

    async def edit_project_v2(
        self,
        project_uid: str,
        edit_project_v2_dto: Optional[EditProjectV2Dto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectDtoV2:
        """
        Operation id: editProjectV2
        Edit project

        :param project_uid: str (required), path.
        :param edit_project_v2_dto: Optional[EditProjectV2Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectDtoV2
        """

        endpoint = f"/api2/v2/projects/{project_uid}"
        if type(edit_project_v2_dto) is dict:
            edit_project_v2_dto = EditProjectV2Dto.model_validate(edit_project_v2_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = edit_project_v2_dto

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

        try:
            _u = ProjectDtoV2.model_validate(r.json())
        except Exception:
            data = r.json()
            if isinstance(data, dict):
                disc = "userRole"
                if disc not in data or data.get(disc) in (None, ""):
                    data[disc] = "PROJECT_MANAGER"
                _u = ProjectDtoV2.model_validate(data)
            else:
                raise
        return getattr(_u, "root", _u)

    async def edit_project_v3(
        self,
        project_uid: str,
        edit_project_v3_dto: Optional[EditProjectV3Dto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectDtoV2:
        """
        Operation id: editProjectV3
        Edit project

        :param project_uid: str (required), path.
        :param edit_project_v3_dto: Optional[EditProjectV3Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectDtoV2
        """

        endpoint = f"/api2/v3/projects/{project_uid}"
        if type(edit_project_v3_dto) is dict:
            edit_project_v3_dto = EditProjectV3Dto.model_validate(edit_project_v3_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = edit_project_v3_dto

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

        try:
            _u = ProjectDtoV2.model_validate(r.json())
        except Exception:
            data = r.json()
            if isinstance(data, dict):
                disc = "userRole"
                if disc not in data or data.get(disc) in (None, ""):
                    data[disc] = "PROJECT_MANAGER"
                _u = ProjectDtoV2.model_validate(data)
            else:
                raise
        return getattr(_u, "root", _u)

    async def enabled_quality_checks(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> EnabledQualityChecksDto:
        """
        Operation id: enabledQualityChecks
        Get QA checks
        Returns enabled quality assurance settings.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: EnabledQualityChecksDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/qaSettingsChecks"

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

        return EnabledQualityChecksDto.model_validate(r.json())

    async def get_analyse_settings_for_project(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> AnalyseSettingsDto:
        """
        Operation id: getAnalyseSettingsForProject
        Get analyse settings

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AnalyseSettingsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/analyseSettings"

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

        return AnalyseSettingsDto.model_validate(r.json())

    async def get_custom_field_of_project(
        self,
        field_instance_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> CustomFieldInstanceDto:
        """
        Operation id: getCustomFieldOfProject
        Get custom field of project

        :param field_instance_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstanceDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/customFields/{field_instance_uid}"

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

        return CustomFieldInstanceDto.model_validate(r.json())

    async def get_custom_fields_page_of_project(
        self,
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
        Operation id: getCustomFieldsPageOfProject
        Get custom fields of project (page)

        :param project_uid: str (required), path.
        :param created_by: Optional[List[str]] = None (optional), query. Filter by webhook creators UIDs.
        :param modified_by: Optional[List[str]] = None (optional), query. Filter by webhook updaters UIDs.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 20 (optional), query. Page size, accepts values between 1 and 50, default 20.
        :param sort_field: Optional[str] = None (optional), query. Sort by this field.
        :param sort_trend: Optional[str] = "ASC" (optional), query. Sort direction.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCustomFieldInstanceDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/customFields"

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

        return PageDtoCustomFieldInstanceDto.model_validate(r.json())

    async def get_file_naming_settings(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> FileNamingSettingsDto:
        """
        Operation id: getFileNamingSettings
        Get file naming settings for project

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileNamingSettingsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/fileNamingSettings"

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

        return FileNamingSettingsDto.model_validate(r.json())

    async def get_financial_settings(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> FinancialSettingsDto2:
        """
        Operation id: getFinancialSettings
        Get financial settings

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FinancialSettingsDto2
        """

        endpoint = f"/api2/v1/projects/{project_uid}/financialSettings"

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

        return FinancialSettingsDto2.model_validate(r.json())

    async def get_import_settings_for_project(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> FileImportSettingsDto:
        """
        Operation id: getImportSettingsForProject
        Get projects's default import settings

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileImportSettingsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/importSettings"

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

        return FileImportSettingsDto.model_validate(r.json())

    async def get_mt_settings_for_project(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> MTSettingsPerLanguageListDto:
        """
        Operation id: getMtSettingsForProject
        Get project machine translate settings

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MTSettingsPerLanguageListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/mtSettings"

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

        return MTSettingsPerLanguageListDto.model_validate(r.json())

    async def get_project(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ProjectDto:
        """
        Operation id: getProject
        Get project

        This API call retrieves information specific to a project.

        The level of detail in the response varies based on the user's role. Admins, Project Managers, Vendors, Buyers, and
        Linguists receive different responses, detailed below.

        - Details about predefined system metadata, such as client, domain, subdomain, cost center, business unit, or status.
        Note that [Custom Fields](#operation/getCustomField_1), if added to projects, are not included here and require
        retrieval via a dedicated Custom Fields API call. Metadata exposed to Linguists or Vendors might differ from what's
        visible to Admins or Project Managers.
        - [Workflow Step](https://support.phrase.com/hc/en-us/articles/5709717879324-Workflow-TMS-) information, crucial for
        user or vendor assignments through APIs. When projects are created, each workflow step's global ID instantiates into a
        project-specific workflow step ID necessary for user assignments. Attempting to assign the global workflow step ID
        (found under Settings or via Workflow Step APIs) results in an error, as only the project-specific step can be assigned.
        - Progress information indicating the total number of jobs across all workflow steps in the project, alongside the
        proportion of completed and overdue jobs.

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}"

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

        _u = ProjectDto.model_validate(r.json())
        return getattr(_u, "root", _u)

    async def get_project_access_settings_v2(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ProjectSecuritySettingsDtoV2:
        """
        Operation id: getProjectAccessSettingsV2
        Get access and security settings

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectSecuritySettingsDtoV2
        """

        endpoint = f"/api2/v2/projects/{project_uid}/accessSettings"

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

        return ProjectSecuritySettingsDtoV2.model_validate(r.json())

    async def get_project_assignments(
        self,
        project_uid: str,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        provider_name: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoProviderReference:
        """
        Operation id: getProjectAssignments
        List project providers

        :param project_uid: str (required), path.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param provider_name: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoProviderReference
        """

        endpoint = f"/api2/v1/projects/{project_uid}/providers"

        params = {
            "providerName": provider_name,
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

        return PageDtoProviderReference.model_validate(r.json())

    async def get_project_pre_translate_settings_v4(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> PreTranslateSettingsV4Dto:
        """
        Operation id: getProjectPreTranslateSettingsV4
        Get project pre-translate settings

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PreTranslateSettingsV4Dto
        """

        endpoint = f"/api2/v4/projects/{project_uid}/preTranslateSettings"

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

        return PreTranslateSettingsV4Dto.model_validate(r.json())

    async def get_project_settings(
        self,
        project_uid: str,
        workflow_level: Optional[int] = 1,
        phrase_token: Optional[str] = None,
    ) -> LqaSettingsDto:
        """
        Operation id: getProjectSettings
        Get LQA settings

        :param project_uid: str (required), path.
        :param workflow_level: Optional[int] = 1 (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaSettingsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/lqaSettings"

        params = {"workflowLevel": workflow_level}

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

        return LqaSettingsDto.model_validate(r.json())

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

    async def get_project_trans_memories_v3(
        self,
        project_uid: str,
        target_lang: Optional[str] = None,
        wf_step_uid: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectTransMemoryListDtoV3:
        """
        Operation id: getProjectTransMemoriesV3
        Get translation memories

        :param project_uid: str (required), path.
        :param target_lang: Optional[str] = None (optional), query. Filter project translation memories by target language.
        :param wf_step_uid: Optional[str] = None (optional), query. Filter project translation memories by workflow step.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTransMemoryListDtoV3
        """

        endpoint = f"/api2/v3/projects/{project_uid}/transMemories"

        params = {"targetLang": target_lang, "wfStepUid": wf_step_uid}

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

        return ProjectTransMemoryListDtoV3.model_validate(r.json())

    async def get_project_workflow_steps_v2(
        self,
        project_uid: str,
        with_assigned_jobs: Optional[bool] = False,
        phrase_token: Optional[str] = None,
    ) -> ProjectWorkflowStepListDtoV2:
        """
        Operation id: getProjectWorkflowStepsV2
        Get workflow steps

        :param project_uid: str (required), path.
        :param with_assigned_jobs: Optional[bool] = False (optional), query. Return only steps containing jobs assigned to the calling linguist..

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectWorkflowStepListDtoV2
        """

        endpoint = f"/api2/v2/projects/{project_uid}/workflowSteps"

        params = {"withAssignedJobs": with_assigned_jobs}

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

        return ProjectWorkflowStepListDtoV2.model_validate(r.json())

    async def get_quotes_for_project(
        self,
        project_uid: str,
        name: Optional[str] = None,
        order: Optional[str] = "desc",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "DATE_CREATED",
        phrase_token: Optional[str] = None,
    ) -> PageDtoQuoteDto:
        """
        Operation id: getQuotesForProject
        List quotes

        :param project_uid: str (required), path.
        :param name: Optional[str] = None (optional), query. Name to search by.
        :param order: Optional[str] = "desc" (optional), query. Sorting order.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "DATE_CREATED" (optional), query. Sorting field.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoQuoteDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/quotes"

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

        return PageDtoQuoteDto.model_validate(r.json())

    async def list_assigned_projects(
        self,
        user_uid: str,
        due_in_hours: Optional[int] = None,
        filename: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        project_name: Optional[str] = None,
        status: Optional[List[str]] = None,
        target_lang: Optional[List[str]] = None,
        workflow_step_id: Optional[int] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoProjectReference:
        """
        Operation id: listAssignedProjects
        List assigned projects
        List projects in which the user is assigned to at least one job matching the criteria
        :param user_uid: str (required), path.
        :param due_in_hours: Optional[int] = None (optional), query. Number of hours in which the assigned jobs are due. Use `-1` for jobs that are overdue..
        :param filename: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query.
        :param project_name: Optional[str] = None (optional), query.
        :param status: Optional[List[str]] = None (optional), query. Status of the assigned jobs.
        :param target_lang: Optional[List[str]] = None (optional), query. Target language of the assigned jobs.
        :param workflow_step_id: Optional[int] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoProjectReference
        """

        endpoint = f"/api2/v1/users/{user_uid}/projects"

        params = {
            "status": status,
            "targetLang": target_lang,
            "workflowStepId": workflow_step_id,
            "dueInHours": due_in_hours,
            "filename": filename,
            "projectName": project_name,
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

        return PageDtoProjectReference.model_validate(r.json())

    async def list_by_project_v3(
        self,
        project_uid: str,
        name: Optional[str] = None,
        only_owner_org: Optional[bool] = None,
        order: Optional[str] = "desc",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "DATE_CREATED",
        uid: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoAnalyseReference:
        """
        Operation id: listByProjectV3
        List analyses by project

        :param project_uid: str (required), path.
        :param name: Optional[str] = None (optional), query. Name to search by.
        :param only_owner_org: Optional[bool] = None (optional), query.
        :param order: Optional[str] = "desc" (optional), query. Sorting order.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "DATE_CREATED" (optional), query. Sorting field.
        :param uid: Optional[str] = None (optional), query. Uid to search by.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAnalyseReference
        """

        endpoint = f"/api2/v3/projects/{project_uid}/analyses"

        params = {
            "name": name,
            "uid": uid,
            "pageNumber": page_number,
            "pageSize": page_size,
            "sort": sort,
            "order": order,
            "onlyOwnerOrg": only_owner_org,
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

        return PageDtoAnalyseReference.model_validate(r.json())

    async def list_projects(
        self,
        archived_only: Optional[bool] = False,
        business_unit_id: Optional[int] = None,
        business_unit_name: Optional[str] = None,
        buyer_id: Optional[int] = None,
        client_id: Optional[int] = None,
        client_name: Optional[str] = None,
        cost_center_id: Optional[int] = None,
        cost_center_name: Optional[str] = None,
        created_in_last_hours: Optional[int] = None,
        domain_id: Optional[int] = None,
        domain_name: Optional[str] = None,
        due_in_hours: Optional[int] = None,
        include_archived: Optional[bool] = False,
        job_status_group: Optional[str] = None,
        job_statuses: Optional[List[str]] = None,
        name: Optional[str] = None,
        name_or_internal_id: Optional[str] = None,
        order: Optional[str] = "ASC",
        owner_id: Optional[int] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "ID",
        source_langs: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        sub_domain_id: Optional[int] = None,
        sub_domain_name: Optional[str] = None,
        target_langs: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoAbstractProjectDto:
        """
        Operation id: listProjects
        List projects

        API call to retrieve a paginated list of projects. Contains a subset of information contained in
        [Get project](#operation/getProject) API call.

        Utilize the query parameters below to refine the search criteria:

        - **name** - The full project name or a portion of it. For instance, using `name=GUI` or `name=02` will find projects
        named `GUI02`.
        - **clientId** - The client's ID within the system, not interchangeable with its UID.
        - **clientName** - The complete or partial name of the client. For example, using `clientName=GUI` or `clientName=02`
        will find projects associated with the client `GUI02`.
        - **businessUnitId** - The business unit's ID within the system, not interchangeable with its UID.
        - **businessUnitName** - The complete or partial name of the business unit. For instance, using `businessUnitName=GUI`
        or `businessUnitName=02` will find projects linked to the business unit `GUI02`.
        - **statuses** - A list of project statuses. When adding multiple statuses, include each as a dedicated query
        parameter, e.g., `statuses=ASSIGNED&statuses=COMPLETED`.
        - **domainId** - The domain's ID within the system, not interchangeable with its UID.
        - **domainName** - The complete or partial name of the domain. Using `domainName=GUI` or `domainName=02` will find
        projects associated with the domain `GUI02`.
        - **subDomainId** - The subdomain's ID within the system, not interchangeable with its UID.
        - **subDomainName** - The complete or partial name of the subdomain. For example, using `subDomainName=GUI` or
        `subDomainName=02` will find projects linked to the subdomain `GUI02`.
        - **costCenterId** - The cost center's ID within the system, not interchangeable with its UID.
        - **costCenterName** - The complete or partial name of the cost center. For instance, using `costCenterName=GUI` or
        `costCenterName=02` will find projects associated with the cost center `GUI02`.
        - **dueInHours** - Filter for jobs with due dates less than or equal to the specified number of hours.
        - **createdInLastHours** - Filter for jobs created within the specified number of hours.
        - **ownerId** - The user ID who owns the project within the system, not interchangeable with its UID.
        - **jobStatuses** - A list of statuses for jobs within the projects. Include each status as a dedicated query parameter,
        e.g., `jobStatuses=ASSIGNED&jobStatuses=COMPLETED`.
        - **jobStatusGroup** - The name of the status group used to filter projects containing at least one job with the
        specified status, similar to the status filter in the Projects list for a Linguist user.
        - **buyerId** - The Buyer's ID.
        - **pageNumber** - Indicates the desired page number (zero-based) to retrieve. The total number of pages is returned in
        the `totalPages` field within each response.
        - **pageSize** - Indicates the page size, affecting the `totalPages` retrieved in each response and potentially
        influencing the number of iterations needed to obtain all projects.
        - **nameOrInternalId** - Specify either the project name or Internal ID (the sequence number in the project list
        displayed in the UI).
        - **includeArchived** - A boolean parameter to include archived projects in the search.
        - **archivedOnly** - A boolean search indicating whether only archived projects should be searched.

        :param archived_only: Optional[bool] = False (optional), query. List only archived projects, regardless of `includeArchived`.
        :param business_unit_id: Optional[int] = None (optional), query.
        :param business_unit_name: Optional[str] = None (optional), query.
        :param buyer_id: Optional[int] = None (optional), query.
        :param client_id: Optional[int] = None (optional), query.
        :param client_name: Optional[str] = None (optional), query.
        :param cost_center_id: Optional[int] = None (optional), query.
        :param cost_center_name: Optional[str] = None (optional), query.
        :param created_in_last_hours: Optional[int] = None (optional), query.
        :param domain_id: Optional[int] = None (optional), query.
        :param domain_name: Optional[str] = None (optional), query.
        :param due_in_hours: Optional[int] = None (optional), query. -1 for projects that are overdue.
        :param include_archived: Optional[bool] = False (optional), query. List also archived projects.
        :param job_status_group: Optional[str] = None (optional), query. Allowed for linguists only.
        :param job_statuses: Optional[List[str]] = None (optional), query. Allowed for linguists only.
        :param name: Optional[str] = None (optional), query.
        :param name_or_internal_id: Optional[str] = None (optional), query. Name or internal ID of project.
        :param order: Optional[str] = "ASC" (optional), query.
        :param owner_id: Optional[int] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "ID" (optional), query.
        :param source_langs: Optional[List[str]] = None (optional), query.
        :param statuses: Optional[List[str]] = None (optional), query.
        :param sub_domain_id: Optional[int] = None (optional), query.
        :param sub_domain_name: Optional[str] = None (optional), query.
        :param target_langs: Optional[List[str]] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAbstractProjectDto
        """

        endpoint = "/api2/v1/projects"

        params = {
            "name": name,
            "clientId": client_id,
            "clientName": client_name,
            "businessUnitId": business_unit_id,
            "businessUnitName": business_unit_name,
            "statuses": statuses,
            "targetLangs": target_langs,
            "domainId": domain_id,
            "domainName": domain_name,
            "subDomainId": sub_domain_id,
            "subDomainName": sub_domain_name,
            "costCenterId": cost_center_id,
            "costCenterName": cost_center_name,
            "dueInHours": due_in_hours,
            "createdInLastHours": created_in_last_hours,
            "sourceLangs": source_langs,
            "ownerId": owner_id,
            "jobStatuses": job_statuses,
            "jobStatusGroup": job_status_group,
            "buyerId": buyer_id,
            "pageNumber": page_number,
            "pageSize": page_size,
            "nameOrInternalId": name_or_internal_id,
            "includeArchived": include_archived,
            "archivedOnly": archived_only,
            "sort": sort,
            "order": order,
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

        return PageDtoAbstractProjectDto.model_validate(r.json())

    async def list_providers_3(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ProviderListDtoV2:
        """
        Operation id: listProviders_3
        Get suggested providers

        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProviderListDtoV2
        """

        endpoint = f"/api2/v2/projects/{project_uid}/providers/suggest"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

        return ProviderListDtoV2.model_validate(r.json())

    async def patch_project(
        self,
        project_uid: str,
        patch_project_dto: Optional[PatchProjectDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectDto:
        """
        Operation id: patchProject
        Edit project

        :param project_uid: str (required), path.
        :param patch_project_dto: Optional[PatchProjectDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}"
        if type(patch_project_dto) is dict:
            patch_project_dto = PatchProjectDto.model_validate(patch_project_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = patch_project_dto

        r = await self.client.make_request(
            "PATCH",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        _u = ProjectDto.model_validate(r.json())
        return getattr(_u, "root", _u)

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

    async def relevant_trans_memories_for_project(
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

        return PageDtoTransMemoryDto.model_validate(r.json())

    async def restore_project(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: restoreProject
        Restore project
        Restores a project that was previously archived
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/restore"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        await self.client.make_request(
            "PATCH",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return

    async def search_tm_segment(
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

        return SearchResponseListTmDto.model_validate(r.json())

    async def set_financial_settings(
        self,
        project_uid: str,
        set_financial_settings_dto: Optional[SetFinancialSettingsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> FinancialSettingsDto2:
        """
        Operation id: setFinancialSettings
        Edit financial settings

        :param project_uid: str (required), path.
        :param set_financial_settings_dto: Optional[SetFinancialSettingsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FinancialSettingsDto2
        """

        endpoint = f"/api2/v1/projects/{project_uid}/financialSettings"
        if type(set_financial_settings_dto) is dict:
            set_financial_settings_dto = SetFinancialSettingsDto.model_validate(
                set_financial_settings_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = set_financial_settings_dto

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

        return FinancialSettingsDto2.model_validate(r.json())

    async def set_mt_settings_for_project(
        self,
        project_uid: str,
        edit_project_mt_settings_dto: Optional[EditProjectMTSettingsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> MTSettingsPerLanguageListDto:
        """
        Operation id: setMtSettingsForProject
        Edit machine translate settings
        This will erase all mtSettings per language for project.
                To remove all machine translate settings from project call without a machineTranslateSettings parameter.
        :param project_uid: str (required), path.
        :param edit_project_mt_settings_dto: Optional[EditProjectMTSettingsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MTSettingsPerLanguageListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/mtSettings"
        if type(edit_project_mt_settings_dto) is dict:
            edit_project_mt_settings_dto = EditProjectMTSettingsDto.model_validate(
                edit_project_mt_settings_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = edit_project_mt_settings_dto

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

        return MTSettingsPerLanguageListDto.model_validate(r.json())

    async def set_mt_settings_per_language_for_project(
        self,
        project_uid: str,
        edit_project_mt_sett_per_lang_list_dto: Optional[
            EditProjectMTSettPerLangListDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> MTSettingsPerLanguageListDto:
        """
        Operation id: setMtSettingsPerLanguageForProject
        Edit machine translate settings per language
        This will erase mtSettings for project
        :param project_uid: str (required), path.
        :param edit_project_mt_sett_per_lang_list_dto: Optional[EditProjectMTSettPerLangListDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MTSettingsPerLanguageListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/mtSettingsPerLanguage"
        if type(edit_project_mt_sett_per_lang_list_dto) is dict:
            edit_project_mt_sett_per_lang_list_dto = (
                EditProjectMTSettPerLangListDto.model_validate(
                    edit_project_mt_sett_per_lang_list_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = edit_project_mt_sett_per_lang_list_dto

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

        return MTSettingsPerLanguageListDto.model_validate(r.json())

    async def set_project_qa_settings_v2(
        self,
        project_uid: str,
        edit_qa_settings_dto_v2: Optional[EditQASettingsDtoV2 | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> QASettingsDtoV2:
        """
        Operation id: setProjectQASettingsV2
        Edit quality assurance settings

        :param project_uid: str (required), path.
        :param edit_qa_settings_dto_v2: Optional[EditQASettingsDtoV2 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QASettingsDtoV2
        """

        endpoint = f"/api2/v2/projects/{project_uid}/qaSettings"
        if type(edit_qa_settings_dto_v2) is dict:
            edit_qa_settings_dto_v2 = EditQASettingsDtoV2.model_validate(
                edit_qa_settings_dto_v2
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = edit_qa_settings_dto_v2

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

        return QASettingsDtoV2.model_validate(r.json())

    async def set_project_status(
        self,
        project_uid: str,
        set_project_status_dto: Optional[SetProjectStatusDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: setProjectStatus
        Edit project status

        :param project_uid: str (required), path.
        :param set_project_status_dto: Optional[SetProjectStatusDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/setStatus"
        if type(set_project_status_dto) is dict:
            set_project_status_dto = SetProjectStatusDto.model_validate(
                set_project_status_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = set_project_status_dto

        await self.client.make_request(
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

    async def set_project_trans_memories_v3(
        self,
        project_uid: str,
        set_project_trans_memories_v3_dto: Optional[
            SetProjectTransMemoriesV3Dto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> ProjectTransMemoryListDtoV3:
        """
        Operation id: setProjectTransMemoriesV3
        Edit translation memories
        If user wants to edit “All target languages” or "All workflow steps”,
                               but there are already varied TM settings for individual languages or steps,
                               then the user risks to overwrite these individual choices.
        :param project_uid: str (required), path.
        :param set_project_trans_memories_v3_dto: Optional[SetProjectTransMemoriesV3Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTransMemoryListDtoV3
        """

        endpoint = f"/api2/v3/projects/{project_uid}/transMemories"
        if type(set_project_trans_memories_v3_dto) is dict:
            set_project_trans_memories_v3_dto = (
                SetProjectTransMemoriesV3Dto.model_validate(
                    set_project_trans_memories_v3_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = set_project_trans_memories_v3_dto

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

        return ProjectTransMemoryListDtoV3.model_validate(r.json())

    async def update_file_naming_settings(
        self,
        project_uid: str,
        file_naming_settings_dto: Optional[FileNamingSettingsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> FileNamingSettingsDto:
        """
        Operation id: updateFileNamingSettings
        Update file naming settings for project

        :param project_uid: str (required), path.
        :param file_naming_settings_dto: Optional[FileNamingSettingsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileNamingSettingsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/fileNamingSettings"
        if type(file_naming_settings_dto) is dict:
            file_naming_settings_dto = FileNamingSettingsDto.model_validate(
                file_naming_settings_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = file_naming_settings_dto

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

        return FileNamingSettingsDto.model_validate(r.json())

    async def update_project_pre_translate_settings_v4(
        self,
        project_uid: str,
        pre_translate_settings_v4_dto: Optional[
            PreTranslateSettingsV4Dto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> PreTranslateSettingsV4Dto:
        """
        Operation id: updateProjectPreTranslateSettingsV4
        Update project pre-translate settings

        :param project_uid: str (required), path.
        :param pre_translate_settings_v4_dto: Optional[PreTranslateSettingsV4Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PreTranslateSettingsV4Dto
        """

        endpoint = f"/api2/v4/projects/{project_uid}/preTranslateSettings"
        if type(pre_translate_settings_v4_dto) is dict:
            pre_translate_settings_v4_dto = PreTranslateSettingsV4Dto.model_validate(
                pre_translate_settings_v4_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = pre_translate_settings_v4_dto

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

        return PreTranslateSettingsV4Dto.model_validate(r.json())

    async def upload_job_preview_package(
        self,
        file: bytes,
        project_uid: str,
        content_type: str = "multipart/form-data",
        filename: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> JobPreviewPackageDto:
        """
        Operation id: uploadJobPreviewPackage
        Upload Job Preview Package
        Uploads a Job Preview Package to a project. ImportFile API then refers to the preview package.
                The package is a zip file containing the preview HTML and related asset (css, js..) files.
        :param file: bytes (required), formData.
        :param project_uid: str (required), path.
        :param content_type: str = "multipart/form-data" (required), header.

        :param filename: Optional name for the uploaded file; defaults to field name.
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPreviewPackageDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobPreviewPackage"

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

        return JobPreviewPackageDto.model_validate(r.json())
