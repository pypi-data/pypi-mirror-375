from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    PageDtoAssignedJobDto,
    PageDtoLastLoginDto,
    PageDtoProjectReference,
    PageDtoString,
    PageDtoUserDto,
    PageDtoWorkflowStepReference,
    UserCreateDto,
    UserDetailsDtoV3Union,
    UserDto,
    UserEditDto,
    UserPasswordEditDto,
    UserStatisticsListDto,
)


class UserOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def cancel_deletion(
        self,
        user_uid: str,
        phrase_token: Optional[str] = None,
    ) -> UserDto:
        """
        Operation id: cancelDeletion
        Restore user

        :param user_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UserDto
        """

        endpoint = f"/api2/v1/users/{user_uid}/undelete"

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

        return UserDto.model_validate(r.json())

    async def create_user_v3(
        self,
        user_create_dto: Optional[UserCreateDto | dict] = None,
        send_invitation: Optional[bool] = False,
        phrase_token: Optional[str] = None,
    ) -> UserDetailsDtoV3Union:
        """
        Operation id: createUserV3
        Create user

        :param user_create_dto: Optional[UserCreateDto | dict] = None (optional), body.
        :param send_invitation: Optional[bool] = False (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UserDetailsDtoV3Union
        """

        endpoint = "/api2/v3/users"
        if type(user_create_dto) is dict:
            user_create_dto = UserCreateDto.model_validate(user_create_dto)

        params = {"sendInvitation": send_invitation}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = user_create_dto

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

        _u = UserDetailsDtoV3Union.model_validate(r.json())
        return getattr(_u, "root", _u)

    async def delete_user(
        self,
        user_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteUser
        Delete user

        :param user_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/users/{user_uid}"

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

    async def disable_two_factor_auth_v3(
        self,
        user_uid: str,
        phrase_token: Optional[str] = None,
    ) -> UserDetailsDtoV3Union:
        """
        Operation id: disableTwoFactorAuthV3
        Disable two-factor authentication

        :param user_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UserDetailsDtoV3Union
        """

        endpoint = f"/api2/v3/users/{user_uid}/disableTwoFactorAuth"

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

        _u = UserDetailsDtoV3Union.model_validate(r.json())
        return getattr(_u, "root", _u)

    async def get_list_of_users_filtered(
        self,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        include_deleted: Optional[bool] = False,
        last_name: Optional[str] = None,
        name: Optional[str] = None,
        name_or_email: Optional[str] = None,
        order: Optional[List[str]] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        role: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
        user_name: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoUserDto:
        """
        Operation id: getListOfUsersFiltered
        List users

        :param email: Optional[str] = None (optional), query.
        :param first_name: Optional[str] = None (optional), query. Filter for first name, that starts with value.
        :param include_deleted: Optional[bool] = False (optional), query.
        :param last_name: Optional[str] = None (optional), query. Filter for last name, that starts with value.
        :param name: Optional[str] = None (optional), query. Filter for last name or first name, that starts with value.
        :param name_or_email: Optional[str] = None (optional), query. Filter for last name, first name or email starting with the value.
        :param order: Optional[List[str]] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param role: Optional[List[str]] = None (optional), query.
        :param sort: Optional[List[str]] = None (optional), query.
        :param user_name: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoUserDto
        """

        endpoint = "/api2/v1/users"

        params = {
            "firstName": first_name,
            "lastName": last_name,
            "name": name,
            "userName": user_name,
            "email": email,
            "nameOrEmail": name_or_email,
            "role": role,
            "includeDeleted": include_deleted,
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

        return PageDtoUserDto.model_validate(r.json())

    async def get_user_v3(
        self,
        user_uid: str,
        phrase_token: Optional[str] = None,
    ) -> UserDetailsDtoV3Union:
        """
        Operation id: getUserV3
        Get user

        :param user_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UserDetailsDtoV3Union
        """

        endpoint = f"/api2/v3/users/{user_uid}"

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

        _u = UserDetailsDtoV3Union.model_validate(r.json())
        return getattr(_u, "root", _u)

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

    async def list_jobs(
        self,
        user_uid: str,
        due_in_hours: Optional[int] = None,
        filename: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        project_uid: Optional[str] = None,
        status: Optional[List[str]] = None,
        target_lang: Optional[List[str]] = None,
        workflow_step_id: Optional[int] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoAssignedJobDto:
        """
        Operation id: listJobs
        List assigned jobs

        :param user_uid: str (required), path.
        :param due_in_hours: Optional[int] = None (optional), query. -1 for jobs that are overdue.
        :param filename: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query.
        :param project_uid: Optional[str] = None (optional), query.
        :param status: Optional[List[str]] = None (optional), query.
        :param target_lang: Optional[List[str]] = None (optional), query.
        :param workflow_step_id: Optional[int] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAssignedJobDto
        """

        endpoint = f"/api2/v1/users/{user_uid}/jobs"

        params = {
            "status": status,
            "projectUid": project_uid,
            "targetLang": target_lang,
            "workflowStepId": workflow_step_id,
            "dueInHours": due_in_hours,
            "filename": filename,
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

        return PageDtoAssignedJobDto.model_validate(r.json())

    async def list_target_langs(
        self,
        user_uid: str,
        due_in_hours: Optional[int] = None,
        filename: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        project_uid: Optional[str] = None,
        status: Optional[List[str]] = None,
        workflow_step_id: Optional[int] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoString:
        """
        Operation id: listTargetLangs
        List assigned target languages

        :param user_uid: str (required), path.
        :param due_in_hours: Optional[int] = None (optional), query. -1 for jobs that are overdue.
        :param filename: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query.
        :param project_uid: Optional[str] = None (optional), query.
        :param status: Optional[List[str]] = None (optional), query.
        :param workflow_step_id: Optional[int] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoString
        """

        endpoint = f"/api2/v1/users/{user_uid}/targetLangs"

        params = {
            "status": status,
            "projectUid": project_uid,
            "workflowStepId": workflow_step_id,
            "dueInHours": due_in_hours,
            "filename": filename,
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

        return PageDtoString.model_validate(r.json())

    async def list_workflow_steps(
        self,
        user_uid: str,
        due_in_hours: Optional[int] = None,
        filename: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        project_uid: Optional[str] = None,
        status: Optional[List[str]] = None,
        target_lang: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoWorkflowStepReference:
        """
        Operation id: listWorkflowSteps
        List assigned workflow steps

        :param user_uid: str (required), path.
        :param due_in_hours: Optional[int] = None (optional), query. -1 for jobs that are overdue.
        :param filename: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query.
        :param page_size: Optional[int] = 50 (optional), query.
        :param project_uid: Optional[str] = None (optional), query.
        :param status: Optional[List[str]] = None (optional), query.
        :param target_lang: Optional[List[str]] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoWorkflowStepReference
        """

        endpoint = f"/api2/v1/users/{user_uid}/workflowSteps"

        params = {
            "status": status,
            "projectUid": project_uid,
            "targetLang": target_lang,
            "dueInHours": due_in_hours,
            "filename": filename,
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

        return PageDtoWorkflowStepReference.model_validate(r.json())

    async def login_activity(
        self,
        user_uid: str,
        phrase_token: Optional[str] = None,
    ) -> UserStatisticsListDto:
        """
        Operation id: loginActivity
        Login statistics

        :param user_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UserStatisticsListDto
        """

        endpoint = f"/api2/v1/users/{user_uid}/loginStatistics"

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

        return UserStatisticsListDto.model_validate(r.json())

    async def send_login_info(
        self,
        user_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: sendLoginInfo
        Send login information

        :param user_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/users/{user_uid}/emailLoginInformation"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

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

    async def update_password(
        self,
        user_uid: str,
        user_password_edit_dto: Optional[UserPasswordEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: updatePassword
        Update password

        Can be used by the user to update their own password or by ADMIN to update password of user without joined account
        * Password length must be between 8 and 255
        * Password must not be same as the username

        :param user_uid: str (required), path.
        :param user_password_edit_dto: Optional[UserPasswordEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/users/{user_uid}/updatePassword"
        if type(user_password_edit_dto) is dict:
            user_password_edit_dto = UserPasswordEditDto.model_validate(
                user_password_edit_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = user_password_edit_dto

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

    async def update_user_v3(
        self,
        user_uid: str,
        user_edit_dto: Optional[UserEditDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> UserDetailsDtoV3Union:
        """
        Operation id: updateUserV3
        Edit user

        :param user_uid: str (required), path.
        :param user_edit_dto: Optional[UserEditDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UserDetailsDtoV3Union
        """

        endpoint = f"/api2/v3/users/{user_uid}"
        if type(user_edit_dto) is dict:
            user_edit_dto = UserEditDto.model_validate(user_edit_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = user_edit_dto

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

        _u = UserDetailsDtoV3Union.model_validate(r.json())
        return getattr(_u, "root", _u)

    async def user_last_logins(
        self,
        order: Optional[List[str]] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 100,
        role: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
        user_name: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> PageDtoLastLoginDto:
        """
        Operation id: user-lastLogins
        List last login dates

        :param order: Optional[List[str]] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 100 (optional), query. Page size, accepts values between 1 and 100, default 100.
        :param role: Optional[List[str]] = None (optional), query.
        :param sort: Optional[List[str]] = None (optional), query.
        :param user_name: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoLastLoginDto
        """

        endpoint = "/api2/v1/users/lastLogins"

        params = {
            "userName": user_name,
            "role": role,
            "sort": sort,
            "order": order,
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

        return PageDtoLastLoginDto.model_validate(r.json())
