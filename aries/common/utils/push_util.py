import requests

from aries.common import urlmapper
from aries.common.utils import message_util

PUSH_ORDER_COMPLETE = 0
PUSH_ORDER_CANCEL = 4


TARGET_UPCOMING = 1
TARGET_DELIVERY_COMPLETE = 2
TARGET_ORDER_CANCEL = 3
TARGET_REVIEW = 4
TARGET_PROMOTION = 5
TARGET_MY_NEWS = 6


class PushInstance(object):
    def factory(push_type, os_type, order_id, open_id, access_token, cn_header):
        if push_type == PUSH_ORDER_COMPLETE:
            return OrderComplete(os_type, order_id, open_id, access_token, cn_header)
        if push_type == PUSH_ORDER_CANCEL:
            return OrderCanceled(os_type, order_id, open_id, access_token, cn_header)
    factory = staticmethod(factory)

    def get_headers(self, access_token):
        return {'authorization': 'bearer ' + access_token}

    def get_push_msg(self, open_id, target, order_id, message):
        payload = {
            'open_id': open_id,
            'title': 'VIASTELLE',
            'content': message,
            'custom': {
                'visibility': 'public',
                'target': target,
                'extra': order_id
            }
        }
        return payload


class OrderComplete(PushInstance):

    def __init__(self, os_type, order_id, open_id, access_token, cn_header):
        self.os_type = os_type
        self.order_id = order_id
        self.open_id = open_id
        self.access_token = access_token
        self.cn_header = cn_header

    def get_response(self):
        message = message_util.get_order_success_push(self.cn_header)
        headers = self.get_headers(self.access_token)
        payload = self.get_push_msg(self.open_id, TARGET_UPCOMING, self.order_id, message)
        url = urlmapper.get_push_url(self.os_type)
        response = requests.post(url, headers=headers, json=payload)
        return response


class OrderCanceled(PushInstance):

    def __init__(self, os_type, order_id, open_id, access_token, cn_header):
        self.os_type = os_type
        self.order_id = order_id
        self.open_id = open_id
        self.access_token = access_token
        self.cn_header = cn_header

    def get_response(self):
        message = message_util.get_order_cancel_push(self.cn_header)
        headers = self.get_headers(self.access_token)
        payload = self.get_push_msg(self.open_id, TARGET_ORDER_CANCEL, self.order_id, message)
        url = urlmapper.get_push_url(self.os_type)
        response = requests.post(url, headers=headers, json=payload)
        return response
