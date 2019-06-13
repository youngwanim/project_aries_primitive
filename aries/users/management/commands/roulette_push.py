import datetime

from django.core.management import BaseCommand
from xinge_push import MessageIOS
from xinge_push import XingeApp
from xinge_push import ClickAction
from xinge_push import Message
from xinge_push import Style
from django.conf import settings

from aries.users.models import UserInfo

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

DEVICE_IOS = 0
DEVICE_ANDROID = 0

WEEKDAY_MSG_EN = [
    'Dreadful Monday? Play 100% winning roulette and get lucky from the first day of the week!',
    'What is for lunch? Let the roulette dictate your faith.',
    'Wednesday is the luckiest day of the week, according to a study. Get lucky with the food.',
    'Do not settle for mediocre food just because it is Thursday. Roulette will lead you to choose great food.',
    'Finally, Friday! Start the playful day by playing the roulette.',
    'Still in bed, browsing what to eat? Do not move, spin the wheel and get the deal.',
    'Time to get back to reality, and decide what is for lunch tomorrow. Go find out with the roulette!',
]

WEEKDAY_MSG_CN = [
    '周一综合症？要不来玩玩100%中奖的幸运大转盘！它会消除你的周一压力',
    '今天午餐吃什么呢？ 玩幸运大转盘，获取每日小幸运！',
    '据不记名统计，周三早晨是一个人运气最好的时候！',
    '好烦好烦，周四吃啥呢，好烧脑！来我们这里看一看耍一耍，让天意为你做决定',
    '周五终于到啦，开森！来再转一次呗？',
    '还躺在床上吗？再躺一会吧， 反正有我们在',
    '明天就是周一， 回到现实中吧！饭还是要吃的，钱还是要赚的',
]


def build_ios_notification(title, content, custom):
    msg = MessageIOS()
    msg.title = title
    msg.alert = content
    msg.sound = 'default'
    msg.custom = custom
    return msg


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


def send_push_for_ios(open_id_list, title, content, custom):
    if settings.DEBUG:
        server_environ = 2
    else:
        server_environ = 1

    access_id = '2200264357'
    secret_key = '28b4e56f299a5521a005d8d787d17cba'

    message = build_ios_notification(title, content, custom)
    push_app = XingeApp(access_id, secret_key)
    ret_code, error_msg, third = push_app.PushAccountList(DEVICE_IOS, open_id_list, message, server_environ)
    print(ret_code, error_msg, third)

    if ret_code:
        result = False
        print('Push failed! retcode: {}, msg: {}'.format(ret_code, error_msg))
    else:
        result = True
        print('Push successfully')

    return result


def send_push_for_android(open_id_list, title, content, custom):
    access_id = '2100257323'
    secret_key = 'e7c3215b9b837132ae73f5493b15ad3b'

    message = build_android_notification(title, content)
    message.custom = custom

    push_app = XingeApp(access_id, secret_key)
    ret_code, error_msg, third = push_app.PushAccountList(DEVICE_ANDROID, open_id_list, message)
    print(ret_code, error_msg, third)

    if ret_code:
        result = False
        print('Push failed! retcode: {}, msg: {}'.format(ret_code, error_msg))
    else:
        result = True
        print('Push successfully')

    return result


def get_cn_header(locale):
    if locale == 'en' or locale == 'EN' or locale == 'En':
        return False
    else:
        return True


def get_user_list(os_type):
    target_user = []
    user_info_list = UserInfo.objects.filter(os_type=os_type)
    for user_info in user_info_list:
        if user_info.user.push_agreement == 'Y':
            result = (user_info.user.open_id, get_cn_header(user_info.user.locale))
            target_user.append(result)

    return target_user


def send_push_ios(open_id_list):
    today = datetime.datetime.today()

    custom = {
        'visibility': 'public',
        'target': '100',
        'extra': ''
    }

    sending_list_en = []
    sending_list_cn = []

    sending_list = []

    for open_id_object in open_id_list:
        if open_id_object[1]:
            sending_list_cn.append(open_id_object[0])
        else:
            sending_list_en.append(open_id_object[0])

    content_en = {
        'title': 'LUCKY ROULETTE',
        'body': WEEKDAY_MSG_EN[today.weekday()]
    }

    content_cn = {
        'title': '幸运转盘',
        'body': WEEKDAY_MSG_CN[today.weekday()]
    }

    for open_id in sending_list_en:
        sending_list.append(open_id)

        if len(sending_list) == 100:
            send_push_for_ios(sending_list, 'LUCKY ROULETTE', content_en, custom)
            sending_list.clear()

    send_push_for_ios(sending_list, 'LUCKY ROULETTE', content_en, custom)
    sending_list.clear()

    for open_id in sending_list_cn:
        sending_list.append(open_id)

        if len(sending_list) == 100:
            send_push_for_ios(sending_list, '幸运转盘', content_cn, custom)
            sending_list.clear()

    send_push_for_ios(sending_list, '幸运转盘', content_cn, custom)
    sending_list.clear()


def send_push_android(open_id_list):
    today = datetime.datetime.today()

    custom = {
        'visibility': 'public',
        'target': '100',
        'extra': ''
    }

    sending_list_en = []
    sending_list_cn = []

    sending_list = []

    for open_id_object in open_id_list:
        if open_id_object[1]:
            sending_list_cn.append(open_id_object[0])
        else:
            sending_list_en.append(open_id_object[0])

    content_en = WEEKDAY_MSG_EN[today.weekday()]
    content_cn = WEEKDAY_MSG_CN[today.weekday()]

    for open_id in sending_list_en:
        sending_list.append(open_id)

        if len(sending_list) == 100:
            send_push_for_android(sending_list, 'LUCKY ROULETTE', content_en, custom)
            sending_list.clear()

    send_push_for_android(sending_list, 'LUCKY ROULETTE', content_en, custom)
    sending_list.clear()

    for open_id in sending_list_cn:
        sending_list.append(open_id)

        if len(sending_list) == 100:
            send_push_for_android(sending_list, '幸运转盘', content_cn, custom)
            sending_list.clear()

    send_push_for_android(sending_list, '幸运转盘', content_cn, custom)
    sending_list.clear()


class Command(BaseCommand):

    def handle(self, *args, **options):
        user_list = get_user_list(0)
        print(user_list)
        send_push_android(user_list)

        user_list = get_user_list(1)
        print(user_list)
        send_push_ios(user_list)
