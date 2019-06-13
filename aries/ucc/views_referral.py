import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import AuthInfoError, BusinessLogicError, DataValidationError
from aries.common.http_utils import header_parser
from aries.common.http_utils.purchase_api_util import update_coupon_count_no_log
from aries.common.models import ResultResponse
from aries.ucc.common.referral_func import referral_authentication_validation, coupon_issue_validation, \
    share_id_param_validation, request_notify_info, open_id_param_validation
from aries.ucc.manager.referral_manager import ReferralManager


class ReferralBoard(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def get(self, request):
        auth_info = header_parser.parse_auth_info(request)
        language_info = header_parser.parse_language_v2(request.META)

        self.logger_info.info('[views_referral][ReferralBoard][get]['
                              + str(auth_info.open_id) + str(auth_info.access_token) + ']')

        referral_manager = ReferralManager(self.logger_info, self.logger_error)

        try:
            referral_authentication_validation(auth_info)

            open_id = auth_info.open_id
            access_token = auth_info.access_token
            accept_lang = language_info.accept_lang

            referral_event = referral_manager.get_referral_status(open_id, access_token, accept_lang)
            request_notify_info(open_id, access_token, False)
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
            result.set('referral_event', referral_event)

        return Response(result.get_response(), result.get_code())


class ReferralInformation(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def get(self, request):
        language_info = header_parser.parse_language_v2(request.META)

        referral_manager = ReferralManager(self.logger_info, self.logger_error)

        try:
            referral_info = referral_manager.get_referral_information(language_info.accept_lang)
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
            result.set('friend_coupon_status', referral_info['friend_coupon_status'])
            result.set('first_coupon_status', referral_info['first_coupon_status'])

        return Response(result.get_response(), result.get_code())


class ReferralCoupon(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def post(self, request):
        auth_info = header_parser.parse_auth_info(request)
        lang_info = header_parser.parse_language_v2(request.META)

        request_data = request.data

        self.logger_info.info('[ReferralCoupon][post][' + str(auth_info.open_id) + str(auth_info.access_token) + ']')
        self.logger_info.info('[ReferralCoupon][post][' + str(request_data) + ']')

        try:
            referral_authentication_validation(auth_info)
            coupon_issue_validation(request_data)

            open_id = auth_info.open_id
            coupon_list = request_data['coupon_list']
            coupon_type = request_data['coupon_type']

            referral_manager = ReferralManager(self.logger_info, self.logger_error)
            res_map = referral_manager.issue_referral_coupon(open_id, lang_info.cn_header, coupon_type, coupon_list)
            update_coupon_count_no_log(auth_info.open_id, auth_info.access_token, 0, len(coupon_list))
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
            result.set_map(res_map)

        return Response(result.get_response(), result.get_code())


class ReferralValidation(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def post(self, request):
        request_data = request.data
        self.logger_info.info('[ReferralValidation][post][' + str(request_data) + ']')

        referral_manager = ReferralManager(self.logger_info, self.logger_error)

        try:
            share_id_param_validation(request_data)
            share_id = request_data['share_id']

            validation_result = referral_manager.get_open_id_from_unique_id(share_id)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
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
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('open_id', validation_result['open_id'])

        return Response(result.get_response(), result.get_code())


class ReferralFirstPurchase(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def post(self, request):
        request_data = request.data
        self.logger_info.info('[ReferralFirstPurchase][post][' + str(request_data) + ']')

        referral_manager = ReferralManager(self.logger_info, self.logger_error)

        try:
            open_id_param_validation(request_data)
            open_id = request_data['open_id']

            referral_manager.do_first_purchase_up(open_id)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
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
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())
