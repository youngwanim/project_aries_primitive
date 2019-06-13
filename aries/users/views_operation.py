import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.users.manager.user_manager import UserManager


logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class OrderComplete(APIView):

    def post(self, request):

        authentication = header_parser.parse_authentication(request)

        open_id = authentication[0]
        access_token = authentication[1]
        order_id = request.data.get('order_id', None)

        try:
            user_manager = UserManager()
            result = user_manager.send_order_complete_msg(open_id, access_token, order_id)
            return Response(result.get_response(), result.get_code())

        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, str(e))
            return Response(result.get_response(), result.get_code())


class OrderCanceled(APIView):

    def post(self, request):

        authentication = header_parser.parse_authentication(request)

        open_id = authentication[0]
        access_token = authentication[1]
        order_id = request.data.get('order_id', None)

        try:
            user_manager = UserManager()
            result = user_manager.send_order_cancel_msg(open_id, access_token, order_id)
            return Response(result.get_response(), result.get_code())

        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, str(e))
            return Response(result.get_response(), result.get_code())
