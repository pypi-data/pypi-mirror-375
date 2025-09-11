from exsited.exsited.custom_component.custom_component_api_url import CustomComponentApiUrl
from exsited.exsited.custom_component.dto.custom_component_dto import CustomComponentResponseDTO
from exsited.http.ab_rest_processor import ABRestProcessor
from exsited.common.sdk_util import SDKUtil
from exsited.exsited.common.common_enum import SortDirection

class CustomComponent(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)
    def custom_component_list(self, limit: int = None, offset: int = None, direction: SortDirection = None,
                             order_by: str = None, param_filters: dict = None) -> CustomComponentResponseDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=CustomComponentApiUrl.CUSTOM_COMPONENT, params=params,
                            response_obj={})
        return response

    def custom_component_details(self, uuid: str, limit: int = None, offset: int = None, direction: SortDirection = None,
                             order_by: str = None, param_filters: dict = None) -> CustomComponentResponseDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=CustomComponentApiUrl.CUSTOM_COMPONENT_DETAILS.format(uuid=uuid), params=params,
                            response_obj={})
        return response

    def custom_component_create(self, uuid: str, request_data: dict) -> dict:
        response = self.post(url=CustomComponentApiUrl.CUSTOM_COMPONENT_DETAILS.format(uuid=uuid), request_obj=request_data, response_obj={})
        return response

    def custom_component_uuid_details(self, id: str, uuid: str, limit: int = None, offset: int = None, direction: SortDirection = None,
                             order_by: str = None, param_filters: dict = None) -> CustomComponentResponseDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=CustomComponentApiUrl.CUSTOM_COMPONENT_UUID_DETAILS.format(uuid=uuid, id=id), params=params,
                            response_obj={})
        return response

    def custom_component_pdf(self, id: str, uuid: str) -> CustomComponentResponseDTO:
        response = self.get(url=CustomComponentApiUrl.CUSTOM_COMPONENT_PDF.format(uuid=uuid, id=id))
        return response