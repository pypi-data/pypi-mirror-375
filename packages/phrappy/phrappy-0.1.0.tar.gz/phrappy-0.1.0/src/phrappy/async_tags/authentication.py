from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import json

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    AppleTokenResponseDto,
    LoginDto,
    LoginOtherDto,
    LoginOtherV3Dto,
    LoginResponseDto,
    LoginResponseV3Dto,
    LoginToSessionDto,
    LoginToSessionResponseDto,
    LoginToSessionResponseV3Dto,
    LoginToSessionV3Dto,
    LoginUserDto,
    LoginV3Dto,
    LoginWithAppleDto,
    LoginWithGoogleDto,
)


class AuthenticationOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def login(
        self,
        login_dto: Optional[LoginDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LoginResponseDto:
        """
        Operation id: login
        Login

        :param login_dto: Optional[LoginDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseDto
        """

        endpoint = "/api2/v1/auth/login"
        if type(login_dto) is dict:
            login_dto = LoginDto.model_validate(login_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = login_dto

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

        return LoginResponseDto.model_validate(r.json())

    async def login_by_apple_with_code(
        self,
        login_with_apple_dto: Optional[LoginWithAppleDto | dict] = None,
        native: Optional[bool] = None,
        phrase_token: Optional[str] = None,
    ) -> LoginResponseDto:
        """
        Operation id: loginByAppleWithCode
        Login with Apple with code

        :param login_with_apple_dto: Optional[LoginWithAppleDto | dict] = None (optional), body.
        :param native: Optional[bool] = None (optional), query. For sign in with code from native device.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseDto
        """

        endpoint = "/api2/v1/auth/loginWithApple/code"
        if type(login_with_apple_dto) is dict:
            login_with_apple_dto = LoginWithAppleDto.model_validate(
                login_with_apple_dto
            )

        params = {"native": native}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = login_with_apple_dto

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

        return LoginResponseDto.model_validate(r.json())

    async def login_by_apple_with_refresh_token(
        self,
        login_with_apple_dto: Optional[LoginWithAppleDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LoginResponseDto:
        """
        Operation id: loginByAppleWithRefreshToken
        Login with Apple refresh token

        :param login_with_apple_dto: Optional[LoginWithAppleDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseDto
        """

        endpoint = "/api2/v1/auth/loginWithApple/refreshToken"
        if type(login_with_apple_dto) is dict:
            login_with_apple_dto = LoginWithAppleDto.model_validate(
                login_with_apple_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = login_with_apple_dto

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

        return LoginResponseDto.model_validate(r.json())

    async def login_by_google(
        self,
        login_with_google_dto: Optional[LoginWithGoogleDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LoginResponseDto:
        """
        Operation id: loginByGoogle
        Login with Google

        :param login_with_google_dto: Optional[LoginWithGoogleDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseDto
        """

        endpoint = "/api2/v1/auth/loginWithGoogle"
        if type(login_with_google_dto) is dict:
            login_with_google_dto = LoginWithGoogleDto.model_validate(
                login_with_google_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = login_with_google_dto

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

        return LoginResponseDto.model_validate(r.json())

    async def login_other(
        self,
        login_other_dto: Optional[LoginOtherDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LoginResponseDto:
        """
        Operation id: loginOther
        Login as another user
        Available only for admin
        :param login_other_dto: Optional[LoginOtherDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseDto
        """

        endpoint = "/api2/v1/auth/loginOther"
        if type(login_other_dto) is dict:
            login_other_dto = LoginOtherDto.model_validate(login_other_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = login_other_dto

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

        return LoginResponseDto.model_validate(r.json())

    async def login_other_v3(
        self,
        login_other_v3_dto: Optional[LoginOtherV3Dto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LoginResponseV3Dto:
        """
        Operation id: loginOtherV3
        Login as another user
        Available only for admin
        :param login_other_v3_dto: Optional[LoginOtherV3Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseV3Dto
        """

        endpoint = "/api2/v3/auth/loginOther"
        if type(login_other_v3_dto) is dict:
            login_other_v3_dto = LoginOtherV3Dto.model_validate(login_other_v3_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = login_other_v3_dto

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

        return LoginResponseV3Dto.model_validate(r.json())

    async def login_to_session(
        self,
        login_to_session_dto: Optional[LoginToSessionDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LoginToSessionResponseDto:
        """
        Operation id: loginToSession
        Login to session

        :param login_to_session_dto: Optional[LoginToSessionDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginToSessionResponseDto
        """

        endpoint = "/api2/v1/auth/loginToSession"
        if type(login_to_session_dto) is dict:
            login_to_session_dto = LoginToSessionDto.model_validate(
                login_to_session_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = login_to_session_dto

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

        return LoginToSessionResponseDto.model_validate(r.json())

    async def login_to_session_2(
        self,
        login_to_session_v3_dto: Optional[LoginToSessionV3Dto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LoginToSessionResponseV3Dto:
        """
        Operation id: loginToSession_2
        Login to session

        :param login_to_session_v3_dto: Optional[LoginToSessionV3Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginToSessionResponseV3Dto
        """

        endpoint = "/api2/v3/auth/loginToSession"
        if type(login_to_session_v3_dto) is dict:
            login_to_session_v3_dto = LoginToSessionV3Dto.model_validate(
                login_to_session_v3_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = login_to_session_v3_dto

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

        return LoginToSessionResponseV3Dto.model_validate(r.json())

    async def login_v3(
        self,
        login_v3_dto: Optional[LoginV3Dto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> LoginResponseV3Dto:
        """
        Operation id: loginV3
        Login

        :param login_v3_dto: Optional[LoginV3Dto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseV3Dto
        """

        endpoint = "/api2/v3/auth/login"
        if type(login_v3_dto) is dict:
            login_v3_dto = LoginV3Dto.model_validate(login_v3_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = login_v3_dto

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

        return LoginResponseV3Dto.model_validate(r.json())

    async def logout(
        self,
        authorization: Optional[str] = None,
        token: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: logout
        Logout

        :param authorization: Optional[str] = None (optional), header.
        :param token: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = "/api2/v1/auth/logout"

        params = {"token": token}

        headers = {
            "Authorization": (
                authorization.model_dump_json()
                if hasattr(authorization, "model_dump_json")
                else (
                    json.dumps(authorization)
                    if False and not isinstance(authorization, str)
                    else str(authorization)
                )
            )
        }
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

    async def refresh_apple_token(
        self,
        token: Optional[str] = None,
        phrase_token: Optional[str] = None,
    ) -> AppleTokenResponseDto:
        """
        Operation id: refreshAppleToken
        Refresh Apple token

        :param token: Optional[str] = None (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AppleTokenResponseDto
        """

        endpoint = "/api2/v1/auth/refreshAppleToken"

        params = {"token": token}

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

        return AppleTokenResponseDto.model_validate(r.json())

    async def who_am_i(
        self,
        phrase_token: Optional[str] = None,
    ) -> LoginUserDto:
        """
        Operation id: whoAmI
        Who am I


        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginUserDto
        """

        endpoint = "/api2/v1/auth/whoAmI"

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

        return LoginUserDto.model_validate(r.json())
