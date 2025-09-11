from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import json

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    CreateSegmentationRuleMeta,
    EditSegmentationRuleDto,
    PageDtoSegmentationRuleDto,
    SegmentationRuleDto,
    SegmentationRulesOwnersDto,
)


class SegmentationRulesOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def create_segmentation_rule(
        self,
        file_bytes: bytes,
        seg_rule: CreateSegmentationRuleMeta | dict,
        phrase_token: Optional[str] = None,
    ) -> SegmentationRuleDto:
        """
        Operation id: createSegmentationRule
        Create segmentation rule
        Creates new Segmentation Rule with file and segRule JSON Object as header parameter. The same object is used for GET action.
        :param file_bytes: bytes (required), body.
        :param seg_rule: CreateSegmentationRuleMeta | dict (required), header.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SegmentationRuleDto
        """

        endpoint = "/api2/v1/segmentationRules"
        if type(seg_rule) is dict:
            seg_rule = CreateSegmentationRuleMeta.model_validate(seg_rule)

        params = {}

        headers = {
            "segRule": (
                seg_rule.model_dump_json()
                if hasattr(seg_rule, "model_dump_json")
                else (
                    json.dumps(seg_rule)
                    if True and not isinstance(seg_rule, str)
                    else str(seg_rule)
                )
            )
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        payload = None
        content = file_bytes

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

        return SegmentationRuleDto.model_validate(r.json())

    async def deletes_segmentation_rule(
        self,
        seg_rule_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deletesSegmentationRule
        Delete segmentation rule

        :param seg_rule_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/segmentationRules/{seg_rule_uid}"

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

    async def export_default_segmentation_rules(
        self,
        locale: str,
        format: Optional[str] = "SRX",
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: exportDefaultSegmentationRules
        Export default segmentation rules

        :param locale: str (required), path.
        :param format: Optional[str] = "SRX" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/segmentationRules/{locale}/exportDefault"

        params = {"format": format}

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

    async def export_segmentation_rule(
        self,
        seg_rule_uid: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: exportSegmentationRule
        Export segmentation rule

        :param seg_rule_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/segmentationRules/{seg_rule_uid}/export"

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

    async def get_list_of_segmentation_rules(
        self,
        filename: Optional[str] = None,
        language: Optional[str] = None,
        languages: Optional[List[str]] = None,
        locales: Optional[List[str]] = None,
        name: Optional[str] = None,
        order: Optional[str] = "ASC",
        owner_uid: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        primary: Optional[bool] = None,
        sort: Optional[str] = "DATE_CREATED",
        phrase_token: Optional[str] = None,
    ) -> PageDtoSegmentationRuleDto:
        """
        Operation id: getListOfSegmentationRules
        List segmentation rules

        :param filename: Optional[str] = None (optional), query. Filter by filename.
        :param language: Optional[str] = None (optional), query. Filter by language.
        :param languages: Optional[List[str]] = None (optional), query. Filter by multiple languages.
        :param locales: Optional[List[str]] = None (optional), query.
        :param name: Optional[str] = None (optional), query. Filter by name.
        :param order: Optional[str] = "ASC" (optional), query.
        :param owner_uid: Optional[str] = None (optional), query. Filter by owner.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param primary: Optional[bool] = None (optional), query. Filter by the primary field.
        :param sort: Optional[str] = "DATE_CREATED" (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoSegmentationRuleDto
        """

        endpoint = "/api2/v1/segmentationRules"

        params = {
            "locales": locales,
            "pageNumber": page_number,
            "pageSize": page_size,
            "sort": sort,
            "order": order,
            "name": name,
            "language": language,
            "languages": languages,
            "filename": filename,
            "primary": primary,
            "ownerUid": owner_uid,
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

        return PageDtoSegmentationRuleDto.model_validate(r.json())

    async def get_segmentation_rule(
        self,
        seg_rule_uid: int,
        phrase_token: Optional[str] = None,
    ) -> SegmentationRuleDto:
        """
        Operation id: getSegmentationRule
        Get segmentation rule

        :param seg_rule_uid: int (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SegmentationRuleDto
        """

        endpoint = f"/api2/v1/segmentationRules/{seg_rule_uid}"

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

        return SegmentationRuleDto.model_validate(r.json())

    async def get_segmentation_rules_owners(
        self,
        phrase_token: Optional[str] = None,
    ) -> SegmentationRulesOwnersDto:
        """
        Operation id: getSegmentationRulesOwners
        Get owners of segmentation rules


        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SegmentationRulesOwnersDto
        """

        endpoint = "/api2/v1/segmentationRules/owners"

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

        return SegmentationRulesOwnersDto.model_validate(r.json())

    async def updates_segmentation_rule(
        self,
        seg_rule_uid: int,
        edit_segmentation_rule_dto: Optional[EditSegmentationRuleDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SegmentationRuleDto:
        """
        Operation id: updatesSegmentationRule
        Edit segmentation rule

        :param seg_rule_uid: int (required), path.
        :param edit_segmentation_rule_dto: Optional[EditSegmentationRuleDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SegmentationRuleDto
        """

        endpoint = f"/api2/v1/segmentationRules/{seg_rule_uid}"
        if type(edit_segmentation_rule_dto) is dict:
            edit_segmentation_rule_dto = EditSegmentationRuleDto.model_validate(
                edit_segmentation_rule_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = edit_segmentation_rule_dto

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

        return SegmentationRuleDto.model_validate(r.json())
