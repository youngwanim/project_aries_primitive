import hashlib
import uuid

import os
import pyqrcode
import requests

from aries.common.exceptions.exceptions import AuthInfoError, BusinessLogicError, DataValidationError
from aries.common.urlmapper import url_mapper


def referral_authentication_validation(auth_info):
    if auth_info.open_id is None or auth_info.access_token is None:
        raise AuthInfoError

    if len(auth_info.open_id) != 24:
        raise AuthInfoError


def share_id_param_validation(request_data):
    if 'share_id' not in request_data:
        raise AuthInfoError


def open_id_param_validation(request_data):
    if 'open_id' not in request_data:
        raise AuthInfoError

    if 'validation_key' not in request_data:
        raise AuthInfoError

    valid_key = request_data['validation_key']
    if valid_key != 'apple_upper_case':
        raise AuthInfoError


def get_shared_id(open_id):
    salt = uuid.uuid4().hex
    shorten_id = hashlib.sha256(salt.encode('utf-8') + open_id.encode()).hexdigest()
    return shorten_id[:6]


def get_coupon_information(coupon_list, accept_lang):
    url = url_mapper.get('COUPON_INFORMATION')
    headers = {'accept-language': accept_lang}
    response = requests.post(url, headers=headers, json=coupon_list)

    if response.status_code != 200:
        raise BusinessLogicError('API connection failed', None, None)

    coupon_info = response.json()['coupon_info']

    return coupon_info


def coupon_issue_validation(request_data):
    if 'coupon_list' not in request_data or 'coupon_type' not in request_data:
        raise DataValidationError('Request data invalid', None)


def issue_coupon(open_id, cn_header, coupon_list, coupon_code, sender_id):
    url = url_mapper.get('REFERRAL_COUPON')
    body = {
        'coupon_list': coupon_list, 'open_id': open_id, 'cn_header': cn_header,
        'coupon_code': coupon_code, 'sender_id': sender_id
    }
    response = requests.post(url, json=body)

    if response.status_code != 200:
        raise BusinessLogicError('API connection failed', None, None)


def friend_coupon_naming(discount_price, accept_lang):
    if accept_lang == 'zh' or accept_lang == 'Zh' or accept_lang == 'ZH':
        return '{}元'.format(discount_price)
    else:
        return '¥{}'.format(discount_price)


def pur_coupon_naming(discount_price, accept_lang):
    if accept_lang == 'zh' or accept_lang == 'Zh' or accept_lang == 'ZH':
        return '{}元'.format(discount_price)
    else:
        return '¥{}'.format(discount_price)


def get_coupon_description(expired_day, accept_lang):
    if accept_lang == 'zh' or accept_lang == 'Zh' or accept_lang == 'ZH':
        return '礼券有效期 : 登记后的{}天以内'.format(str(expired_day))
    else:
        return 'Coupon expiration date : within {} days upon issue date'.format(str(expired_day))


def get_image_with_language(referral_event, accept_lang):
    thumbnail_en = 'resources/img/referral/invitation_poster_thumbnail_eng.jpg'
    thumbnail_cn = 'resources/img/referral/invitation_poster_thumbnail_chn.jpg'

    if accept_lang == 'zh' or accept_lang == 'Zh' or accept_lang == 'ZH':
        referral_event['name'] = '邀请好友活动'
        referral_event['invitation_thumbnail'] = thumbnail_cn
    else:
        referral_event['invitation_thumbnail'] = thumbnail_en


def get_share_information(referral_event, accept_lang):
    if accept_lang == 'zh' or accept_lang == 'Zh' or accept_lang == 'ZH':
        referral_event['share_title'] = '加入VIA STELLE，5元享沙拉！'
        referral_event['share_description'] = '现在注册，只花5元购买夏季限定新品沙拉窈窕的象，立省47元！更好美食，更有潮范）'
    else:
        referral_event['share_title'] = 'JOIN VIA STELLE & GET SALAD AT ￥5!'
        referral_event['share_description'] = 'Sign in now and get Skinny Elephant at ￥5,' \
                                              ' save ￥47! HAVE BETTER FOOD, STAY IN STYLE'


def generate_qr_code(unique_id, open_id, access_token):
    content = 'https://m.viastelle.com/reg.html?id=' + unique_id
    qr_code = pyqrcode.create(content, error='M', version=5)

    filename = 'base/media/' + unique_id + '.png'
    qr_code.png(filename, scale=2)
    qr_code_file = open(filename, 'rb')

    url = url_mapper.get('CDN_FILE_UPLOAD') + '/ref_qr'
    files = {'file': qr_code_file}
    headers = {'Authorization': 'bearer ' + access_token, 'open-id': open_id}
    response = requests.post(url, headers=headers, files=files)

    if os.path.isfile(filename):
        os.remove(filename)

    result = True

    # if response.status_code == 401:
    #     raise AuthInfoError

    if response.status_code != 200:
        result = False

    return result


def request_notify_info(open_id, access_token, notify_info_value):
    if notify_info_value:
        notify_value = '0'
    else:
        notify_value = '1'

    url = url_mapper.get('USER_NOTIFICATION_UPDATE').format('referral', notify_value, '0')
    headers = {'Authorization': 'bearer ' + access_token, 'open-id': open_id}
    response = requests.get(url, headers=headers)

    result = False

    if response.status_code == 200:
        result = True

    return result
