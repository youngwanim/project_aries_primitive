import hashlib
import json
from datetime import datetime

import requests
import xmltodict
from django.conf import settings
from wechatpy.pay import utils, WeChatPay

from aries.common import dateformatter
from aries.common import resources

HOST_DEV = 'http://139.196.123.42:8080'
HOST_STG = 'http://192.168.1.210:8080'
HOST_PAYMENT_REL = 'http://192.168.1.106:80'

# PAYMENT
PAYMENT_DEV = HOST_DEV + '/payments'
PAYMENT_STG = HOST_STG + '/payments'
PAYMENT_REL = HOST_PAYMENT_REL + '/payments'


def wechat_payment_str(orderid):
    text = orderid + 'nextplatform!' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    phrase = hashlib.md5()
    phrase.update(text.encode('utf-8'))
    return phrase.hexdigest().upper()


def get_payment_wechat_signing(params):
    api_key = 'viastelle'
    return utils.calculate_signature(params, api_key)


def get_payment_wechat_public_signing(params, nonce_str=''):
    merchant_id = 'viastelle'
    api_key = 'viastelle'

    if settings.DEBUG:
        print('Get payment wechat public keys in JSAPI signing')
        sandbox_key_params = {
            'mch_id': merchant_id,
            'nonce_str': nonce_str,
        }
        signature = utils.calculate_signature(sandbox_key_params, api_key)
        sandbox_key_params['sign'] = signature
        sandbox_key_data = utils.dict_to_xml(sandbox_key_params, signature)

        headers = {'Content-type': 'application/xml'}
        response = requests.post(url=resources.WECHAT_SANDBOX_SIGN_KEY, data=sandbox_key_data, headers=headers)
        print(response.text)

        result_dict = xmltodict.parse(response.text)['xml']
        api_key = result_dict['sandbox_signkey']

        print(api_key)

    return utils.calculate_signature(params, api_key)


def get_payment_wechat_dict_to_xml(params):
    signature = get_payment_wechat_signing(params)
    return utils.dict_to_xml(params, signature)


def get_payment_wechat_public_dict_to_xml(params):
    signature = get_payment_wechat_public_signing(params)
    return utils.dict_to_xml(params, signature)


def get_payment_wechat_app(debug, order_id, total_price, product_title, nonce_str):

    wechat_app_id = 'viastelle'
    merchant_id = 'viastelle'
    ip_addr = '101.132.64.37'
    api_key = 'viastelle'

    total_fee = int(round((total_price*100), 2))

    product_split = product_title.split(' ')
    if len(product_split) >= 4:
        product_body = product_split[0] + ' ' + product_split[1] + ' ' + product_split[2] + '...'
    else:
        product_body = product_title
    product_name = 'Viastelle - ' + product_body

    prepaid_object = {
        'appid': wechat_app_id,
        'body': product_name.replace('\'', '`'),
        'mch_id': merchant_id,
        'nonce_str': nonce_str,
        'notify_url': 'https://api.viastelle.com/payments/wechat/notification/',
        'out_trade_no': order_id,
        'spbill_create_ip': ip_addr,
        'total_fee': total_fee,
        'trade_type': 'APP',
    }

    prepaid_signature = utils.calculate_signature(prepaid_object, api_key)
    prepaid_data = utils.dict_to_xml(prepaid_object, prepaid_signature)

    return prepaid_data


def get_payment_wechat_public(order_id, total_price, product_title, nonce_str, ip_addr, openid):
    wechat_app_id = 'viastelle'
    merchant_id = 'viastelle'
    api_key = 'viastelle'

    if settings.DEBUG:
        total_fee = 101
    else:
        total_fee = int((total_price*100))

    product_split = product_title.split(' ')
    if len(product_split) >= 4:
        product_body = product_split[0] + ' ' + product_split[1]
    else:
        product_body = product_title

    notify_url = resources.get_wechat_notify_url()

    prepaid_object = {
        'appid': wechat_app_id,
        'body': product_body,
        'mch_id': merchant_id,
        'nonce_str': nonce_str,
        'notify_url': notify_url,
        'out_trade_no': order_id,
        'spbill_create_ip': ip_addr,
        'total_fee': total_fee,
        'trade_type': 'JSAPI',
        'openid': openid
    }

    print(prepaid_object)

    if settings.DEBUG:
        print('Get payment wechat public payments')
        sandbox_key_params = {
            'mch_id': merchant_id,
            'nonce_str': nonce_str,
        }
        signature = utils.calculate_signature(sandbox_key_params, api_key)
        sandbox_key_params['sign'] = signature
        sandbox_key_data = utils.dict_to_xml(sandbox_key_params, signature)

        headers = {'Content-type': 'application/xml'}
        response = requests.post(url=resources.WECHAT_SANDBOX_SIGN_KEY, data=sandbox_key_data, headers=headers)
        print(response.text)

        result_dict = xmltodict.parse(response.text)['xml']
        api_key = result_dict['sandbox_signkey']

        print(api_key)
        prepaid_object['total_fee'] = total_fee

    prepaid_signature = utils.calculate_signature(prepaid_object, api_key)
    prepaid_data = utils.dict_to_xml(prepaid_object, prepaid_signature)

    return prepaid_data


def get_payment_wechat_mweb(debug, order_id, total_price, product_title, nonce_str, scene_info, ip_addr):
    wechat_app_id = 'viastelle'
    wechat_public_app_id = 'viastelle'
    merchant_id = 'viastelle'
    merchant_id_public_account = 'viastelle'
    # ip_addr = '139.196.142.226'
    api_key = 'viastelle'
    api_key_public_account = 'viastelle'

    if debug:
        total_fee = int((total_price*100))

        product_split = product_title.split(' ')
        if len(product_split) >= 4:
            product_body = product_split[0] + ' ' + product_split[1] + ' ' + product_split[2] + '...'
        else:
            product_body = product_title

        sandbox_request = {
            'mch_id': merchant_id,
            'nonce_str': nonce_str,
        }

        sandbox_request_sign = utils.calculate_signature(sandbox_request, api_key)
        sandbox_request['sign'] = sandbox_request_sign
        sandbox_xml = utils.dict_to_xml(sandbox_request, sandbox_request_sign)

        headers = {'Content-Type': 'application/xml'}
        response = requests.post(url=resources.WECHAT_SANDBOX_SIGN_KEY, data=sandbox_xml, headers=headers)
        response_data = response.text

        prepaid_result = xmltodict.parse(response_data)['xml']
        sandbox_api_key = prepaid_result['sandbox_signkey']
        product_name = 'Viastelle - ' + product_body

        scene_info = {
            'h5_info': scene_info
        }

        prepaid_object = {
            'appid': wechat_app_id,
            'body': product_name,
            'mch_id': merchant_id,
            'nonce_str': nonce_str,
            'notify_url': 'http://139.196.123.42:8080/payments/wechat/notification/',
            'out_trade_no': order_id,
            'spbill_create_ip': ip_addr,
            'total_fee': total_fee,
            'trade_type': 'MWEB',
            'scene_info': json.dumps(scene_info)
        }

        prepaid_signature = utils.calculate_signature(prepaid_object, sandbox_api_key)
        prepaid_data = utils.dict_to_xml(prepaid_object, prepaid_signature)

        return {'prepaid_data': prepaid_data, 'sandbox_key': sandbox_api_key}
    else:
        total_fee = int((total_price*100))

        product_split = product_title.split(' ')
        if len(product_split) >= 4:
            product_body = product_split[0] + ' ' + product_split[1] + ' ' + product_split[2] + '...'
        else:
            product_body = product_title

        prepaid_object = {
            'appid': wechat_public_app_id,
            'body': product_body,
            'mch_id': merchant_id_public_account,
            'nonce_str': nonce_str,
            'notify_url': 'https://api.viastelle.com/payments/wechat/notification/',
            'out_trade_no': order_id,
            'spbill_create_ip': ip_addr,
            'total_fee': total_fee,
            'trade_type': 'JSAPI',
        }

        print(prepaid_object)

        prepaid_signature = utils.calculate_signature(prepaid_object, api_key_public_account)
        prepaid_data = utils.dict_to_xml(prepaid_object, prepaid_signature)

        return prepaid_data


def get_payment_order_app(debug, wechat_app_id, merchant_id, prepaid_id, nonce_str, api_key):
    print(debug)

    timestamp = str(dateformatter.get_timestamp())
    payment_order = {
        'appid': wechat_app_id,
        'partnerid': merchant_id,
        'prepayid': prepaid_id,
        'package': 'Sign=WXPay',
        'noncestr': nonce_str,
        'timestamp': timestamp,
    }

    payment_order_sign = utils.calculate_signature(payment_order, api_key)
    payment_order['sign'] = payment_order_sign

    return payment_order


def get_payment_alipay_mweb(params):
    if settings.DEBUG:
        mobile_url = resources.ALIPAY_DEV_URL + '?' + params
    elif settings.STAGE:
        mobile_url = resources.ALIPAY_DEV_URL + '?' + params
    else:
        mobile_url = resources.ALIPAY_REL_URL + '?' + params
    return mobile_url


def get_payment_app_url(payment_type):
    payment_list = ['/alipay', '/wechat', '/alipay', '/wechat']
    host = [PAYMENT_DEV, PAYMENT_STG, PAYMENT_REL]
    if settings.DEBUG:
        server_type = 0
    elif settings.STAGE:
        server_type = 1
    else:
        server_type = 2
    return host[server_type] + payment_list[payment_type]


def get_payment_wechat_sign_validation(params):
    wechat_app_id = 'viastelle'
    merchant_id = 'viastelle'
    api_key = 'viastelle'
    client = WeChatPay(
        appid=wechat_app_id,
        mch_id=merchant_id,
        api_key=api_key,
    )
    return client.check_signature(params)


def get_order_hash(created_date, user_telephone, delivery_date, open_id):
    delimiter = ':'
    hash_str = str(created_date) + delimiter + user_telephone + delimiter +\
        str(delivery_date) + delimiter + open_id

    return hashlib.sha1(bytes(hash_str, 'utf-8')).hexdigest()


def get_order_id(hash_str, open_id, hub_id):
    hub_list = ['D', 'S', 'P']

    if hub_id == 1 or hub_id == 2:
        hub_code = hub_list[hub_id]
    else:
        hub_code = hub_list[0]

    today_str = str(datetime.today())
    time_factor = today_str.replace('-', '').replace(' ', '').replace(':', '').replace('.', '')[:8]
    hash_factor = hash_str[:10] + open_id[:10]
    return hub_code + time_factor + hashlib.md5(bytes(hash_factor, 'utf-8')).hexdigest()[:8].upper()


def get_coupon_title_str(coupon_name, is_primary_coupon, target_id, product_list):
    product_name = ''

    if is_primary_coupon:
        prefix = '[COUPON] '
    else:
        prefix = '[GIFT COUPON] '

    if target_id != 0:
        for product in product_list:
            if product['id'] == target_id:
                product_name = '\n' + product['menu']['name']
    return prefix + coupon_name + product_name


def get_order_unavailable_msg(cn_header):
    time = 3

    en_message = 'LUNCH UNTIL {0}PM'.format(time)
    cn_message = '午餐到{0}点钟'.format(time)

    if cn_header:
        return cn_message
    else:
        return en_message
