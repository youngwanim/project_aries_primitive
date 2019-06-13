import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.http_utils import header_parser
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse
from aries.products.manager.hub_manager_v2 import HubManagerV2

logger_info = logging.getLogger('products_info')
logger_error = logging.getLogger('products_error')


class HubGeoInformation(APIView):
    SUCCESS_MSG = 'success'
    DEFAULT_HUB = 1

    def get(self, request):
        auth_info = header_parser.parse_auth_info(request)
        lang_info = parse_language_v2(request.META)

        if auth_info.open_id is not None:
            logger_info.info('[HubGeoInformation][get][' + str(auth_info.open_id) + ']')

        try:
            hub_manager = HubManagerV2(logger_info, logger_error)
            hub_list = hub_manager.get_hub_list(self.DEFAULT_HUB, lang_info.cn_header, lang_info.target_db)
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS_MSG)
            result.set('hub_list', hub_list)

        return Response(result.get_response(), result.get_code())


class HubDelivery(APIView):
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    def get(self, request):
        self.logger_info.info('[HubDelivery][get]')
        default_hub = 1
        lang_info = parse_language_v2(request.META)

        try:
            hub_manager = HubManagerV2(logger_info, logger_error)
            delivery_hub_list = hub_manager.get_hub_delivery(lang_info.cn_header, lang_info.target_db)
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('delivery_hub_list', delivery_hub_list)

        return Response(result.get_response(), result.get_code())
