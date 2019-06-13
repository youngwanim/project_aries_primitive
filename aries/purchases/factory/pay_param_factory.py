from abc import abstractmethod

import requests
import xmltodict
from alipay import AliPay
from django.conf import settings

from aries.common import resources, urlmapper, payment_util, code, dateformatter
from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.message_utils import message_mapper
from aries.common.resources import get_wechat_prepaid_url

ALIPAY_APP = 0
WECHAT_APP = 1
ALIPAY_MWEB = 2
WECHAT_PUBLIC = 3


class PayParamInstance(object):

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

    @abstractmethod
    def get_payment_params(self, payment_params):
        pass

    def factory(payment_type, logger_info, logger_error):
        if payment_type == ALIPAY_APP:
            return AlipayApp(logger_info, logger_error)
        elif payment_type == WECHAT_APP:
            return WechatApp(logger_info, logger_error)
        elif payment_type == ALIPAY_MWEB:
            return AlipayMweb(logger_info, logger_error)
        elif payment_type == WECHAT_PUBLIC:
            return WechatPublic(logger_info, logger_error)
    factory = staticmethod(factory)


class AlipayApp(PayParamInstance):

    def get_payment_params(self, payment_params):
        if settings.DEBUG:
            debug = True
        elif settings.STAGE:
            debug = True
        else:
            debug = False

        alipay = AliPay(
            debug=debug,
            appid=resources.get_alipay_app_id(),
            app_notify_url=urlmapper.get_url('ALIPAY_CALLBACK_URL'),
            app_private_key_path=resources.get_viastelle_pri_key(),
            alipay_public_key_path=resources.get_viastelle_pub_key(),
            sign_type="RSA2"
        )

        payment_order = alipay.api_alipay_trade_app_pay(
            out_trade_no=payment_params['order_id'],
            total_amount=payment_params['total_price'],
            subject=payment_params['product_title'],
        )
        self.logger_info.info(payment_order)
        param_result = {'alipay_order': payment_order}

        return param_result


class WechatApp(PayParamInstance):
    wechat_app_id = 'wx07120aaebb959414'
    merchant_id = '1498998992'
    api_key = '55baaafdfbbb44a9be261d6b0c978604'

    def get_payment_params(self, payment_params):
        order_id = payment_params['order_id']
        total_price = payment_params['total_price']
        product_title = payment_params['product_title']
        cn_header = payment_params['cn_header']

        nonce_str = payment_util.wechat_payment_str(order_id)
        prepaid_data = payment_util.get_payment_wechat_app(False, order_id, total_price, product_title, nonce_str)

        self.logger_info.info(prepaid_data)
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(url=get_wechat_prepaid_url(), data=prepaid_data, headers=headers)

        if response.status_code != code.ARIES_200_SUCCESS:
            self.logger_error.error(code.ERROR_4004_PAYMENT_INTERFACE_FAILED)
            raise BusinessLogicError(message_mapper.get(4004, cn_header), 4004, None)

        response_data = response.text
        prepaid_result = xmltodict.parse(response_data)['xml']
        self.logger_info.info(prepaid_result)

        if not self.check_prepaid_result(prepaid_result):
            self.logger_error.error(code.ERROR_4004_PAYMENT_INTERFACE_FAILED)
            raise BusinessLogicError(message_mapper.get(4004, cn_header), 4004, None)

        prepaid_id = prepaid_result['prepay_id']
        payment_order = payment_util.get_payment_order_app(
            False, self.wechat_app_id, self.merchant_id, prepaid_id, nonce_str, self.api_key
        )

        self.logger_info.info(payment_order)
        param_result = {'wechat_pay_order': payment_order}

        return param_result

    def check_prepaid_result(self, prepaid_result):
        if prepaid_result['return_code'] == 'FAIL' or prepaid_result['result_code'] != 'SUCCESS' \
                or prepaid_result['appid'] != self.wechat_app_id:
            return False
        else:
            return True


class AlipayMweb(PayParamInstance):

    def get_payment_params(self, payment_params):
        alipay = AliPay(
            debug=settings.DEBUG,
            appid=resources.get_alipay_app_id(),
            app_notify_url=urlmapper.get_url('ALIPAY_CALLBACK_URL'),
            app_private_key_path=resources.get_viastelle_pri_key(),
            alipay_public_key_path=resources.get_viastelle_pub_key(),
        )

        mobile_payment_params = alipay.api_alipay_trade_wap_pay('Viastelle products',
                                                                payment_params['order_id'],
                                                                payment_params['total_price'],
                                                                resources.get_callback_url())
        self.logger_info.info(mobile_payment_params)

        mweb_payment_params = payment_util.get_payment_alipay_mweb(mobile_payment_params)
        param_result = {'mobile_web_payment_params': mweb_payment_params}

        return param_result


class WechatPublic(PayParamInstance):

    def get_payment_params(self, payment_params):
        ip_addr = payment_params['ip_addr']
        wechat_code = payment_params['wechat_code']
        cn_header = payment_params['cn_header']
        order_id = payment_params['order_id']
        total_price = payment_params['total_price']
        product_title = payment_params['product_title']

        # WeChat public account login
        payload = {'appid': 'wx41b86399fee7a2ec', 'secret': '1b3d5dce9860be7e4fc04847df6a6177',
                   'code': wechat_code, 'grant_type': 'authorization_code'}
        response = requests.get(resources.WECHAT_ACCESS_TOKEN_URL, params=payload)
        response_json = response.json()

        if response.status_code != code.ARIES_200_SUCCESS or not response_json.get('openid'):
            raise BusinessLogicError(message_mapper.get(4004, cn_header), 4004, None)

        wechat_openid = response_json['openid']

        nonce_str = payment_util.wechat_payment_str(order_id)
        prepaid_data = payment_util.get_payment_wechat_public(
            order_id, total_price, product_title, nonce_str, ip_addr, wechat_openid
        )
        self.logger_info.info(prepaid_data)

        headers = {'Content-Type': 'application/xml'}
        response = requests.post(url=get_wechat_prepaid_url(), data=prepaid_data, headers=headers)

        if response.status_code != code.ARIES_200_SUCCESS:
            raise BusinessLogicError(message_mapper.get(4004, cn_header), 4004, None)

        response_data = response.text.encode('utf-8')
        prepaid_result = xmltodict.parse(response_data)['xml']

        self.logger_info.info(prepaid_result)

        if prepaid_result['return_code'] == 'FAIL' or prepaid_result['result_code'] != 'SUCCESS':
            raise BusinessLogicError(message_mapper.get(4004, cn_header), 4004, None)

        prepaid_id = prepaid_result['prepay_id']

        mobile_web_payment_params = {
            'appId': 'wx41b86399fee7a2ec',
            'timeStamp': str(dateformatter.get_timestamp()),
            'nonceStr': nonce_str,
            'package': 'prepay_id=' + prepaid_id,
            'signType': 'MD5'
        }

        sign = payment_util.get_payment_wechat_public_signing(mobile_web_payment_params, nonce_str)
        mobile_web_payment_params['paySign'] = sign

        param_result = {'mobile_web_payment_params': mobile_web_payment_params}

        return param_result
