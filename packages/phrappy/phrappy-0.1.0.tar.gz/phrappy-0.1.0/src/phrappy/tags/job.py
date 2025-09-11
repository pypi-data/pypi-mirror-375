from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import json

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    AsyncRequestWrapperV2Dto,
    ComparedSegmentsDto,
    CreateCustomFieldInstancesDto,
    CreateTermsDto,
    CreateWebEditorLinkDtoV2,
    CustomFieldInstanceDto,
    CustomFieldInstancesDto,
    DownloadTargetFileDto,
    FileHandoverDto,
    FileImportSettingsCreateDto,
    FileImportSettingsDto,
    GetBilingualFileDto,
    JobCreateRequestDto,
    JobExportActionDto,
    JobExportResponseDto,
    JobListDto,
    JobPartDeleteReferences,
    JobPartExtendedDto,
    JobPartPatchBatchDto,
    JobPartPatchResultDto,
    JobPartPatchSingleDto,
    JobPartReadyDeleteTranslationDto,
    JobPartReadyReferences,
    JobPartReferences,
    JobPartStatusChangesDto,
    JobPartUpdateBatchDto,
    JobPartUpdateSingleDto,
    JobPartsDto,
    JobStatusChangeActionDto,
    JobUpdateSourceMeta,
    JobUpdateSourceResponseDto,
    JobUpdateTargetMeta,
    NotifyJobPartsRequestDto,
    PageDtoAnalyseReference,
    PageDtoCustomFieldInstanceDto,
    PageDtoJobPartReferenceV2,
    PreviewUrlsDto,
    ProjectWorkflowStepDto,
    ProviderListDtoV2,
    PseudoTranslateActionDto,
    PseudoTranslateWrapperDto,
    SearchInTextResponseList2Dto,
    SearchJobsDto,
    SearchJobsRequestDto,
    SearchResponseListTmDto,
    SearchResponseListTmDtoV3,
    SearchTMByJobRequestDto,
    SearchTMByJobRequestDtoV3,
    SearchTbByJobRequestDto,
    SearchTbInTextByJobRequestDto,
    SearchTbResponseListDto,
    SegmentListDto,
    SegmentsCountsResponseListDto,
    SplitJobActionDto,
    TargetFileWarningsDto,
    TermPairDto,
    TranslationResourcesDto,
    UpdateCustomFieldInstanceDto,
    UpdateCustomFieldInstancesDto,
    UploadHandoverFileMeta,
    WebEditorLinkDtoV2,
    WildCardSearchByJobRequestDtoV3,
)


class JobOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def compare_part(
        self,
        project_uid: str,
        at_workflow_level: Optional[int] = 1,
        job_part_ready_references: Optional[JobPartReadyReferences | dict] = None,
        with_workflow_level: Optional[int] = 1,
        phrase_token: Optional[str] = None,
    ) -> ComparedSegmentsDto:
        """
        Operation id: comparePart
        Compare jobs on workflow levels

        :param project_uid: str (required), path.
        :param at_workflow_level: Optional[int] = 1 (optional), query.
        :param job_part_ready_references: Optional[JobPartReadyReferences | dict] = None (optional), body.
        :param with_workflow_level: Optional[int] = 1 (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ComparedSegmentsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/compare"
        if type(job_part_ready_references) is dict:
            job_part_ready_references = JobPartReadyReferences.model_validate(
                job_part_ready_references
            )

        params = {
            "atWorkflowLevel": at_workflow_level,
            "withWorkflowLevel": with_workflow_level,
        }

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_ready_references

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

        return ComparedSegmentsDto.model_validate(r.json())

    def completed_file_v2(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> AsyncRequestWrapperV2Dto:
        """
        Operation id: completedFileV2
        Download target file (async)

        This call initiates an asynchronous request to generate and download the target file containing translations.
        This request covers jobs created via actions like 'split jobs', ensuring accessibility even for such cases.

        To monitor the status of this asynchronous request, you have two options:
        1. Use [Get asynchronous request](#operation/getAsyncRequest).
        2. Search for the asyncRequestId by utilizing [List pending requests](#operation/listPendingRequests).

        In contrast to the previous version (v1) of this call, v2 does not directly provide the target file within the response.
        Once the asynchronous request is completed, you can download the target file using
        [Download target file based on async request](#operation/downloadCompletedFile).

        _Note_: The asyncRequestId can be used only once. Once the download is initiated through `Download target file based on
        async request`, the asyncRequestId becomes invalid for further use.

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperV2Dto
        """

        endpoint = f"/api2/v2/projects/{project_uid}/jobs/{job_uid}/targetFile"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

        return AsyncRequestWrapperV2Dto.model_validate(r.json())

    def completed_file_v3(
        self,
        job_uid: str,
        project_uid: str,
        download_target_file_dto: Optional[DownloadTargetFileDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AsyncRequestWrapperV2Dto:
        """
        Operation id: completedFileV3
        Download target file (async)

        This call initiates an asynchronous request to generate and download the target file containing translations.
        This request covers jobs created via actions like 'split jobs', ensuring accessibility even for such cases.

        To monitor the status of this asynchronous request, you have three options:
        1. Use [Get asynchronous request](#operation/getAsyncRequest).
        2. Search for the asyncRequestId by utilizing [List pending requests](#operation/listPendingRequests).
        3. Use callbackUrl to get notification that operation was finished

        In contrast to the previous version (v1) of this call, v2 does not directly provide the target file within the response.
        Once the asynchronous request is completed, you can download the target file using
        [Download target file based on async request](#operation/downloadCompletedFile).

        _Note_: The asyncRequestId can be used only once. Once the download is initiated through `Download target file based on
        async request`, the asyncRequestId becomes invalid for further use.

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param download_target_file_dto: Optional[DownloadTargetFileDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperV2Dto
        """

        endpoint = f"/api2/v3/projects/{project_uid}/jobs/{job_uid}/targetFile"
        if type(download_target_file_dto) is dict:
            download_target_file_dto = DownloadTargetFileDto.model_validate(
                download_target_file_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = download_target_file_dto

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

        return AsyncRequestWrapperV2Dto.model_validate(r.json())

    def copy_source_to_target(
        self,
        project_uid: str,
        job_part_ready_references: Optional[JobPartReadyReferences | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: copySourceToTarget
        Copy Source to Target

        :param project_uid: str (required), path.
        :param job_part_ready_references: Optional[JobPartReadyReferences | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/copySourceToTarget"
        if type(job_part_ready_references) is dict:
            job_part_ready_references = JobPartReadyReferences.model_validate(
                job_part_ready_references
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_ready_references

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

    def copy_source_to_target_job_part(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: copySourceToTargetJobPart
        Copy Source to Target job

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/copySourceToTarget"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

    def create_job(
        self,
        project_uid: str,
        content_disposition: Optional[str] = None,
        memsource: Optional[JobCreateRequestDto | dict] = None,
        file_bytes: Optional[bytes] = None,
        phrase_token: Optional[str] = None,
    ) -> JobListDto:
        """
        Operation id: createJob
        Create job

        An API call to create a [job](https://support.phrase.com/hc/en-us/articles/5709686763420-Jobs-TMS-)
        within a specified [project](https://support.phrase.com/hc/en-us/articles/5709748435484-Projects-TMS-).
        The source file can be provided directly in the message body or downloaded from connector.

        Please supply job metadata in `Memsource` header. For file in the request body provide also the
        filename in `Content-Disposition` header.

        Accepted metadata:

        - **targetLangs** - This parameter specifies what languages should the job be created in. Only languages that are
        present in the project are supported, but this parameter accepts a subset of languages. When the file is uploaded, the
        number of jobs created (and returned) corresponds to the number of target languages and the workflow steps of the
        project. For example, `sample.json` imported for `EN>DE` and `EN>FR` language combination into a project with
        `Translation` and `Review` workflow steps will result in 4 jobs being created, one for each language and step.
        _Note_: Each time a file is uploaded, the resulting wordcount for each target language (not workflow step) is counted
        towards the organization's allowance.
        - **due** - ISO 8601
        - **workflowSettings** - This parameter is used to set up assignments and due date for projects with workflow steps.
        When a project is created, the global workflow steps available via [List woorkflow steps](#operation/listWFSteps) are
        instantiated for the given project at hand. To assign users or due dates, these project specific IDs need to be used
        instead of the global ones.
        - **assignments** - If a project does not contain workflow steps, this parameter can be used to assign users directly.
        - **importSettings** - Re-usable [import settings](#operation/createImportSettings)
        - **useProjectFileImportSettings** - When project is created, either global default setting or settings of a
        [project template](https://support.phrase.com/hc/en-us/articles/5709647439772-Project-Templates-TMS-) are copied
        into it. This parameter can be used to reference these project settings instead of using the API defaults.
        Mutually exclusive with importSettings
        - **callbackUrl** - A URL that can be notified when the job creation has been finished.
        Unlike [webhooks](https://support.phrase.com/hc/en-us/articles/5709693398812-Webhooks-TMS-) which are global for the
        entire account, the `callbackUrl` is set only for the specific operation at hand.
        - **path** - A parameter that can be used to specify a location of the source file and preserved for later download.
        This is automatically created when importing ZIP files.
        - **preTranslate** - A parameter that indicates if the job should be
        [pre-translated](https://support.phrase.com/hc/en-us/articles/5709717749788-Pre-translation-TMS-) after job creation.
        - **semanticMarkup** - Set semantic markup processing after import when enabled for organization
        - **xmlAssistantProfile** - Apply XML import settings defined using XML assistant
        - **jobPreviewPackageFileUidRef** - reference to a job preview package file to create a preview for the imported file

        For remote file jobs also `remoteFile` can be added. To retrieve the information below,
        use the [connector](#operation/getConnectorList) APIs.
        - **connectorToken** - Token of the connector for the purposes of the APIs
        - **remoteFolder** - An encoded name of the folder, retrieved by e.g. [List files in a subfolder](#operation/getFolder)
        - **remoteFileName** - An encoded name of the file, retrieved similarly to above.
        - **continuous** - Jobs created with files from a connector can be created
        as [continuous](https://support.phrase.com/hc/en-us/articles/5709711922972-Continuous-Jobs-CJ-TMS-)

        Create and assign job in project without workflow step:
        ```

        {
          "targetLangs": [
            "cs_cz"
          ],
          "callbackUrl": "https://my-shiny-service.com/consumeCallback",
          "importSettings": {
            "uid": "abcd123"
          },
          "due": "2007-12-03T10:15:30.00Z",
          "path": "destination directory",
          "assignments": [
            {
              "targetLang": "cs_cz",
              "providers": [
                {
                  "id": "4321",
                  "type": "USER"
                }
              ]
            }
          ],
          "notifyProvider": {
            "organizationEmailTemplate": {
              "id": "39"
            },
            "notificationIntervalInMinutes": "10"
          }
        }
        ```

        Create job from remote file without workflow steps:
        ```

        {
          "remoteFile": {
            "connectorToken": "948123ef-e1ef-4cd3-a90e-af1617848af3",
            "remoteFolder": "/",
            "remoteFileName": "Few words.docx",
            "continuous": false
          },
          "assignments": [],
          "workflowSettings": [],
          "targetLangs": [
            "cs"
          ]
        }
        ```

        Create and assign job in project with workflow step:
        ```

        {
          "targetLangs": [
            "de"
          ],
          "useProjectFileImportSettings": "true",
          "workflowSettings": [
            {
              "id": "64",
              "due": "2007-12-03T10:15:30.00Z",
              "assignments": [
                {
                  "targetLang": "de",
                  "providers": [
                    {
                      "id": "3",
                      "type": "VENDOR"
                    }
                  ]
                }
              ],
              "notifyProvider": {
                "organizationEmailTemplate": {
                  "id": "39"
                },
                "notificationIntervalInMinutes": "10"
              }
            }
          ]
        }
        ```

        Create a job with job preview package reference:
        ```
        {
          "targetLangs": [
            "de"
          ],
          "jobPreviewPackageFileUidRef": {"uid": "jobPreviewPackageFileUid123"}
        }
        ```

        :param project_uid: str (required), path.
        :param content_disposition: Optional[str] = None (optional), header. must match pattern `((inline|attachment); )?(filename\\*=UTF-8''(.+)|filename="?(.+)"?)`.
        :param memsource: Optional[JobCreateRequestDto | dict] = None (optional), header.
        :param file_bytes: Optional[bytes] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs"
        if type(memsource) is dict:
            memsource = JobCreateRequestDto.model_validate(memsource)

        params = {}

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

        return JobListDto.model_validate(r.json())

    def create_job_from_async_download_task(
        self,
        project_uid: str,
        job_create_request_dto: Optional[JobCreateRequestDto | dict] = None,
        continuous: Optional[bool] = False,
        download_task_id: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> JobListDto:
        """
        Operation id: createJobFromAsyncDownloadTask
        Create job from connector asynchronous download task

        Creates the job in project specified by path param projectUid. Source file is defined by downloadTaskId parameter. That is value of finished download async task
        [Connector - Download file (async)](#operation/getFile_1).

        Please supply job metadata in body.

        Accepted metadata:

          - `targetLangs` - **required**
          - `due` - ISO 8601
          - `workflowSettings` - project with workflow - see examples bellow
          - `assignments` - project without workflows - see examples bellow
          - `importSettings` - re-usable import settings - see [Create import settings](#operation/createImportSettings)
          - `useProjectFileImportSettings` - mutually exclusive with importSettings
          - `callbackUrl` - consumer callback
          - `path` - original destination directory
          - `preTranslate` - set pre translate job after import
          - `semanticMarkup` - set semantic markup processing after import when enabled for organization
          - `xmlAssistantProfile` - apply XML import settings defined using XML assistant

        Create job simple (without workflow steps, without assignments):
        ```
        {
          "targetLangs": [
            "cs_cz",
            "es_es"
          ]
        }
        ```

        Create and assign job in project without workflow step:
        ```
        {
          "targetLangs": [
            "cs_cz"
          ],
          "callbackUrl": "https://my-shiny-service.com/consumeCallback",
          "importSettings": {
            "uid": "abcd123"
          },
          "due": "2007-12-03T10:15:30.00Z",
          "path": "destination directory",
          "assignments": [
            {
              "targetLang": "cs_cz",
              "providers": [
                {
                  "id": "4321",
                  "type": "USER"
                }
              ]
            }
          ],
          "notifyProvider": {
            "organizationEmailTemplate": {
              "id": "39"
            },
            "notificationIntervalInMinutes": "10"
          }
        }
        ```

        Create and assign job in project with workflow step:
        ```
        {
          "targetLangs": [
            "de"
          ],
          "useProjectFileImportSettings": "true",
          "workflowSettings": [
            {
              "id": "64",
              "due": "2007-12-03T10:15:30.00Z",
              "assignments": [
                {
                  "targetLang": "de",
                  "providers": [
                    {
                      "id": "3",
                      "type": "VENDOR"
                    }
                  ]
                }
              ],
              "notifyProvider": {
                "organizationEmailTemplate": {
                  "id": "39"
                },
                "notificationIntervalInMinutes": "10"
              }
            }
          ]
        }
        ```

        :param project_uid: str (required), path.
        :param job_create_request_dto: Optional[JobCreateRequestDto | dict] = None (optional), body.
        :param continuous: Optional[bool] = False (optional), query.
        :param download_task_id: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/connectorTask"
        if type(job_create_request_dto) is dict:
            job_create_request_dto = JobCreateRequestDto.model_validate(
                job_create_request_dto
            )

        params = {"downloadTaskId": download_task_id, "continuous": continuous}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_create_request_dto

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

        return JobListDto.model_validate(r.json())

    def create_term_by_job(
        self,
        job_uid: str,
        project_uid: str,
        create_terms_dto: Optional[CreateTermsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> TermPairDto:
        """
        Operation id: createTermByJob
        Create term in job's term bases
        Create new term in the write term base assigned to the job
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param create_terms_dto: Optional[CreateTermsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TermPairDto
        """

        endpoint = (
            f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/termBases/createByJob"
        )
        if type(create_terms_dto) is dict:
            create_terms_dto = CreateTermsDto.model_validate(create_terms_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_terms_dto

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

        return TermPairDto.model_validate(r.json())

    def delete_all_translations(
        self,
        project_uid: str,
        job_part_ready_references: Optional[JobPartReadyReferences | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteAllTranslations
        Delete all translations

        :param project_uid: str (required), path.
        :param job_part_ready_references: Optional[JobPartReadyReferences | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/translations"
        if type(job_part_ready_references) is dict:
            job_part_ready_references = JobPartReadyReferences.model_validate(
                job_part_ready_references
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_ready_references

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

    def delete_all_translations_v2(
        self,
        project_uid: str,
        job_part_ready_delete_translation_dto: Optional[
            JobPartReadyDeleteTranslationDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteAllTranslationsV2
        Delete specific translations

        :param project_uid: str (required), path.
        :param job_part_ready_delete_translation_dto: Optional[JobPartReadyDeleteTranslationDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v2/projects/{project_uid}/jobs/translations"
        if type(job_part_ready_delete_translation_dto) is dict:
            job_part_ready_delete_translation_dto = (
                JobPartReadyDeleteTranslationDto.model_validate(
                    job_part_ready_delete_translation_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_ready_delete_translation_dto

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

    def delete_handover_file(
        self,
        project_uid: str,
        job_part_references: Optional[JobPartReferences | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteHandoverFile
        Delete handover file

        :param project_uid: str (required), path.
        :param job_part_references: Optional[JobPartReferences | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/fileHandovers"
        if type(job_part_references) is dict:
            job_part_references = JobPartReferences.model_validate(job_part_references)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_references

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

    def delete_parts(
        self,
        project_uid: str,
        job_part_delete_references: Optional[JobPartDeleteReferences | dict] = None,
        purge: Optional[bool] = False,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteParts
        Delete job (batch)

        :param project_uid: str (required), path.
        :param job_part_delete_references: Optional[JobPartDeleteReferences | dict] = None (optional), body.
        :param purge: Optional[bool] = False (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/batch"
        if type(job_part_delete_references) is dict:
            job_part_delete_references = JobPartDeleteReferences.model_validate(
                job_part_delete_references
            )

        params = {"purge": purge}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_delete_references

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

    def download_completed_file(
        self,
        async_request_id: str,
        job_uid: str,
        project_uid: str,
        format: Optional[str] = "ORIGINAL",
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: downloadCompletedFile
        Download target file based on async request

        This call will return target file with translation. This means even for other jobs that were created via
        'split jobs' etc.

        The asyncRequestId can be used only once. Once the download is initiated , the asyncRequestId becomes
        invalid for further use.

        :param async_request_id: str (required), path.
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param format: Optional[str] = "ORIGINAL" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v2/projects/{project_uid}/jobs/{job_uid}/downloadTargetFile/{async_request_id}"

        params = {"format": format}

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

    def edit_job_import_settings(
        self,
        job_uid: str,
        project_uid: str,
        file_import_settings_create_dto: Optional[
            FileImportSettingsCreateDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> FileImportSettingsDto:
        """
        Operation id: editJobImportSettings
        Edit job import settings

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param file_import_settings_create_dto: Optional[FileImportSettingsCreateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileImportSettingsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/importSettings"
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

        return FileImportSettingsDto.model_validate(r.json())

    def edit_part(
        self,
        job_uid: str,
        project_uid: str,
        job_part_update_single_dto: Optional[JobPartUpdateSingleDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> JobPartExtendedDto:
        """
        Operation id: editPart
        Edit job

        This API call facilitates job editing using a PUT method.

        Unlike [Patch job](#operation/patchPart), this call employs a PUT method, necessitating the inclusion of all
        parameters in the request. Omitting any parameter will reset its value to the default. For instance, if only the status
        field is included, the due date and provider fields will be emptied, even if they had previous values.

        It's recommended to either use a call like [Get job](#operation/getPart) or [List jobs](#operation/listPartsV2) to
        gather the unchanged information or consider using the [Patch job](#operation/patchPart) operation.

        This call supports editing the status, due date, and providers. When modifying providers, it's crucial to submit both
        the provider's ID and its type (either VENDOR or USER).

        The response will offer a subset of information from [Get job](#operation/getPart).

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param job_part_update_single_dto: Optional[JobPartUpdateSingleDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartExtendedDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}"
        if type(job_part_update_single_dto) is dict:
            job_part_update_single_dto = JobPartUpdateSingleDto.model_validate(
                job_part_update_single_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_update_single_dto

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

        return JobPartExtendedDto.model_validate(r.json())

    def edit_parts(
        self,
        project_uid: str,
        job_part_update_batch_dto: Optional[JobPartUpdateBatchDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> JobPartsDto:
        """
        Operation id: editParts
        Edit jobs (batch)

        Returns only jobs which were updated by the batch operation.

        :param project_uid: str (required), path.
        :param job_part_update_batch_dto: Optional[JobPartUpdateBatchDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/batch"
        if type(job_part_update_batch_dto) is dict:
            job_part_update_batch_dto = JobPartUpdateBatchDto.model_validate(
                job_part_update_batch_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_update_batch_dto

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

        return JobPartsDto.model_validate(r.json())

    def export_to_online_repository(
        self,
        project_uid: str,
        job_export_action_dto: Optional[JobExportActionDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> JobExportResponseDto:
        """
        Operation id: exportToOnlineRepository
        Export jobs to online repository

        :param project_uid: str (required), path.
        :param job_export_action_dto: Optional[JobExportActionDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobExportResponseDto
        """

        endpoint = f"/api2/v3/projects/{project_uid}/jobs/export"
        if type(job_export_action_dto) is dict:
            job_export_action_dto = JobExportActionDto.model_validate(
                job_export_action_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_export_action_dto

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

        return JobExportResponseDto.model_validate(r.json())

    def file_preview(
        self,
        job_uid: str,
        project_uid: str,
        file_bytes: Optional[bytes] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: filePreview
        Download preview file
        Takes bilingual file (.mxliff only) as argument. If not passed, data will be taken from database
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param file_bytes: Optional[bytes] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/preview"

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

        return r.content

    def file_preview_job(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: filePreviewJob
        Download preview file

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/preview"

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

    def get_asset(
        self,
        asset_file_uid: str,
        job_part_uid: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: getAsset
        Get Job Preview Package assets.
        URLs for this API are provided in html skeleton (preview) part of mxliff.
        :param asset_file_uid: str (required), path.
        :param job_part_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        !!! N.B.: API docs have no 200 range response declared, so falling back to returning the raw bytes from the API response.

        :return: bytes
        """

        endpoint = f"/api2/v1/jobs/{job_part_uid}/previewPackage/asset/{asset_file_uid}"

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

    def get_bilingual_file(
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

    def get_completed_file_warnings(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> TargetFileWarningsDto:
        """
        Operation id: getCompletedFileWarnings
        Get target file's warnings

        This call will return target file's warnings. This means even for other jobs that were created via 'split jobs' etc.

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TargetFileWarningsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/targetFileWarnings"

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

        return TargetFileWarningsDto.model_validate(r.json())

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

    def get_handover_files(
        self,
        project_uid: str,
        job_uid: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: getHandoverFiles
        Download handover file(s)

        For downloading multiple files as ZIP file provide multiple IDs in query parameters.
        * For example `?jobUid={id1}&jobUid={id2}`
        * When no files matched given IDs error 404 is returned, otherwise ZIP file will include those that were found

        :param project_uid: str (required), path.
        :param job_uid: Optional[List[str]] = None (optional), query. JobPart Id of requested handover file.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/projects/{project_uid}/fileHandovers"

        params = {"jobUid": job_uid}

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

    def get_import_settings_for_job(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> FileImportSettingsDto:
        """
        Operation id: getImportSettingsForJob
        Get import settings for job

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileImportSettingsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/importSettings"

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

        return FileImportSettingsDto.model_validate(r.json())

    def get_original_file(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: getOriginalFile
        Download original file

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/original"

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

    def get_part(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> JobPartExtendedDto:
        """
        Operation id: getPart
        Get job

        This API call provides specific information about a
        [job](https://support.phrase.com/hc/en-us/articles/5709686763420-Jobs-TMS-) within a project.

        The response includes fundamental job details such as the current status, assigned providers, language combination, or
        [workflow step](https://support.phrase.com/hc/en-us/articles/5709717879324-Workflow-TMS-) to which the job belongs.
        Additionally, it offers a subset of the [Get project](#operation/getProject) information.

        Furthermore, the response contains timestamps for the last
        [Update source and Update target](https://support.phrase.com/hc/en-us/articles/10825557848220-Job-Tools) operations
        executed on the job.

        If the job was imported as
        [continuous](https://support.phrase.com/hc/en-us/articles/5709711922972-Continuous-Jobs-CJ-TMS-), the job will be
        marked as such, and the response will include the timestamp of the last update.

        Moreover, the response features a boolean flag indicating if the job was imported successfully.
        It also highlights potential errors that might have occurred during the import process.

        The `jobReference` field serves as a unique identifier that allows matching corresponding jobs across different
        workflow steps.

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartExtendedDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}"

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

        return JobPartExtendedDto.model_validate(r.json())

    def get_parts_workflow_step(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ProjectWorkflowStepDto:
        """
        Operation id: getPartsWorkflowStep
        Get job's workflowStep

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectWorkflowStepDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/workflowStep"

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

        return ProjectWorkflowStepDto.model_validate(r.json())

    def get_segments_count(
        self,
        project_uid: str,
        job_part_ready_references: Optional[JobPartReadyReferences | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SegmentsCountsResponseListDto:
        """
        Operation id: getSegmentsCount
        Get segments count

        This API provides the current count of segments (progress data).

        Every time this API is called, it returns the most up-to-date information. Consequently, these numbers will change
        dynamically over time. The data retrieved from this API call is utilized to calculate the progress percentage in the UI.

        The call returns the following information:

        Counts of characters, words, and segments for each of the locked, confirmed, and completed categories. In this context,
        _completed_ is defined as `confirmed` + `locked` - `confirmed and locked`.

        The number of added words if the [Update source](https://support.phrase.com/hc/en-us/articles/10825557848220-Job-Tools)
        operation has been performed on the job. In this context, added words are defined as the original word count plus the
        sum of words added during all subsequent update source operations.

        The count of segments where relevant machine translation (MT) was available (machineTranslationRelevantSegmentsCount)
        and the number of segments where the MT output was post-edited (machineTranslationPostEditedSegmentsCount).

        A breakdown of [Quality assurance](https://support.phrase.com/hc/en-us/articles/5709703799324-Quality-Assurance-QA-TMS-)
        results, including the number of segments on which it was performed, the count of warnings found, and the number of
        warnings that were ignored.

        Additionally, a breakdown of the aforementioned information from the previous
        [Workflow step](https://support.phrase.com/hc/en-us/articles/5709717879324-Workflow-TMS-) is also provided.

        :param project_uid: str (required), path.
        :param job_part_ready_references: Optional[JobPartReadyReferences | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SegmentsCountsResponseListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/segmentsCount"
        if type(job_part_ready_references) is dict:
            job_part_ready_references = JobPartReadyReferences.model_validate(
                job_part_ready_references
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_ready_references

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

        return SegmentsCountsResponseListDto.model_validate(r.json())

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

    def list_part_analyse_v3(
        self,
        job_uid: str,
        project_uid: str,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoAnalyseReference:
        """
        Operation id: listPartAnalyseV3
        List analyses

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAnalyseReference
        """

        endpoint = f"/api2/v3/projects/{project_uid}/jobs/{job_uid}/analyses"

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

        return PageDtoAnalyseReference.model_validate(r.json())

    def list_parts_v2(
        self,
        project_uid: str,
        assigned_user: Optional[int] = None,
        assigned_vendor: Optional[int] = None,
        count: Optional[bool] = False,
        due_in_hours: Optional[int] = None,
        filename: Optional[str] = None,
        not_ready: Optional[bool] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        status: Optional[List[str]] = None,
        target_lang: Optional[str] = None,
        workflow_level: Optional[int] = 1,
        phrase_token: Optional[str] = None,
    ) -> PageDtoJobPartReferenceV2:
        """
        Operation id: listPartsV2
        List jobs

        API call to return a paginated list of [jobs](https://support.phrase.com/hc/en-us/articles/5709686763420-Jobs-TMS-)
        in the given project.

        Use the query parameters to further narrow down the searching criteria.

        - **pageNumber** - A zero-based parameter indicating the page number you wish to retrieve. The total number of pages is
        returned in each response in the `totalPages` field in the top level of the response.
        - **pageSize** - A parameter indicating the size of the page you wish to return.
        This has direct effect on the `totalPages`
        retrieved in each response and can hence influence the number of times to iterate over to get all the jobs.
        - **count** - When set to `true`, the response will not contain the list of jobs (the `content` field) but only the
        counts of elements and pages. Can be used to quickly retrieve the number of elements and pages to iterate over.
        - **workflowLevel** - A non-zero based parameter indicating which
        [workflow steps](https://support.phrase.com/hc/en-us/articles/5709717879324-Workflow-TMS-)
        the returned jobs belong to. If left unspecified, its value is set to 1.
        - **status** - A parameter allowing for filtering only for jobs in a specific status.
        - **assignedUser** - A parameter allowing for filtering only for jobs assigned to a specific user.
        The parameter accepts a user ID.
        - **dueInHours** - A parameter allowing for filtering only for jobs whose due date is less or equal to the number
         of hours specified.
        - **filename** - A parameter allowing for filtering only for jobs with a specific file name.
        - **targetLang** - A parameter allowing for filtering only for jobs with a specific target language.
        - **assignedVendor** - A parameter allowing for filtering only for jobs assigned to a specific vendor.
        The parameter accepts a user ID.
        - **notReady** - A parameter allowing for filtering only jobs that have been imported. When set to `true` the response
         will only contain jobs that have not been imported yet.
         This will also return jobs that have not been imported correctly, e.g. due to an error.

        :param project_uid: str (required), path.
        :param assigned_user: Optional[int] = None (optional), query.
        :param assigned_vendor: Optional[int] = None (optional), query.
        :param count: Optional[bool] = False (optional), query.
        :param due_in_hours: Optional[int] = None (optional), query.
        :param filename: Optional[str] = None (optional), query.
        :param not_ready: Optional[bool] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query.
        :param status: Optional[List[str]] = None (optional), query.
        :param target_lang: Optional[str] = None (optional), query.
        :param workflow_level: Optional[int] = 1 (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoJobPartReferenceV2
        """

        endpoint = f"/api2/v2/projects/{project_uid}/jobs"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "count": count,
            "workflowLevel": workflow_level,
            "status": status,
            "assignedUser": assigned_user,
            "dueInHours": due_in_hours,
            "filename": filename,
            "targetLang": target_lang,
            "assignedVendor": assigned_vendor,
            "notReady": not_ready,
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

        return PageDtoJobPartReferenceV2.model_validate(r.json())

    def list_providers_4(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
    ) -> ProviderListDtoV2:
        """
        Operation id: listProviders_4
        Get suggested providers

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProviderListDtoV2
        """

        endpoint = f"/api2/v2/projects/{project_uid}/jobs/{job_uid}/providers/suggest"

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

        return ProviderListDtoV2.model_validate(r.json())

    def list_segments(
        self,
        job_uid: str,
        project_uid: str,
        begin_index: Optional[int] = 0,
        end_index: Optional[int] = 0,
        phrase_token: Optional[str] = None,
    ) -> SegmentListDto:
        """
        Operation id: listSegments
        Get segments

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param begin_index: Optional[int] = 0 (optional), query.
        :param end_index: Optional[int] = 0 (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SegmentListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/segments"

        params = {"beginIndex": begin_index, "endIndex": end_index}

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

        return SegmentListDto.model_validate(r.json())

    def notify_assigned(
        self,
        project_uid: str,
        notify_job_parts_request_dto: Optional[NotifyJobPartsRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: notifyAssigned
        Notify assigned users

        :param project_uid: str (required), path.
        :param notify_job_parts_request_dto: Optional[NotifyJobPartsRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/notifyAssigned"
        if type(notify_job_parts_request_dto) is dict:
            notify_job_parts_request_dto = NotifyJobPartsRequestDto.model_validate(
                notify_job_parts_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = notify_job_parts_request_dto

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

    def patch_part(
        self,
        job_uid: str,
        project_uid: str,
        job_part_patch_single_dto: Optional[JobPartPatchSingleDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> JobPartExtendedDto:
        """
        Operation id: patchPart
        Patch job

        This API call allows for partial updates to jobs, modifying specific fields without overwriting
        those not included in the update request.

        Differing from [Edit job](#operation/editPart), this call employs a PATCH method, updating only the provided fields
        without altering others. It's beneficial when editing a subset of supported fields is required.

        The call supports the editing of status, due date, and providers. When editing providers, it's essential to submit
        both the ID of the provider and its type (either VENDOR or USER).

        The response will provide a subset of information from [Get job](#operation/getPart).

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param job_part_patch_single_dto: Optional[JobPartPatchSingleDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartExtendedDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}"
        if type(job_part_patch_single_dto) is dict:
            job_part_patch_single_dto = JobPartPatchSingleDto.model_validate(
                job_part_patch_single_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_patch_single_dto

        r = self.client.make_request(
            "PATCH",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return JobPartExtendedDto.model_validate(r.json())

    def patch_update_job_parts(
        self,
        job_part_patch_batch_dto: Optional[JobPartPatchBatchDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> JobPartPatchResultDto:
        """
        Operation id: patchUpdateJobParts
        Edit jobs (with possible partial updates)
        Allows partial update, not breaking whole batch if single job fails and returns list of errors
        :param job_part_patch_batch_dto: Optional[JobPartPatchBatchDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartPatchResultDto
        """

        endpoint = "/api2/v3/jobs"
        if type(job_part_patch_batch_dto) is dict:
            job_part_patch_batch_dto = JobPartPatchBatchDto.model_validate(
                job_part_patch_batch_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_patch_batch_dto

        r = self.client.make_request(
            "PATCH",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return JobPartPatchResultDto.model_validate(r.json())

    def preview_urls(
        self,
        job_uid: str,
        project_uid: str,
        workflow_level: Optional[int] = 1,
        phrase_token: Optional[str] = None,
    ) -> PreviewUrlsDto:
        """
        Operation id: previewUrls
        Get PDF preview

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param workflow_level: Optional[int] = 1 (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PreviewUrlsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/previewUrl"

        params = {"workflowLevel": workflow_level}

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

        return PreviewUrlsDto.model_validate(r.json())

    def pseudo_translate_job_part(
        self,
        job_uid: str,
        project_uid: str,
        pseudo_translate_action_dto: Optional[PseudoTranslateActionDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: pseudoTranslateJobPart
        Pseudo-translates job

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param pseudo_translate_action_dto: Optional[PseudoTranslateActionDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/pseudoTranslate"
        if type(pseudo_translate_action_dto) is dict:
            pseudo_translate_action_dto = PseudoTranslateActionDto.model_validate(
                pseudo_translate_action_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = pseudo_translate_action_dto

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

    def pseudo_translate_v2(
        self,
        project_uid: str,
        pseudo_translate_wrapper_dto: Optional[PseudoTranslateWrapperDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: pseudoTranslateV2
        Pseudo-translate job

        :param project_uid: str (required), path.
        :param pseudo_translate_wrapper_dto: Optional[PseudoTranslateWrapperDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v2/projects/{project_uid}/jobs/pseudoTranslate"
        if type(pseudo_translate_wrapper_dto) is dict:
            pseudo_translate_wrapper_dto = PseudoTranslateWrapperDto.model_validate(
                pseudo_translate_wrapper_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = pseudo_translate_wrapper_dto

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

    def search_parts_in_project(
        self,
        project_uid: str,
        search_jobs_request_dto: Optional[SearchJobsRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchJobsDto:
        """
        Operation id: searchPartsInProject
        Search jobs in project

        This API call can be used to verify (search) which of the provided jobs belong to the specified project. For the jobs
        that belong to the project, a subset of [Get job](#operation/getPart) information will be returned and the rest of the
        jobs will be filtered out.

        :param project_uid: str (required), path.
        :param search_jobs_request_dto: Optional[SearchJobsRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchJobsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/search"
        if type(search_jobs_request_dto) is dict:
            search_jobs_request_dto = SearchJobsRequestDto.model_validate(
                search_jobs_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = search_jobs_request_dto

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

        return SearchJobsDto.model_validate(r.json())

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

    def search_terms_by_job_v2(
        self,
        job_uid: str,
        project_uid: str,
        search_tb_by_job_request_dto: Optional[SearchTbByJobRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchTbResponseListDto:
        """
        Operation id: searchTermsByJobV2
        Search job's term bases
        Search all read term bases assigned to the job
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param search_tb_by_job_request_dto: Optional[SearchTbByJobRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchTbResponseListDto
        """

        endpoint = (
            f"/api2/v2/projects/{project_uid}/jobs/{job_uid}/termBases/searchByJob"
        )
        if type(search_tb_by_job_request_dto) is dict:
            search_tb_by_job_request_dto = SearchTbByJobRequestDto.model_validate(
                search_tb_by_job_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = search_tb_by_job_request_dto

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

        return SearchTbResponseListDto.model_validate(r.json())

    def search_terms_in_text_by_job_v2(
        self,
        job_uid: str,
        project_uid: str,
        search_tb_in_text_by_job_request_dto: Optional[
            SearchTbInTextByJobRequestDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> SearchInTextResponseList2Dto:
        """
        Operation id: searchTermsInTextByJobV2
        Search terms in text
        Search in text in all read term bases assigned to the job
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param search_tb_in_text_by_job_request_dto: Optional[SearchTbInTextByJobRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchInTextResponseList2Dto
        """

        endpoint = f"/api2/v2/projects/{project_uid}/jobs/{job_uid}/termBases/searchInTextByJob"
        if type(search_tb_in_text_by_job_request_dto) is dict:
            search_tb_in_text_by_job_request_dto = (
                SearchTbInTextByJobRequestDto.model_validate(
                    search_tb_in_text_by_job_request_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = search_tb_in_text_by_job_request_dto

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

        return SearchInTextResponseList2Dto.model_validate(r.json())

    def set_status(
        self,
        job_uid: str,
        project_uid: str,
        job_status_change_action_dto: Optional[JobStatusChangeActionDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: setStatus
        Edit job status

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param job_status_change_action_dto: Optional[JobStatusChangeActionDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/setStatus"
        if type(job_status_change_action_dto) is dict:
            job_status_change_action_dto = JobStatusChangeActionDto.model_validate(
                job_status_change_action_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_status_change_action_dto

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

    def split(
        self,
        job_uid: str,
        project_uid: str,
        split_job_action_dto: Optional[SplitJobActionDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> JobPartsDto:
        """
        Operation id: split
        Split job

        Splits job by one of the following methods:
        * **After specific segments** - fill in `segmentOrdinals`
        * **Into X parts** - fill in `partCount`
        * **Into parts with specific size** - fill in `partSize`. partSize represents segment count in each part.
        * **Into parts with specific word count** - fill in `wordCount`
        * **By document parts** - fill in `byDocumentParts`, works only with **PowerPoint** files

        Only one option at a time is allowed.

        Use `splitAllWorkflowSteps` to split in all workflow steps (default: false). When enabled, the split operation will be
        applied to all sibling job parts across all workflow steps in the project.
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param split_job_action_dto: Optional[SplitJobActionDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartsDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/split"
        if type(split_job_action_dto) is dict:
            split_job_action_dto = SplitJobActionDto.model_validate(
                split_job_action_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = split_job_action_dto

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

        return JobPartsDto.model_validate(r.json())

    def status_changes(
        self,
        job_uid: str,
        project_uid: str,
        order: Optional[str] = "ASC",
        phrase_token: Optional[str] = None,
    ) -> JobPartStatusChangesDto:
        """
        Operation id: statusChanges
        Get status changes

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param order: Optional[str] = "ASC" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartStatusChangesDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/statusChanges"

        params = {"order": order}

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

        return JobPartStatusChangesDto.model_validate(r.json())

    def update_source(
        self,
        content_disposition: str,
        project_uid: str,
        memsource: Optional[JobUpdateSourceMeta | dict] = None,
        file_bytes: Optional[bytes] = None,
        phrase_token: Optional[str] = None,
    ) -> JobUpdateSourceResponseDto:
        """
        Operation id: updateSource
        Update source

        API updated source file for specified job

        Job file can be provided directly in the message body.

        Please supply jobs in `Memsource` header.

        For file in the request body provide also the filename in `Content-Disposition` header.

        If a job from a multilingual file is updated, all jobs from the same file are update too even if their UIDs aren't
        listed in the jobs field.

        Accepted metadata:

          - `jobs` - **required** - list of jobs UID reference (maximum size `100`)
          - `preTranslate` - pre translate flag (default `false`)
          - `allowAutomaticPostAnalysis` - if automatic post editing analysis should be created. If not specified then value
                                           is taken from the analyse settings of the project
          - `callbackUrl` - consumer callback

        Job restrictions:
          - job must belong to project specified in path (`projectUid`)
          - job `UID` must be from the first workflow step
          - job cannot be split
          - job cannot be continuous
          - job cannot originate in a connector
          - status in any of the job's workflow steps cannot be a final
            status (`COMPLETED_BY_LINGUIST`, `COMPLETED`, `CANCELLED`)
          - job UIDs must be from the same multilingual file if a multilingual file is updated
          - multiple multilingual files or a mixture of multilingual and other jobs cannot be updated in one call

        File restrictions:
          - file cannot be a `.zip` file

        Example:

        ```
        {
          "jobs": [
            {
                "uid": "jobIn1stWfStepAndNonFinalStatusUid"
            }
          ],
          "preTranslate": false,
          "allowAutomaticPostAnalysis": false
          "callbackUrl": "https://my-shiny-service.com/consumeCallback"
        }
        ```


        :param content_disposition: str (required), header. must match pattern `((inline|attachment); )?(filename\\*=UTF-8''(.+)|filename="?(.+)"?)`.
        :param project_uid: str (required), path.
        :param memsource: Optional[JobUpdateSourceMeta | dict] = None (optional), header.
        :param file_bytes: Optional[bytes] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobUpdateSourceResponseDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/source"
        if type(memsource) is dict:
            memsource = JobUpdateSourceMeta.model_validate(memsource)

        params = {}

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

        return JobUpdateSourceResponseDto.model_validate(r.json())

    def update_target(
        self,
        project_uid: str,
        content_disposition: Optional[str] = None,
        memsource: Optional[JobUpdateTargetMeta | dict] = None,
        file_bytes: Optional[bytes] = None,
        phrase_token: Optional[str] = None,
    ) -> JobUpdateSourceResponseDto:
        """
        Operation id: updateTarget
        Update target

        API update target file for specified job

        Job file can be provided directly in the message body.

        Please supply jobs in `Memsource` header.

        For file in the request body provide also the filename in `Content-Disposition` header.

        Accepted metadata:

          - `jobs` - **required** - list of jobs UID reference (maximum size `1`)
          - `propagateConfirmedToTm` - sets if confirmed segments should be stored in TM (default value: true)
          - `callbackUrl` - consumer callback
          - `targetSegmentationRule` - ID reference to segmentation rule of organization to use for update target
          - `unconfirmChangedSegments` - sets if segments should stay unconfirmed

        Job restrictions:
          - job must belong to project specified in path (`projectUid`)
          - job cannot be split
          - job cannot be continuous
          - job cannot originate in a connector
          - job cannot have different file extension than original file

        File restrictions:
          - file cannot be a `.zip` file
          - update target is not allowed for jobs with file extensions: po, tbx, tmx, ttx, ts
          - update target for multilingual jobs works only with following file extensions: xliff, xlsx, csv

        Example:

        ```
        {
          "jobs": [
            {
                "uid": "jobUid"
            }
          ],
          "propagateConfirmedToTm": true,
          "targetSegmentationRule": {
                "id": "1"
           },
          "callbackUrl": "https://my-shiny-service.com/consumeCallback"
        }
        ```


        :param project_uid: str (required), path.
        :param content_disposition: Optional[str] = None (optional), header. must match pattern `((inline|attachment); )?(filename\\*=UTF-8''(.+)|filename="?(.+)"?)`.
        :param memsource: Optional[JobUpdateTargetMeta | dict] = None (optional), header.
        :param file_bytes: Optional[bytes] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobUpdateSourceResponseDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/target"
        if type(memsource) is dict:
            memsource = JobUpdateTargetMeta.model_validate(memsource)

        params = {}

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

        return JobUpdateSourceResponseDto.model_validate(r.json())

    def upload_handover_file(
        self,
        content_disposition: str,
        memsource: UploadHandoverFileMeta | dict,
        project_uid: str,
        content_length: Optional[int] = None,
        file_bytes: Optional[bytes] = None,
        phrase_token: Optional[str] = None,
    ) -> FileHandoverDto:
        """
        Operation id: uploadHandoverFile
        Upload handover file

        For following jobs the handover file is not supported:
        * Continuous jobs
        * Jobs from connectors
        * Split jobs
        * Multilingual jobs

        :param content_disposition: str (required), header. must match pattern `((inline|attachment); )?(filename\\*=UTF-8''(.+)|filename="?(.+)"?)`.
        :param memsource: UploadHandoverFileMeta | dict (required), header.
        :param project_uid: str (required), path.
        :param content_length: Optional[int] = None (optional), header.
        :param file_bytes: Optional[bytes] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileHandoverDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/fileHandovers"
        if type(memsource) is dict:
            memsource = UploadHandoverFileMeta.model_validate(memsource)

        params = {}

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
            "Content-Disposition": (
                content_disposition.model_dump_json()
                if hasattr(content_disposition, "model_dump_json")
                else (
                    json.dumps(content_disposition)
                    if False and not isinstance(content_disposition, str)
                    else str(content_disposition)
                )
            ),
            "Content-Length": (
                content_length.model_dump_json()
                if hasattr(content_length, "model_dump_json")
                else (
                    json.dumps(content_length)
                    if False and not isinstance(content_length, str)
                    else str(content_length)
                )
            ),
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        payload = None
        content = file_bytes

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

        return FileHandoverDto.model_validate(r.json())

    def web_editor_link_v2(
        self,
        project_uid: str,
        create_web_editor_link_dto_v2: Optional[CreateWebEditorLinkDtoV2 | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> WebEditorLinkDtoV2:
        """
        Operation id: webEditorLinkV2
        Get Web Editor URL

        Possible warning codes are:
          - `NOT_ACCEPTED_BY_LINGUIST` - Job is not accepted by linguist
          - `NOT_ASSIGNED_TO_LINGUIST` - Job is not assigned to linguist
          - `PDF` - One of requested jobs is PDF
          - `PREVIOUS_WORKFLOW_NOT_COMPLETED` - Previous workflow step is not completed
          - `PREVIOUS_WORKFLOW_NOT_COMPLETED_STRICT` - Previous workflow step is not completed and project has strictWorkflowFinish set to true
          - `IN_DELIVERED_STATE` - Jobs in DELIVERED state
          - `IN_COMPLETED_STATE` - Jobs in COMPLETED state
          - `IN_REJECTED_STATE` - Jobs in REJECTED state

        Possible error codes are:
          - `ASSIGNED_TO_OTHER_USER` - Job is accepted by other user
          - `NOT_UNIQUE_TARGET_LANG` - Requested jobs contains different target locales
          - `TOO_MANY_SEGMENTS` - Count of requested job's segments is higher than **40000**
          - `TOO_MANY_JOBS` - Count of requested jobs is higher than **290**
          - `COMPLETED_JOINED_WITH_OTHER` - Jobs in COMPLETED state cannot be joined with jobs in other states
          - `DELIVERED_JOINED_WITH_OTHER` - Jobs in DELIVERED state cannot be joined with jobs in other states
          - `REJECTED_JOINED_WITH_OTHER` - Jobs in REJECTED state cannot be joined with jobs in other states

        Warning response example:
        ```
        {
            "warnings": [
                {
                    "message": "Not accepted by linguist",
                    "args": {
                        "jobs": [
                            "abcd1234"
                        ]
                    },
                    "code": "NOT_ACCEPTED_BY_LINGUIST"
                },
                {
                    "message": "Previous workflow step not completed",
                    "args": {
                        "jobs": [
                            "abcd1234"
                        ]
                    },
                    "code": "PREVIOUS_WORKFLOW_NOT_COMPLETED"
                }
            ],
            "url": "/web/job/abcd1234-efgh5678/translate"
        }
        ```

        Error response example:
        Status: `400 Bad Request`
        ```
        {
            "errorCode": "NOT_UNIQUE_TARGET_LANG",
            "errorDescription": "Only files with identical target languages can be joined",
            "errorDetails": [
                {
                    "code": "NOT_UNIQUE_TARGET_LANG",
                    "args": {
                        "targetLocales": [
                            "de",
                            "en"
                        ]
                    },
                    "message": "Only files with identical target languages can be joined"
                },
                {
                    "code": "TOO_MANY_SEGMENTS",
                    "args": {
                        "maxSegments": 40000,
                        "segments": 400009
                    },
                    "message": "Up to 40000 segments can be opened in the CAT Web Editor, job has 400009 segments"
                }
            ]
        }
        ```

        :param project_uid: str (required), path.
        :param create_web_editor_link_dto_v2: Optional[CreateWebEditorLinkDtoV2 | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: WebEditorLinkDtoV2
        """

        endpoint = f"/api2/v2/projects/{project_uid}/jobs/webEditor"
        if type(create_web_editor_link_dto_v2) is dict:
            create_web_editor_link_dto_v2 = CreateWebEditorLinkDtoV2.model_validate(
                create_web_editor_link_dto_v2
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_web_editor_link_dto_v2

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

        return WebEditorLinkDtoV2.model_validate(r.json())

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
