from exsited.exsited.custom_attributes.custom_attributes_api_url import CustomAttributesApiUrl
from exsited.exsited.custom_attributes.dto.custom_attributes_dto import CustomAttributesResponseDTO, \
    CustomAttributesRequestDTO
from exsited.common.sdk_util import SDKUtil
from exsited.http.ab_rest_processor import ABRestProcessor


class CustomAttributes(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def custom_attributes(self) -> CustomAttributesResponseDTO:
        response = self.get(url=CustomAttributesApiUrl.CUSTOM_ATTRIBUTES, response_obj={})
        return response
    def custom_attributes_update(self, uuid: str, request_data=CustomAttributesRequestDTO) -> CustomAttributesResponseDTO:
        response = self.patch(url=CustomAttributesApiUrl.CUSTOM_ATTRIBUTES_UPDATE.format(uuid=uuid),request_obj=request_data, response_obj=CustomAttributesResponseDTO())
        return response


