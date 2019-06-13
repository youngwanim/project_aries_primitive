import json
import logging
import requests

from urllib.parse import parse_qs
from rest_framework.response import Response

from aries.common import code, code_msg
from aries.common import resources
from aries.common import urlmapper
from aries.common.models import ResultResponse
from aries.users.manager.sign_up_manager import SignUpManager
from aries.users.models import UserLoginInfo, User

MDN_PASSWORD = 0
QQ_APPLICATION = 1
WECHAT_APPLICATION = 2
WECHAT_PUBLIC = 3
QQ_MOBILE = 4
MDN_QUICK = 5

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class UserLoginInstance(object):
    def factory(login_type, request_data):
        if login_type == MDN_PASSWORD:
            login_instance = MdnPasswordLogin(request_data)
            return login_instance
        if login_type == QQ_APPLICATION:
            return QqApplicationLogin(request_data)
        if login_type == WECHAT_APPLICATION or login_type == WECHAT_PUBLIC:
            return WechatLogin(request_data)
        if login_type == QQ_MOBILE:
            return QqWebLogin(request_data)
        if login_type == MDN_QUICK:
            return MdnQuickLogin(request_data)

    factory = staticmethod(factory)


class MdnPasswordLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        login_key = self.login_data['login_key']
        login_value = self.login_data['login_value']
        try:
            login_info = UserLoginInfo.objects.filter(login_key=login_key, login_value=login_value)[0]
        except Exception as e:
            print(e)
            result = (None, None, False)
        else:
            result = (login_info, login_value, False)
        return result


class QqApplicationLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        # QQ SNS login
        login_sns_open_id = self.login_data['login_sns_open_id']

        try:
            login_info = UserLoginInfo.objects.filter(login_sns_open_id=login_sns_open_id)[0]
        except Exception as e:
            print(e)
            sign_up_manager = SignUpManager()
            result = sign_up_manager.sign_up(QQ_APPLICATION, self.login_data)
        else:
            result = (login_info, login_sns_open_id, False)
        return result


class WechatLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        # Wechat Login
        login_sns_open_id = self.login_data['login_sns_open_id']
        login_type = self.login_data['login_type']

        if login_type == WECHAT_APPLICATION:
            # WeChat app login
            payload = {'appid': 'wx87010cb61b99206d', 'secret': '21b9cf8d51b704fd244f40b351d7876e',
                       'code': login_sns_open_id, 'grant_type': 'authorization_code'}
        else:
            # WeChat public account login
            payload = {'appid': 'wx41b86399fee7a2ec', 'secret': '1b3d5dce9860be7e4fc04847df6a6177',
                       'code': login_sns_open_id, 'grant_type': 'authorization_code'}

        response = requests.get(resources.WECHAT_ACCESS_TOKEN_URL, params=payload)
        response_json = response.json()
        logger_info.info(response.text)

        if response_json.get('unionid'):
            login_sns_open_id = response_json['unionid']

            try:
                login_info = UserLoginInfo.objects.filter(login_sns_open_id=login_sns_open_id)[0]
            except Exception as e:
                print(e)
                wechat_login_data = {
                    'login_key': response_json['openid'],
                    'login_value': '',
                    'login_sns_open_id': login_sns_open_id,
                    'login_sns_access_token': response_json['access_token'],
                    'login_sns_refresh_token': response_json['refresh_token']
                }
                sign_up_manager = SignUpManager()
                result = sign_up_manager.sign_up(WECHAT_APPLICATION, wechat_login_data)
            else:
                login_instance = UserLoginInfo.objects.get(login_sns_open_id=login_sns_open_id)
                login_instance.login_sns_access_token = response_json['access_token']
                login_instance.login_sns_refresh_token = response_json['refresh_token']
                login_instance.save()
                result = (login_info, login_sns_open_id, False)
            return result
        else:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                    code_msg.get_msg(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL))
            result.set_error(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL)
            logger_error.error(code_msg.get_msg(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL))
            return Response(result.get_response(), result.get_code())


class QqWebLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        # QQ Mobile web Login
        login_sns_open_id = self.login_data['login_sns_open_id']

        payload = {'grant_type': 'authorization_code', 'client_id': '1106290901',
                   'client_secret': 'WbcNyj80WeBvgoSs', 'code': login_sns_open_id,
                   'redirect_uri': 'https://api.viastelle.com/users/signin/callback'}
        response = requests.get(resources.QQ_ACCESS_TOKEN_URL, params=payload)
        logger_info.info(response.text)

        res_text = response.text

        if 'access_token' in res_text:
            res_json = json.loads(json.dumps(parse_qs(res_text)))
            qq_access_token = res_json['access_token'][0]
            qq_exprires_in = res_json['expires_in'][0]
            qq_refresh_token = res_json['refresh_token'][0]

            payload = {'access_token': qq_access_token}
            response = requests.get(resources.QQ_OPEN_ID_URL, params=payload)

            res_text = response.text
            logger_info.info(res_text)

            split_res = res_text.split(' ')
            json_result = json.loads(split_res[1])
            response_openid = json_result['openid']

            login_sns_access_token = response_openid
            login_sns_open_id = login_sns_access_token

            try:
                login_info = UserLoginInfo.objects.filter(login_sns_open_id=login_sns_open_id)[0]
            except Exception as e:
                print(e)
                qq_login_data = {
                    'login_key': login_sns_access_token,
                    'login_value': '',
                    'login_sns_open_id': login_sns_access_token,
                    'login_sns_access_token': qq_access_token,
                    'login_sns_refresh_token': qq_refresh_token,
                }
                sign_up_manager = SignUpManager()

                result = sign_up_manager.sign_up(QQ_MOBILE, qq_login_data)
            else:
                login_instance = UserLoginInfo.objects.get(login_sns_open_id=login_sns_open_id)
                login_instance.login_sns_access_token = login_sns_access_token
                login_instance.login_sns_refresh_token = qq_refresh_token
                login_instance.save()

                result = (login_info, login_sns_open_id, False)
            return result
        else:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                    code_msg.get_msg(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL))
            result.set_error(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL)
            return Response(result.get_response(), result.get_code())


class MdnQuickLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        # MDN quick login
        login_key = self.login_data['login_key']
        login_value = self.login_data['login_value']

        # Check SMS authentication
        url = urlmapper.get_url('USER_SMS_VERIFICATION')
        payload = {'mdn': login_key, 'verification_code': login_value}
        response = requests.post(url, json=payload)

        if response.status_code == code.ARIES_200_SUCCESS:
            try:
                user_instance = User.objects.get(mdn=login_key)
            except Exception as e:
                print(e)
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        code_msg.get_msg(code.ERROR_1005_USER_ALREADY_REGISTRATION))
                result.set_error(code.ERROR_1005_USER_ALREADY_REGISTRATION)
                logger_error.error(code_msg.get_msg(code.ERROR_1005_USER_ALREADY_REGISTRATION))
                return Response(result.get_response(), result.get_code())
            else:
                login_info = UserLoginInfo.objects.filter(user=user_instance).exclude(login_key__icontains='dormant')[0]
                login_id = login_info.id
                login_info = UserLoginInfo.objects.filter(id=login_id)[0]
                result = (login_info, login_key, False)
            return result
        else:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                    code_msg.get_msg(1003))
            result.set_error(code.ERROR_1003_SMS_VERIFICATION_FAILURE)
            return Response(result.get_response(), result.get_code())


class UserValidationLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        login_key = self.login_data['login_key']
        login_value = self.login_data['login_value']
        login_info = UserLoginInfo.objects.filter(login_key=login_key, login_value=login_value)
        result = (login_info, login_value, False)
        return result

