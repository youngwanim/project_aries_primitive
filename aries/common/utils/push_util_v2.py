from django.conf import settings
from xinge_push import Message, MESSAGE_TYPE_ANDROID_NOTIFICATION, Style, ClickAction, XingeApp, MessageIOS


DEVICE_IOS = 0
DEVICE_ANDROID = 0

OS_TYPE_ANDROID = 0
OS_TYPE_IOS = 1


class PushInstance(object):
    def factory(os_type, open_id, title, message, target, extra):
        if os_type == OS_TYPE_ANDROID:
            return AndroidPush(os_type, open_id, title, message, target, extra)
        if os_type == OS_TYPE_IOS:
            return IosPush(os_type, open_id, title, message, target, extra)
    factory = staticmethod(factory)


class AndroidPush(PushInstance):

    def __init__(self, os_type, open_id, title, message, target, extra):
        self.os_type = os_type
        self.open_id = open_id
        self.title = title
        self.message = message
        self.target = target
        self.extra = extra
        self.custom = {
            'visibility': 'public',
            'target': self.target,
            'extra': self.extra
        }

    def send_push_notification(self):
        access_id = '2100257323'
        secret_key = 'e7c3215b9b837132ae73f5493b15ad3b'

        message = self.build_notification_msg()
        message.custom = self.custom
        push_app = XingeApp(access_id, secret_key)
        ret_code = push_app.PushSingleAccount(DEVICE_ANDROID, self.open_id, message)
        print('SEND PUSH NOTIFICATION : ', ret_code)

    def build_notification_msg(self):
        msg = Message()
        msg.type = MESSAGE_TYPE_ANDROID_NOTIFICATION
        msg.title = self.title
        msg.content = self.message
        msg.style = Style(1, 1)
        action = ClickAction()
        action.actionType = 1
        action.activity = 'com.kolon.viastelle.ui.push.PushGatewayActivity'
        action.intent = ''
        msg.action = action
        return msg


class IosPush(PushInstance):

    def __init__(self, os_type, open_id, title, message, target, extra):
        self.os_type = os_type
        self.open_id = open_id
        self.title = title
        self.message = message
        self.target = target
        self.extra = extra
        self.custom = {
            'visibility': 'public',
            'target': self.target,
            'extra': self.extra
        }

    def send_push_notification(self):
        if settings.DEBUG:
            server_env = 2
        else:
            server_env = 1

        access_id = '2200264357'
        secret_key = '28b4e56f299a5521a005d8d787d17cba'

        message = self.build_notification_msg()
        push_app = XingeApp(access_id, secret_key)
        ret_code = push_app.PushSingleAccount(DEVICE_IOS, self.open_id, message, server_env)
        print('SEND PUSH NOTIFICATION : ', ret_code)

    def build_notification_msg(self):
        msg = MessageIOS()
        msg.title = self.title
        msg.alert = {'title': self.title, 'body': self.message}
        msg.sound = 'default'
        msg.custom = self.custom
        return msg
