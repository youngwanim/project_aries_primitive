import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.models import ResultResponse
from aries.shepherd.manager.wechat_event_manager import WechatEventManager
from aries.shepherd.service.wechat_event_service import WechatEventService

logger_info = logging.getLogger('wechat_event_info')
logger_error = logging.getLogger('wechat_event_error')


class WechatEventNotification(APIView):

    app_id = 'viastelle'
    token = 'viastelle'
    aes_key = 'viastelle'

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        signature = request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echostr = request.GET.get('echostr', None)

        if signature is None or timestamp is None or nonce is None or echostr is None:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')

        return Response(int(echostr), result.get_code())

    def post(self, request):
        wechat_event_manager = WechatEventManager(logger_info, logger_error, request)

        try:
            request_data = request.data
            validation_result = wechat_event_manager.request_validation()

            if not validation_result[0]:
                result = validation_result[1]
                raise BusinessLogicError(result.get_response(), result.get_code())

            message_result = wechat_event_manager.get_decrypt_message(
                self.token, self.aes_key, self.app_id, request_data
            )

            if not message_result[0]:
                result = message_result[1]
                raise BusinessLogicError(result.get_response(), result.get_code())

            message = message_result[1]

            wechat_event_service = WechatEventService()
            service_result = wechat_event_service.create_wechat_event_message(message)

            if not service_result[0]:
                result = service_result[1]
                raise BusinessLogicError(result.get_response(), result.get_code())
        except BusinessLogicError as instance:
            response, result_code = instance.args
            return Response(response, result_code)
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            return Response(result.get_response(), result.get_code())
