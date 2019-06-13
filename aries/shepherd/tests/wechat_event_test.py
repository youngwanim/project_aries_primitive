import logging

from django.http import QueryDict, HttpRequest
from django.test import TestCase

from aries.shepherd.manager.wechat_event_manager import WechatEventManager


class TestWechatEvent(TestCase):

    """
        self.signature = request.GET.get('signature', None)
        self.timestamp = request.GET.get('timestamp', None)
        self.nonce = request.GET.get('nonce', None)
        self.open_id = request.GET.get('openid', None)
        self.msg_signature = request.GET.get('msg_signature', None)
        self.encrypt_type = request.GET.get('encrypt_type', None)

    """

    logger_info = logging.getLogger('wechat_event_info')
    logger_error = logging.getLogger('wechat_event_error')

    app_id = 'wx41b86399fee7a2ec'
    token = 'nextplatformviastellesuccess'
    encodingAESKey = 'XbN9Qz3U6JTqz3LaeDNKb0zYmun105EQCsDMzroqyHI'

    def setUp(self):
        self.request = HttpRequest()
        self.request_data = """
        <xml>
            <ToUserName><![CDATA[gh_6eac45e83c4f]]></ToUserName>
            <Encrypt><![CDATA[6L6Ayo7wb7Qtiyf8NwZ5ZFAm0ZHuOzRzHv6RQaTOM5cQuqBvMwAQ34FAmw8PwE63pZU64aoj4mDrg1m+7rNdQx6hfX8fhFpiS3X63Or48o3UBgjDidi5Xe97Eucpp1n1xuWGOu8/X5IZcNDzPZnsZS7yPX8vPL2IIaS9PhTHzVd4CJebLwk2JPJaCNrJSeuryg5j5u2/+9WxddPfAuLFKVrHPlgnyIbP34C5wBLVP57qbzSaOg8HzzGOkxZM5zknQLnrRwRcFvPInJxncQ1Xe1j7agxeSPaO4uC5+89WmA2TxBY/htmlH7s1hI7+9ML+WWFJaYPiFH2Bu6piusCOrxqX7KEaWunYfHdhE8+DV/UBvXMaTDzSDzP1dDUK8zGFHlUg33eJcgM9YcPyub4+/ygeMdFC9B3gt3IYdkBEqD+NUc6Auqgb+QNlki8gGWQlqkvxFtp9DjYb9yaQPOYnc6Qo+Kco10pa6n5iJVQ/tA5jPLM4vSxSq1bbx2iywDmbwjBFLA9whPFnLGkZuTmjmwsmgZkyVrlwZAnRLQ/CuFUhCKky44CDIeyzAz0nF9nzxEyPpZu9bhAb9sYMcCsexA==]]></Encrypt>
        </xml>
        """
        http_get_dict = QueryDict(mutable=True)
        http_get_dict['signature'] = '47590e8b083f3bdac8ae6ac64c05649eaaffde24'
        http_get_dict['timestamp'] = '1519103302'
        http_get_dict['nonce'] = '657919367'
        http_get_dict['openid'] = 'ogzIT1I9CXtUD0LPgJ2flVeG3630'
        http_get_dict['msg_signature'] = '2447ffe261fabab3b31b2982569e95883923099f'
        http_get_dict['encrypt_type'] = 'aes'
        self.request.GET = http_get_dict

    def test_event_manager(self):
        event_manager = WechatEventManager(self.logger_info, self.logger_error, self.request)

        self.assertEqual(self.request.GET['signature'], event_manager.signature)
        self.assertEqual(self.request.GET['timestamp'], event_manager.timestamp)
        self.assertEqual(self.request.GET['nonce'], event_manager.nonce)
        self.assertEqual(self.request.GET['openid'], event_manager.open_id)
        self.assertEqual(self.request.GET['msg_signature'], event_manager.msg_signature)
        self.assertEqual(self.request.GET['encrypt_type'], event_manager.encrypt_type)

        self.assertEqual(True, event_manager.request_validation()[0])

        decrypt_message = event_manager.get_decrypt_message(self.token, self.encodingAESKey, self.app_id, self.request_data)
        self.assertEqual(True, decrypt_message[0])

    def test_fail_case_01(self):
        http_get_dict = QueryDict(mutable=True)
        http_get_dict['timestamp'] = '1519103302'
        http_get_dict['nonce'] = '657919367'
        http_get_dict['openid'] = 'ogzIT1I9CXtUD0LPgJ2flVeG3630'
        http_get_dict['encrypt_type'] = 'aes'
        self.request.GET = http_get_dict

        event_manager = WechatEventManager(self.logger_info, self.logger_error, self.request)

        self.assertEqual(self.request.GET['timestamp'], event_manager.timestamp)
        self.assertEqual(self.request.GET['nonce'], event_manager.nonce)
        self.assertEqual(self.request.GET['openid'], event_manager.open_id)
        self.assertEqual(self.request.GET['encrypt_type'], event_manager.encrypt_type)

        self.assertEqual(False, event_manager.request_validation()[0])

    def test_fail_case_02(self):
        self.request.GET['msg_signature'] = 'WJORJWOFJS'
        event_manager = WechatEventManager(self.logger_info, self.logger_error, self.request)

        decrypt_message = event_manager.get_decrypt_message(self.token, self.encodingAESKey, self.app_id, self.request_data)
        self.assertEqual(False, decrypt_message[0])
