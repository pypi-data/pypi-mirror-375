
from exsited.exsited.external_database.external_database_api_url import ExternalDatabaseApiUrl
from exsited.http.ab_rest_processor import ABRestProcessor
from exsited.common.sdk_util import SDKUtil
from exsited.exsited.common.common_enum import SortDirection

class ExternalDatabase(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def external_database_list(self, limit: int = None, offset: int = None, direction: SortDirection = None,
                             order_by: str = None, param_filters: dict = None) -> dict:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=ExternalDatabaseApiUrl.EXTERNAL_DATABASE, params=params,
                            response_obj={})
        return response

    def external_database_details(self, db_name: str ) -> dict:
        response = self.get(url=ExternalDatabaseApiUrl.EXTERNAL_DATABASE_DETAILS.format(db_name=db_name),
                            response_obj={})
        return response

    def external_database_create(self, request_data: dict ) -> dict:
        response = self.post(url=ExternalDatabaseApiUrl.EXTERNAL_DATABASE,request_obj=request_data,
                            response_obj={})
        return response

    def external_database_table_details(self, db_name: str, table_name: str, limit: int = None, offset: int = None, direction: SortDirection = None,
                             order_by: str = None, param_filters: dict = None ) -> dict:
        params = SDKUtil.init_pagination_params(params=param_filters, limit=limit, offset=offset, direction=direction,
                                                order_by=order_by)
        response = self.get(url=ExternalDatabaseApiUrl.EXTERNAL_DATABASE_TABLE_DETAILS.format(db_name=db_name,table_name=table_name), params=params,
                            response_obj={})
        return response
