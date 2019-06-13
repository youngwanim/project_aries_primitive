import json

import requests

from aries.common import urlmapper
from aries.common.exceptions.exceptions import AuthInfoError


def check_has_event(open_id, access_token):
    headers = {'open-id': open_id, 'Authorization': 'bearer ' + access_token}
    url = urlmapper.get_url('HAS_EVENT')
    try:
        response = requests.get(url, headers=headers, timeout=3)
    except Exception as e:
        print(e)
        return False

    if response.status_code == 200:
        response_json = response.json()
        result = response_json['event_result']
    else:
        result = False

    return result


def get_wechat_account_information(login_type, login_sns_open_id):
    wechat_application = 2

    if login_type == wechat_application:
        payload = {'appid': 'wx87010cb61b99206d', 'secret': '21b9cf8d51b704fd244f40b351d7876e',
                   'code': login_sns_open_id, 'grant_type': 'authorization_code'}
    else:
        payload = {'appid': 'wx41b86399fee7a2ec', 'secret': '1b3d5dce9860be7e4fc04847df6a6177',
                   'code': login_sns_open_id, 'grant_type': 'authorization_code'}

    response = requests.get(urlmapper.get_url('WECHAT_ACCESS_TOKEN'), params=payload)
    response_json = response.json()

    if not response_json.get('unionid'):
        raise AuthInfoError

    return response_json


def get_qq_account_information(login_sns_open_id):
    payload = {'grant_type': 'authorization_code', 'client_id': '1106290901',
               'client_secret': 'WbcNyj80WeBvgoSs', 'code': login_sns_open_id,
               'redirect_uri': 'https://api.viastelle.com/users/signin/callback'}
    response = requests.get(urlmapper.get_url('QQ_ACCESS_TOKEN'), params=payload)
    response_json = response.json()

    if not response_json.get('access_token'):
        raise AuthInfoError

    return response_json


def get_qq_open_id(qq_access_token):
    payload = {'access_token': qq_access_token}
    response = requests.get(urlmapper.get_url('QQ_OPEN_ID'), params=payload)

    res_text = response.text
    split_res = res_text.split(' ')
    json_result = json.loads(split_res[1])
    response_openid = json_result['openid']

    if not json_result.get('openid'):
        raise AuthInfoError

    return response_openid


def sms_authentication(login_key, login_value):
    url = urlmapper.get_url('USER_SMS_VERIFICATION')
    payload = {'mdn': login_key, 'verification_code': login_value}
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise AuthInfoError

    return True
