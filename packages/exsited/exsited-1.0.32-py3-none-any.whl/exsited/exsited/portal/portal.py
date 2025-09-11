from exsited.exsited.common.common_enum import SortDirection
from exsited.common.sdk_util import SDKUtil
from exsited.exsited.portal.dto.portal_dto import *
from exsited.exsited.portal.portal_api_urls import PortalApiUrl
from exsited.http.ab_rest_processor import ABRestProcessor


class Portal(ABRestProcessor):

    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def portal_login(self, request_data: ReportLoginRequestDTO) -> ReportLoginResponseDTO:
        response = self.post(url=PortalApiUrl.PORTAL_LOGIN, request_obj=request_data, response_obj=ReportLoginResponseDTO())
        return response

    def portal_change_password(self, request_data: ReportChangePasswordRequestDTO) -> ReportChangePasswordResponseDTO:
        response = self.post(url=PortalApiUrl.PORTAL_CHANGE_PASSWORD, request_obj=request_data, response_obj=ReportChangePasswordResponseDTO())
        return response
