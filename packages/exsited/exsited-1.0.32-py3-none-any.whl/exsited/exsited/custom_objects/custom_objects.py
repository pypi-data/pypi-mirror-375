from exsited.exsited.custom_objects.custom_objects_api_url import CustomObjectsApiUrl
from exsited.exsited.custom_objects.dto.custom_objects_dto import CustomObjectsListDTO, \
    CustomObjectsDetailsDTO
from exsited.common.sdk_util import SDKUtil
from exsited.http.ab_rest_processor import ABRestProcessor


class CustomObjects(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def account_list(self, id: str) -> CustomObjectsListDTO:
        response = self.get(url=CustomObjectsApiUrl.CO_ACCOUNT_LIST.format(id=id), response_obj=CustomObjectsListDTO())
        return response

    def account_co_details_uuid(self, id: str, uuid: str) -> CustomObjectsDetailsDTO:
        response = self.get(url=CustomObjectsApiUrl.CO_ACCOUNT_DETAILS_UUID.format(id=id, uuid=uuid), response_obj=CustomObjectsDetailsDTO())
        return response

    def custom_objects_list(self, cc_id: str, cc_uuid: str) -> dict:
        response = self.get(url=CustomObjectsApiUrl.CO_LIST.format(cc_id=cc_id, cc_uuid=cc_uuid), response_obj={})
        return response

    def custom_objects_details(self, cc_id: str, cc_uuid: str, co_uuid: str) -> dict:
        response = self.get(url=CustomObjectsApiUrl.CO_DETAILS.format(cc_id=cc_id, cc_uuid=cc_uuid,co_uuid=co_uuid), response_obj={})
        return response

    def custom_objects_create(self, cc_id: str, cc_uuid: str, co_uuid: str, request_data: dict) -> dict:
        response = self.post(url=CustomObjectsApiUrl.CO_DETAILS.format(cc_id=cc_id, cc_uuid=cc_uuid,co_uuid=co_uuid), request_obj=request_data, response_obj={})
        return response

    def custom_objects_update(self, cc_id: str, cc_uuid: str, co_uuid: str, request_data: dict) -> dict:
        response = self.patch(url=CustomObjectsApiUrl.CO_DETAILS.format(cc_id=cc_id, cc_uuid=cc_uuid,co_uuid=co_uuid), request_obj=request_data, response_obj={})
        return response
