from rest_framework.response import Response
from rest_framework.views import APIView
from xinge_push import ClickAction
from xinge_push import Message
from xinge_push import Style
from xinge_push import XingeApp

from aries.common import code
from aries.common.models import ResultResponse


PUSH_TYPE_UPCOMING = 1
PUSH_TYPE_DELIVERED = 2
PUSH_TYPE_CANCELED_ORDERS = 3
PUSH_TYPE_RATE_ORDERS = 4
PUSH_TYPE_PROMOTION_DETAIL = 5
PUSH_TYPE_MY_NEWS = 6
PUSH_TYPE_PRODUCT_DETAIL = 7

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
        title = request_data['title']
        content = request_data['content']
        msg = build_android_notification(title, content)
        msg.custom = request_data['custom']

        print(msg.custom)
        print(len(msg.custom))

        push_app = XingeApp(self.AccessId, self.SecretKey)
        ret = push_app.PushSingleAccount(0, open_id, msg)
        result.set('ret', ret)

        return Response(result.get_response(), result.get_code())


def build_android_notification(title, content):
    msg = Message()
    msg.type = MESSAGE_TYPE_ANDROID_NOTIFICATION
    msg.title = title
    msg.content = content
    msg.style = Style(1, 1)
    # msg.action = ClickAction()
    action = ClickAction()
    action.actionType = 1
    action.activity = 'com.kolon.viastelle.ui.push.PushGatewayActivity'
    action.intent = ''
    msg.action = action
    return msg


class PushCustom(APIView):

    AccessId = '2100257323'
    SecretKey = 'e7c3215b9b837132ae73f5493b15ad3b'

    def post(self, request):
        print(request.data)
        request_data = request.data

        try:
            open_id = request_data['open_id']
            action_type = request_data['action_type']
            action = ClickAction()

            if action_type == 0:
                action = None
            elif action_type == 1:
                action.actionType = 1
                action.activity = request_data['activity']
                action.intentFlag = request_data['if']
                action.pendingFlag = request_data['pf']
            elif action_type == 2:
                action.actionType = 2
                action.url = request_data['browser']
            else:
                action.actionType = 3
                action.intent = request_data['intent']
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Parameter invalid')
            return Response(result.get_response(), result.get_code())

        try:
            msg = build_android_notification_api('Custom push test', 'Test content!')

            if action_type != 0:
                msg.action = action

            if 'custom' in request_data:
                msg.custom = request_data['custom']

            push_app = XingeApp(self.AccessId, self.SecretKey)
            ret = push_app.PushSingleAccount(0, open_id, msg)

            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('ret', ret)

            return Response(result.get_response(), result.get_code())
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Parameter invalid')
            return Response(result.get_response(), result.get_code())


def build_android_notification_api(title, content):
    msg = Message()
    msg.type = MESSAGE_TYPE_ANDROID_NOTIFICATION
    msg.title = title
    msg.content = content
    msg.style = Style(1, 1)
    return msg
