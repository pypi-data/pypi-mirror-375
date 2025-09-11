from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    AsyncRequestWrapperDto,
    AsyncRequestWrapperV2Dto,
    HumanTranslateJobsDto,
    MachineTranslateResponse,
    PreTranslateJobsV3Dto,
    TranslationRequestDto,
)


class TranslationOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def human_translate(
        self,
        project_uid: str,
        human_translate_jobs_dto: Optional[HumanTranslateJobsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AsyncRequestWrapperDto:
        """
        Operation id: humanTranslate
        Human translate (Gengo or Unbabel)

        :param project_uid: str (required), path.
        :param human_translate_jobs_dto: Optional[HumanTranslateJobsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/humanTranslate"
        if type(human_translate_jobs_dto) is dict:
            human_translate_jobs_dto = HumanTranslateJobsDto.model_validate(
                human_translate_jobs_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = human_translate_jobs_dto

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

        return AsyncRequestWrapperDto.model_validate(r.json())

    async def machine_translation_job(
        self,
        job_uid: str,
        project_uid: str,
        translation_request_dto: Optional[TranslationRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> MachineTranslateResponse:
        """
        Operation id: machineTranslationJob
        Translate using machine translation
        Configured machine translate settings is used
        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param translation_request_dto: Optional[TranslationRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MachineTranslateResponse
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/translations/translateWithMachineTranslation"
        if type(translation_request_dto) is dict:
            translation_request_dto = TranslationRequestDto.model_validate(
                translation_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = translation_request_dto

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

        return MachineTranslateResponse.model_validate(r.json())

    async def pre_translate_v3(
        self,
        project_uid: str,
        pre_translate_jobs_v3_dto: Optional[PreTranslateJobsV3Dto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AsyncRequestWrapperV2Dto:
        """
        Operation id: preTranslateV3
        Pre-translate job

        :param project_uid: str (required), path.
        :param pre_translate_jobs_v3_dto: Optional[PreTranslateJobsV3Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperV2Dto
        """

        endpoint = f"/api2/v3/projects/{project_uid}/jobs/preTranslate"
        if type(pre_translate_jobs_v3_dto) is dict:
            pre_translate_jobs_v3_dto = PreTranslateJobsV3Dto.model_validate(
                pre_translate_jobs_v3_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = pre_translate_jobs_v3_dto

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
