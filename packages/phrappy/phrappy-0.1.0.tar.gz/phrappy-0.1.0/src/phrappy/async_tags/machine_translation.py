from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import MachineTranslateResponse, TranslationRequestExtendedDto


class MachineTranslationOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def machine_translation(
        self,
        mt_settings_uid: str,
        translation_request_extended_dto: Optional[
            TranslationRequestExtendedDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> MachineTranslateResponse:
        """
        Operation id: machineTranslation
        Translate with MT

        :param mt_settings_uid: str (required), path.
        :param translation_request_extended_dto: Optional[TranslationRequestExtendedDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MachineTranslateResponse
        """

        endpoint = f"/api2/v1/machineTranslations/{mt_settings_uid}/translate"
        if type(translation_request_extended_dto) is dict:
            translation_request_extended_dto = (
                TranslationRequestExtendedDto.model_validate(
                    translation_request_extended_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = translation_request_extended_dto

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
