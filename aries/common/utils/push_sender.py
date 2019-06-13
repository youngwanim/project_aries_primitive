from xinge_push import ClickAction
from xinge_push import Message
from xinge_push import Style
from xinge_push import XingeApp

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

AccessId = '2100271320'
SecretKey = 'f78e63d29180b46fab6c7498c12c491f'


def sendPushToAdmin(title, content, custom):

    msg = build_android_notification(title, content)
    msg.custom = custom

    push_app = XingeApp(AccessId, SecretKey)
    ret = push_app.PushAllDevices(0, msg)
    return ret


def build_android_notification(title, content):
    msg = Message()
    msg.type = MESSAGE_TYPE_ANDROID_NOTIFICATION
    msg.title = title
    msg.content = content
    msg.style = Style(1, 1)
    # msg.action = ClickAction()
    action = ClickAction()
    action.actionType = 1
    action.activity = 'com.kolon.viastelle.admin.ui.push.PushGatewayActivity'
    action.intent = ''
    msg.action = action
    return msg
