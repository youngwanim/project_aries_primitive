from rest_framework.response import Response
from rest_framework.views import APIView
from xinge_push import MessageIOS
from xinge_push import XingeApp

from aries.common import code
from aries.common.models import ResultResponse
from django.conf import settings

PUSH_TYPE_UPCOMING = 1
PUSH_TYPE_DELIVERED = 2
PUSH_TYPE_CANCELED_ORDERS = 3
PUSH_TYPE_RATE_ORDERS = 4
PUSH_TYPE_PROMOTION_DETAIL = 5
PUSH_TYPE_MY_NEWS = 6

MESSAGE_TYPE_ANDROID_NOTIFICATION = 1
MESSAGE_TYPE_ANDROID_MESSAGE = 2
MESSAGE_TYPE_IOS_APNS_NOTIFICATION = 11
MESSAGE_TYPE_IOS_REMOTE_NOTIFICATION = 12


class PushOrderComplete(APIView):

    AccessId = '2100257323'
    SecretKey = 'e7c3215b9b837132ae73f5493b15ad3b'

    def post(self, request):
        request_data = request.data
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        open_id = request_data['open_id']
        msg = build_ios_notification('Delivering complete.', 'Enjoy it!', request_data['custom'])

        print(msg.custom)
        print(len(msg.custom))

        push_app = XingeApp(self.AccessId, self.SecretKey)
        ret = push_app.PushSingleAccount(0, open_id, msg)
        result.set('ret', ret)

        return Response(result.get_response(), result.get_code())


def build_ios_notification(title, content, custom):
    msg = MessageIOS()
    msg.title = title
    msg.alert = {'body': content}
    msg.sound = 'default'
    msg.custom = custom
    return msg


class PushCustom(APIView):

    AccessId = '2200264357'
    SecretKey = '28b4e56f299a5521a005d8d787d17cba'

    if settings.DEBUG:
        environment = 2
    else:
        environment = 1

    def post(self, request):
        print(request.data)
        request_data = request.data

        try:
            open_id = request_data['open_id']
            title = request_data['title']
            content = request_data['content']
            custom = request_data['custom']
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Parameter invalid')
            return Response(result.get_response(), result.get_code())

        try:
            msg = build_ios_notification(title, content, custom)
            print(msg.GetMessageObject())
            push_app = XingeApp(self.AccessId, self.SecretKey)
            ret = push_app.PushSingleAccount(0, open_id, msg, self.environment)
            # ret = push_app.PushSingleDevice(open_id, msg, 2)

            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('ret', ret)

            return Response(result.get_response(), result.get_code())
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Parameter invalid')
            return Response(result.get_response(), result.get_code())
