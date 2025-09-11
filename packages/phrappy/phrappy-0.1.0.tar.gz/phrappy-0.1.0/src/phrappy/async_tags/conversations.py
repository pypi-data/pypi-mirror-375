from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    AddCommentDto,
    AddLqaCommentResultDto,
    AddPlainCommentResultDto,
    ConversationListDto,
    CreateLqaConversationDto,
    CreatePlainConversationDto,
    EditLqaConversationDto,
    EditPlainConversationDto,
    FindConversationsDto,
    FindConversationsForProjectDto,
    LQAConversationDto,
    LQAConversationsListDto,
    PageDtoCommonConversationDto,
    PlainConversationDto,
    PlainConversationsListDto,
)


class ConversationsOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def add_lqa_comment_v2(
        self,
        conversation_id: str,
        job_uid: str,
        add_comment_dto: Optional[AddCommentDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AddLqaCommentResultDto:
        """
        Operation id: addLQACommentV2
        Add LQA comment

        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.
        :param add_comment_dto: Optional[AddCommentDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AddLqaCommentResultDto
        """

        endpoint = (
            f"/api2/v2/jobs/{job_uid}/conversations/lqas/{conversation_id}/comments"
        )
        if type(add_comment_dto) is dict:
            add_comment_dto = AddCommentDto.model_validate(add_comment_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = add_comment_dto

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

        return AddLqaCommentResultDto.model_validate(r.json())

    async def add_plain_comment_v3(
        self,
        conversation_id: str,
        job_uid: str,
        add_comment_dto: Optional[AddCommentDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AddPlainCommentResultDto:
        """
        Operation id: addPlainCommentV3
        Add plain comment

        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.
        :param add_comment_dto: Optional[AddCommentDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AddPlainCommentResultDto
        """

        endpoint = (
            f"/api2/v3/jobs/{job_uid}/conversations/plains/{conversation_id}/comments"
        )
        if type(add_comment_dto) is dict:
            add_comment_dto = AddCommentDto.model_validate(add_comment_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = add_comment_dto

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

        return AddPlainCommentResultDto.model_validate(r.json())

    async def create_lqa_conversation_v2(
        self,
        job_uid: str,
        create_lqa_conversation_dto: Optional[CreateLqaConversationDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LQAConversationDto:
        """
        Operation id: createLqaConversationV2
        Create LQA conversation

        :param job_uid: str (required), path.
        :param create_lqa_conversation_dto: Optional[CreateLqaConversationDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LQAConversationDto
        """

        endpoint = f"/api2/v2/jobs/{job_uid}/conversations/lqas"
        if type(create_lqa_conversation_dto) is dict:
            create_lqa_conversation_dto = CreateLqaConversationDto.model_validate(
                create_lqa_conversation_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_lqa_conversation_dto

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

        return LQAConversationDto.model_validate(r.json())

    async def create_segment_target_conversation_v3(
        self,
        job_uid: str,
        create_plain_conversation_dto: Optional[
            CreatePlainConversationDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> PlainConversationDto:
        """
        Operation id: createSegmentTargetConversationV3
        Create plain conversation

        :param job_uid: str (required), path.
        :param create_plain_conversation_dto: Optional[CreatePlainConversationDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PlainConversationDto
        """

        endpoint = f"/api2/v3/jobs/{job_uid}/conversations/plains"
        if type(create_plain_conversation_dto) is dict:
            create_plain_conversation_dto = CreatePlainConversationDto.model_validate(
                create_plain_conversation_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_plain_conversation_dto

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

        return PlainConversationDto.model_validate(r.json())

    async def delete_lqa_comment(
        self,
        comment_id: str,
        conversation_id: str,
        job_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteLQAComment
        Delete LQA comment

        :param comment_id: str (required), path.
        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/jobs/{job_uid}/conversations/lqas/{conversation_id}/comments/{comment_id}"

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

    async def delete_lqa_conversation(
        self,
        conversation_id: str,
        job_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteLQAConversation
        Delete LQA conversation

        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/jobs/{job_uid}/conversations/lqas/{conversation_id}"

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

    async def delete_plain_comment(
        self,
        comment_id: str,
        conversation_id: str,
        job_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deletePlainComment
        Delete plain comment

        :param comment_id: str (required), path.
        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/jobs/{job_uid}/conversations/plains/{conversation_id}/comments/{comment_id}"

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

    async def delete_plain_conversation(
        self,
        conversation_id: str,
        job_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deletePlainConversation
        Delete plain conversation

        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/jobs/{job_uid}/conversations/plains/{conversation_id}"

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

    async def find_conversations(
        self,
        find_conversations_dto: Optional[FindConversationsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ConversationListDto:
        """
        Operation id: findConversations
        Find all conversation

        :param find_conversations_dto: Optional[FindConversationsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConversationListDto
        """

        endpoint = "/api2/v1/jobs/conversations/find"
        if type(find_conversations_dto) is dict:
            find_conversations_dto = FindConversationsDto.model_validate(
                find_conversations_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = find_conversations_dto

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

        return ConversationListDto.model_validate(r.json())

    async def get_lqa_conversation(
        self,
        conversation_id: str,
        job_uid: str,
        phrase_token: Optional[str] = None,
    ) -> LQAConversationDto:
        """
        Operation id: getLQAConversation
        Get LQA conversation

        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LQAConversationDto
        """

        endpoint = f"/api2/v1/jobs/{job_uid}/conversations/lqas/{conversation_id}"

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

        return LQAConversationDto.model_validate(r.json())

    async def get_plain_conversation(
        self,
        conversation_id: str,
        job_uid: str,
        phrase_token: Optional[str] = None,
    ) -> PlainConversationDto:
        """
        Operation id: getPlainConversation
        Get plain conversation

        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PlainConversationDto
        """

        endpoint = f"/api2/v1/jobs/{job_uid}/conversations/plains/{conversation_id}"

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

        return PlainConversationDto.model_validate(r.json())

    async def list_all_conversations(
        self,
        job_uid: str,
        include_deleted: Optional[bool] = False,
        since: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> ConversationListDto:
        """
        Operation id: listAllConversations
        List all conversations

        :param job_uid: str (required), path.
        :param include_deleted: Optional[bool] = False (optional), query.
        :param since: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConversationListDto
        """

        endpoint = f"/api2/v1/jobs/{job_uid}/conversations"

        params = {"includeDeleted": include_deleted, "since": since}

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

        return ConversationListDto.model_validate(r.json())

    async def list_lqa_conversations(
        self,
        job_uid: str,
        include_deleted: Optional[bool] = False,
        since: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> LQAConversationsListDto:
        """
        Operation id: listLQAConversations
        List LQA conversations

        :param job_uid: str (required), path.
        :param include_deleted: Optional[bool] = False (optional), query.
        :param since: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LQAConversationsListDto
        """

        endpoint = f"/api2/v1/jobs/{job_uid}/conversations/lqas"

        params = {"includeDeleted": include_deleted, "since": since}

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

        return LQAConversationsListDto.model_validate(r.json())

    async def list_plain_conversations(
        self,
        job_uid: str,
        include_deleted: Optional[bool] = False,
        since: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PlainConversationsListDto:
        """
        Operation id: listPlainConversations
        List plain conversations

        :param job_uid: str (required), path.
        :param include_deleted: Optional[bool] = False (optional), query.
        :param since: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PlainConversationsListDto
        """

        endpoint = f"/api2/v1/jobs/{job_uid}/conversations/plains"

        params = {"includeDeleted": include_deleted, "since": since}

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

        return PlainConversationsListDto.model_validate(r.json())

    async def search_by_project(
        self,
        find_conversations_for_project_dto: Optional[
            FindConversationsForProjectDto | dict
        ] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoCommonConversationDto:
        """
        Operation id: searchByProject
        Search conversation by project
        This endpoint is allowed only to PM and ADMIN roles.
        :param find_conversations_for_project_dto: Optional[FindConversationsForProjectDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCommonConversationDto
        """

        endpoint = "/api2/v1/jobs/conversations/searchByProject"
        if type(find_conversations_for_project_dto) is dict:
            find_conversations_for_project_dto = (
                FindConversationsForProjectDto.model_validate(
                    find_conversations_for_project_dto
                )
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = find_conversations_for_project_dto

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

        return PageDtoCommonConversationDto.model_validate(r.json())

    async def update_lqa_comment_v2(
        self,
        comment_id: str,
        conversation_id: str,
        job_uid: str,
        add_comment_dto: Optional[AddCommentDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LQAConversationDto:
        """
        Operation id: updateLQACommentV2
        Edit LQA comment

        :param comment_id: str (required), path.
        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.
        :param add_comment_dto: Optional[AddCommentDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LQAConversationDto
        """

        endpoint = f"/api2/v2/jobs/{job_uid}/conversations/lqas/{conversation_id}/comments/{comment_id}"
        if type(add_comment_dto) is dict:
            add_comment_dto = AddCommentDto.model_validate(add_comment_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = add_comment_dto

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

        return LQAConversationDto.model_validate(r.json())

    async def update_lqa_conversation_v2(
        self,
        conversation_id: str,
        job_uid: str,
        edit_lqa_conversation_dto: Optional[EditLqaConversationDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LQAConversationDto:
        """
        Operation id: updateLqaConversationV2
        Update LQA conversation

        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.
        :param edit_lqa_conversation_dto: Optional[EditLqaConversationDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LQAConversationDto
        """

        endpoint = f"/api2/v2/jobs/{job_uid}/conversations/lqas/{conversation_id}"
        if type(edit_lqa_conversation_dto) is dict:
            edit_lqa_conversation_dto = EditLqaConversationDto.model_validate(
                edit_lqa_conversation_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = edit_lqa_conversation_dto

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

        return LQAConversationDto.model_validate(r.json())

    async def update_plain_comment_v3(
        self,
        comment_id: str,
        conversation_id: str,
        job_uid: str,
        add_comment_dto: Optional[AddCommentDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> PlainConversationDto:
        """
        Operation id: updatePlainCommentV3
        Edit plain comment

        :param comment_id: str (required), path.
        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.
        :param add_comment_dto: Optional[AddCommentDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PlainConversationDto
        """

        endpoint = f"/api2/v3/jobs/{job_uid}/conversations/plains/{conversation_id}/comments/{comment_id}"
        if type(add_comment_dto) is dict:
            add_comment_dto = AddCommentDto.model_validate(add_comment_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = add_comment_dto

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

        return PlainConversationDto.model_validate(r.json())

    async def update_plain_conversation(
        self,
        conversation_id: str,
        job_uid: str,
        edit_plain_conversation_dto: Optional[EditPlainConversationDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> PlainConversationDto:
        """
        Operation id: updatePlainConversation
        Edit plain conversation

        :param conversation_id: str (required), path.
        :param job_uid: str (required), path.
        :param edit_plain_conversation_dto: Optional[EditPlainConversationDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PlainConversationDto
        """

        endpoint = f"/api2/v1/jobs/{job_uid}/conversations/plains/{conversation_id}"
        if type(edit_plain_conversation_dto) is dict:
            edit_plain_conversation_dto = EditPlainConversationDto.model_validate(
                edit_plain_conversation_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = edit_plain_conversation_dto

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

        return PlainConversationDto.model_validate(r.json())
