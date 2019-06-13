import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code

from aries.common.exceptions.exceptions import DataValidationError, AuthInfoError, BusinessLogicError
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.common.utils.user_util import check_auth_info_v2
from aries.purchases.manager.coupon_manager_v3 import CouponManagerV3


"""
views_coupon - Coupon read api
"""
logger_info = logging.getLogger('purchases_info')
logger_error = logging.getLogger('purchases_error')


class CouponDetail(APIView):
    SUCCESS_MSG = 'success'

    def get(self, request):
        auth_info = header_parser.parse_auth_info(request)
        lang_info = header_parser.parse_language_v2(request.META)

        logger_info.info('[views_coupon][CouponDetail][get][' + str(auth_info.open_id) + ']')

        try:
            coupon_manager = CouponManagerV3(logger_info, logger_error)
            result_map = coupon_manager.get_coupon_detail(auth_info.open_id, lang_info.target_db,
                                                          auth_info.access_token)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS_MSG)
            result.set_map(result_map)

        return Response(result.get_response(), result.get_code())


class CouponPage(APIView):
    EXPIRED_DAY = 7

    def get(self, request):
        auth_info = header_parser.parse_auth_info(request)
        language_info = header_parser.parse_language_v2(request.META)

        logger_info.info('[views_coupon][CouponPage][get][' + auth_info.open_id + ',' + auth_info.access_token + ']')

        try:
            coupon_manager = CouponManagerV3(logger_info, logger_error)
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 20))

            coupon_data = coupon_manager.get_coupon_list(auth_info.open_id, auth_info.access_token,
                                                         language_info.target_db, page, limit, self.EXPIRED_DAY)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set_map(coupon_data)

        return Response(result.get_response(), result.get_code())


class CouponInformation(APIView):

    def post(self, request):
        language_info = header_parser.parse_language_v2(request.META)
        request_data = request.data

        logger_info.info('[views_coupon][CouponInformation][post][' + str(request.data) + ']')

        try:
            coupon_manager = CouponManagerV3(logger_info, logger_error)
            coupon_info_list = coupon_manager.read_coupon_information(request_data, language_info.target_db)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('coupon_info', coupon_info_list)

        return Response(result.get_response(), result.get_code())