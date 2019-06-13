import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.models import ResultResponse

from aries.users.common.referral_func import request_validation, get_referral_result
from aries.users.service.user_referrel_service import UserReferralService


class UserReferralHistory(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def post(self, request):
        request_data = request.data

        try:
            request_validation(request_data)

            open_id = request_data['open_id']
            referral_service = UserReferralService(self.logger_info, self.logger_error)
            referral_info = referral_service.read_user_referral_info(open_id)

            if referral_info is None:
                referral_result = get_referral_result(False, '', '')
            else:
                ref_open_id = referral_info['referrer_open_id']
                ref_share_id = referral_info['referrer_share_id']
                referral_result = get_referral_result(True, ref_open_id, ref_share_id)
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set_map(referral_result)

        return Response(result.get_response(), result.get_code())
