import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.purchases.manager.promotion_manager import PromotionManager


logger_info = logging.getLogger('purchases_info')
logger_error = logging.getLogger('purchases_error')


class PromotionView(APIView):

    def get(self, request, hub_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        auth_info = header_parser.parse_authentication(request)
        lang_info = header_parser.parse_language_v2(request.META)

        promotion_manager = PromotionManager(logger_info, logger_error, lang_info.target_db)
        promotion_manager.update_notification_count(auth_info)

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        os_type = int(request.GET.get('os_type', 2))

        try:
            # Get promotion list
            promotion_list_result = promotion_manager.get_promotion_list(page, limit, hub_id, os_type)
            promotion_count = promotion_list_result[0]
            promotion_list = promotion_list_result[1]

            result.set('total_count', promotion_count)
            result.set('promotions', promotion_list)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class PromotionDetailView(APIView):

    def get(self, request, promotion_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        lang_info = header_parser.parse_language_v2(request.META)
        promotion_manager = PromotionManager(logger_info, logger_error, lang_info.target_db)

        try:
            promotion_data = promotion_manager.get_promotion(promotion_id)
            result.set('promotion', promotion_data)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())
