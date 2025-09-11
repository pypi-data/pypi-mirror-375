from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import CreateVendorDto, DeleteVendorsDto, PageDtoVendorDto, VendorDto


class VendorOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def create_vendor(
        self,
        create_vendor_dto: Optional[CreateVendorDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> VendorDto:
        """
        Operation id: createVendor
        Create vendor

        :param create_vendor_dto: Optional[CreateVendorDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: VendorDto
        """

        endpoint = "/api2/v1/vendors"
        if type(create_vendor_dto) is dict:
            create_vendor_dto = CreateVendorDto.model_validate(create_vendor_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = create_vendor_dto

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

        return VendorDto.model_validate(r.json())

    def delete_vendors(
        self,
        delete_vendors_dto: Optional[DeleteVendorsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: deleteVendors
        Delete vendors (batch)

        :param delete_vendors_dto: Optional[DeleteVendorsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = "/api2/v1/vendors"
        if type(delete_vendors_dto) is dict:
            delete_vendors_dto = DeleteVendorsDto.model_validate(delete_vendors_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = delete_vendors_dto

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

    def get_vendor(
        self,
        vendor_uid: str,
        phrase_token: Optional[str] = None,
    ) -> VendorDto:
        """
        Operation id: getVendor
        Get vendor

        :param vendor_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: VendorDto
        """

        endpoint = f"/api2/v1/vendors/{vendor_uid}"

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

        return VendorDto.model_validate(r.json())

    def list_vendors(
        self,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoVendorDto:
        """
        Operation id: listVendors
        List vendors

        :param name: Optional[str] = None (optional), query. Name or the vendor, for filtering.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoVendorDto
        """

        endpoint = "/api2/v1/vendors"

        params = {"pageNumber": page_number, "pageSize": page_size, "name": name}

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

        return PageDtoVendorDto.model_validate(r.json())
