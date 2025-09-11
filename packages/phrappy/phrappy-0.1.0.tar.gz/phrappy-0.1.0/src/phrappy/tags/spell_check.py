from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    DictionaryItemDto,
    SpellCheckRequestDto,
    SpellCheckResponseDto,
    SuggestRequestDto,
    SuggestResponseDto,
)


class SpellCheckOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def add_word(
        self,
        dictionary_item_dto: Optional[DictionaryItemDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: addWord
        Add word to dictionary

        :param dictionary_item_dto: Optional[DictionaryItemDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = "/api2/v1/spellCheck/words"
        if type(dictionary_item_dto) is dict:
            dictionary_item_dto = DictionaryItemDto.model_validate(dictionary_item_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = dictionary_item_dto

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

    def check(
        self,
        spell_check_request_dto: Optional[SpellCheckRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SpellCheckResponseDto:
        """
        Operation id: check
        Spell check
        Spell check using the settings of the user's organization
        :param spell_check_request_dto: Optional[SpellCheckRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SpellCheckResponseDto
        """

        endpoint = "/api2/v1/spellCheck/check"
        if type(spell_check_request_dto) is dict:
            spell_check_request_dto = SpellCheckRequestDto.model_validate(
                spell_check_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = spell_check_request_dto

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

        return SpellCheckResponseDto.model_validate(r.json())

    def check_by_job(
        self,
        job_uid: str,
        spell_check_request_dto: Optional[SpellCheckRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SpellCheckResponseDto:
        """
        Operation id: checkByJob
        Spell check for job
        Spell check using the settings from the project of the job
        :param job_uid: str (required), path.
        :param spell_check_request_dto: Optional[SpellCheckRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SpellCheckResponseDto
        """

        endpoint = f"/api2/v1/spellCheck/check/{job_uid}"
        if type(spell_check_request_dto) is dict:
            spell_check_request_dto = SpellCheckRequestDto.model_validate(
                spell_check_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = spell_check_request_dto

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

        return SpellCheckResponseDto.model_validate(r.json())

    def suggest(
        self,
        suggest_request_dto: Optional[SuggestRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SuggestResponseDto:
        """
        Operation id: suggest
        Suggest a word
        Spell check suggest using the users's spell check dictionary
        :param suggest_request_dto: Optional[SuggestRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SuggestResponseDto
        """

        endpoint = "/api2/v1/spellCheck/suggest"
        if type(suggest_request_dto) is dict:
            suggest_request_dto = SuggestRequestDto.model_validate(suggest_request_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = suggest_request_dto

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

        return SuggestResponseDto.model_validate(r.json())
