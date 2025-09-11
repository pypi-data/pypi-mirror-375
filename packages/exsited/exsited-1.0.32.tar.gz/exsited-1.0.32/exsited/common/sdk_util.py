from exsited.exsited.common.common_enum import SortDirection
from exsited.common.sdk_conf import SDKConfig
import re


class SDKUtil:

    @staticmethod
    def get_dict_value(data: dict, key: str, default=None):
        if not data or not key:
            return default
        elif key in data:
            return data[key]
        return default

    @staticmethod
    def init_dict_if_value(data: dict, key: str, value):
        if value:
            data[key] = value
        return data

    @staticmethod
    def init_pagination_params(params: dict = None, limit: int = None, offset: int = None, direction: SortDirection = None, order_by: str = None):
        if not params:
            params = {}
        params = SDKUtil.init_dict_if_value(params, "limit", limit)
        params = SDKUtil.init_dict_if_value(params, "offset", offset)
        params = SDKUtil.init_dict_if_value(params, "direction", str(direction))
        params = SDKUtil.init_dict_if_value(params, "order_by", order_by)
        return params

    @staticmethod
    def apply_api_version_to_url(url: str, per_request_version: str = None) -> str:
        """
        Apply API version replacement to URL based on version priority.
        Priority: per_request_version > SDKConfig.API_VERSION > SDKConfig.API_GLOBAL_VERSION > original URL
        If all are None, returns original URL unchanged.
        """

        version_to_use = per_request_version or SDKConfig.API_VERSION or SDKConfig.API_GLOBAL_VERSION

        if version_to_use and re.search(r'/api/v[23]', url):
            return re.sub(r'/api/v[23]', f'/api/{version_to_use}', url)
        
        return url
