from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import json

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    PageDtoTranslationPriceListDto,
    PageDtoTranslationPriceSetDto,
    PriceListForImport,
    TranslationPriceListCreateDto,
    TranslationPriceListDto,
    TranslationPriceSetBulkDeleteDto,
    TranslationPriceSetBulkMinimumPricesDto,
    TranslationPriceSetBulkPricesDto,
    TranslationPriceSetCreateDto,
    TranslationPriceSetListDto,
)


class PriceListOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def clone_price_list(
        self,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
    ) -> TranslationPriceListDto:
        """
        Operation id: clonePriceList
        Clone price list

        :param price_list_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}/clone"

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

        return TranslationPriceListDto.model_validate(r.json())

    async def create_language_pair(
        self,
        price_list_uid: str,
        translation_price_set_create_dto: Optional[
            TranslationPriceSetCreateDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> TranslationPriceSetListDto:
        """
        Operation id: createLanguagePair
        Add language pairs

        :param price_list_uid: str (required), path.
        :param translation_price_set_create_dto: Optional[TranslationPriceSetCreateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceSetListDto
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets"
        if type(translation_price_set_create_dto) is dict:
            translation_price_set_create_dto = (
                TranslationPriceSetCreateDto.model_validate(
                    translation_price_set_create_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = translation_price_set_create_dto

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

        return TranslationPriceSetListDto.model_validate(r.json())

    async def create_price_list(
        self,
        translation_price_list_create_dto: Optional[
            TranslationPriceListCreateDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> TranslationPriceListDto:
        """
        Operation id: createPriceList
        Create price list

        :param translation_price_list_create_dto: Optional[TranslationPriceListCreateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """

        endpoint = "/api2/v1/priceLists"
        if type(translation_price_list_create_dto) is dict:
            translation_price_list_create_dto = (
                TranslationPriceListCreateDto.model_validate(
                    translation_price_list_create_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = translation_price_list_create_dto

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

        return TranslationPriceListDto.model_validate(r.json())

    async def delete_language_pair(
        self,
        price_list_uid: str,
        source_language: str,
        target_language: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteLanguagePair
        Remove language pair

        :param price_list_uid: str (required), path.
        :param source_language: str (required), path.
        :param target_language: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets/{source_language}/{target_language}"

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

    async def delete_language_pairs(
        self,
        price_list_uid: str,
        translation_price_set_bulk_delete_dto: Optional[
            TranslationPriceSetBulkDeleteDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteLanguagePairs
        Remove language pairs

        :param price_list_uid: str (required), path.
        :param translation_price_set_bulk_delete_dto: Optional[TranslationPriceSetBulkDeleteDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets"
        if type(translation_price_set_bulk_delete_dto) is dict:
            translation_price_set_bulk_delete_dto = (
                TranslationPriceSetBulkDeleteDto.model_validate(
                    translation_price_set_bulk_delete_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = translation_price_set_bulk_delete_dto

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

    async def delete_price_list(
        self,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deletePriceList
        Delete price list

        :param price_list_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}"

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

    async def export_price_list(
        self,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: exportPriceList
        Export translation price list

        :param price_list_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        !!! N.B.: API docs have no 200 range response declared, so falling back to returning the raw bytes from the API response.

        :return: bytes
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}/export"

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

        return await r.aread()

    async def get_list_of_price_list(
        self,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoTranslationPriceListDto:
        """
        Operation id: getListOfPriceList
        List price lists

        :param name: Optional[str] = None (optional), query. Filter for name.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTranslationPriceListDto
        """

        endpoint = "/api2/v1/priceLists"

        params = {"pageNumber": page_number, "pageSize": page_size, "name": name}

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

        return PageDtoTranslationPriceListDto.model_validate(r.json())

    async def get_price_list(
        self,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
    ) -> TranslationPriceListDto:
        """
        Operation id: getPriceList
        Get price list

        :param price_list_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}"

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

        return TranslationPriceListDto.model_validate(r.json())

    async def get_prices_with_workflow_steps(
        self,
        price_list_uid: str,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        source_languages: Optional[List[str]] = None,
        target_languages: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoTranslationPriceSetDto:
        """
        Operation id: getPricesWithWorkflowSteps
        List price sets

        :param price_list_uid: str (required), path.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param source_languages: Optional[List[str]] = None (optional), query.
        :param target_languages: Optional[List[str]] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTranslationPriceSetDto
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sourceLanguages": source_languages,
            "targetLanguages": target_languages,
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

        return PageDtoTranslationPriceSetDto.model_validate(r.json())

    async def import_price_list(
        self,
        file: bytes,
        price_list_uid: str,
        content_type: str = "multipart/form-data",
        filename: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PriceListForImport:
        """
        Operation id: importPriceList
        Import translation price list

        :param file: bytes (required), formData.
        :param price_list_uid: str (required), path.
        :param content_type: str = "multipart/form-data" (required), header.

        :param filename: Optional name for the uploaded file; defaults to field name.
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PriceListForImport
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}/import"

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

        return PriceListForImport.model_validate(r.json())

    async def set_minimum_price_for_set(
        self,
        price_list_uid: str,
        translation_price_set_bulk_minimum_prices_dto: Optional[
            TranslationPriceSetBulkMinimumPricesDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> TranslationPriceListDto:
        """
        Operation id: setMinimumPriceForSet
        Edit minimum prices

        :param price_list_uid: str (required), path.
        :param translation_price_set_bulk_minimum_prices_dto: Optional[TranslationPriceSetBulkMinimumPricesDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets/minimumPrices"
        if type(translation_price_set_bulk_minimum_prices_dto) is dict:
            translation_price_set_bulk_minimum_prices_dto = (
                TranslationPriceSetBulkMinimumPricesDto.model_validate(
                    translation_price_set_bulk_minimum_prices_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = translation_price_set_bulk_minimum_prices_dto

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

        return TranslationPriceListDto.model_validate(r.json())

    async def set_prices(
        self,
        price_list_uid: str,
        translation_price_set_bulk_prices_dto: Optional[
            TranslationPriceSetBulkPricesDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> TranslationPriceListDto:
        """
        Operation id: setPrices
        Edit prices
        If object contains only price, all languages and workflow steps will be updated
        :param price_list_uid: str (required), path.
        :param translation_price_set_bulk_prices_dto: Optional[TranslationPriceSetBulkPricesDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets/prices"
        if type(translation_price_set_bulk_prices_dto) is dict:
            translation_price_set_bulk_prices_dto = (
                TranslationPriceSetBulkPricesDto.model_validate(
                    translation_price_set_bulk_prices_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = translation_price_set_bulk_prices_dto

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

        return TranslationPriceListDto.model_validate(r.json())

    async def update_price_list(
        self,
        price_list_uid: str,
        translation_price_list_create_dto: Optional[
            TranslationPriceListCreateDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> TranslationPriceListDto:
        """
        Operation id: updatePriceList
        Update price list

        :param price_list_uid: str (required), path.
        :param translation_price_list_create_dto: Optional[TranslationPriceListCreateDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """

        endpoint = f"/api2/v1/priceLists/{price_list_uid}"
        if type(translation_price_list_create_dto) is dict:
            translation_price_list_create_dto = (
                TranslationPriceListCreateDto.model_validate(
                    translation_price_list_create_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = translation_price_list_create_dto

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

        return TranslationPriceListDto.model_validate(r.json())
