import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import DataValidationError, BusinessLogicError
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.purchases.common.coupon_util import coupon_issue_validation, member_promotion_filtering, \
    member_coupon_issue_validation
from aries.purchases.manager.coupon_manager_v3 import CouponManagerV3
from aries.purchases.manager.promotion_manager import PromotionManager

"""
views_referral_coupon - Referral coupon issue
"""
logger_info = logging.getLogger('purchases_info')
logger_error = logging.getLogger('purchases_error')


class ReferralCoupon(APIView):
    SUCCESS_MSG = 'success'

    def post(self, request):
        request_data = request.data
        logger_info.info('[views_referral_coupon][ReferralCoupon][post][' + str(request_data) + ']')

        try:
            coupon_issue_validation(request_data)

            open_id = request_data['open_id']
            coupon_list = request_data['coupon_list']
            coupon_code = request_data['coupon_code']
            sender_id = request_data['sender_id']

            coupon_manager = CouponManagerV3(logger_info, logger_error)
            coupon_manager.create_coupon_with_coupon_list(open_id, coupon_list, coupon_code, sender_id)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS_MSG)

        return Response(result.get_response(), result.get_code())


class MembershipPromotion(APIView):
    SUCCESS_MSG = 'success'

    def post(self, request):
        lang_info = header_parser.parse_language_v2(request.META)

        request_data = request.data
        logger_info.info('[views_referral_coupon][PromotionCoupon][post][' + str(request_data) + ']')

        try:
            member_coupon_issue_validation(request_data)

            open_id = request_data['open_id']
            promotion_type = request_data['promotion_type']
            promotion_manager = PromotionManager(logger_info, logger_error, lang_info)

            lang_type = 1 if lang_info.cn_header else 0
            member_promotion = promotion_manager.get_promotion_list_with_latest(promotion_type, lang_type)

            if member_promotion is None:
                has_member_promotion = False
                member_promotion = {}
            else:
                has_member_promotion = True

                coupon_id = member_promotion['coupon_id']
                coupon_days = member_promotion['coupon_days']
                coupon_code = member_promotion['coupon_code']
                sender_id = member_promotion['sender_id']

                coupon_manager = CouponManagerV3(logger_info, logger_error)
                coupon_manager.create_coupon_with_promotion(open_id, coupon_id, coupon_days, coupon_code, sender_id)

                member_promotion = member_promotion_filtering(member_promotion)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS_MSG)
            result.set('has_member_promotion', has_member_promotion)
            result.set('member_promotion', member_promotion)

        return Response(result.get_response(), result.get_code())
