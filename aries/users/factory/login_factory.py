import logging
import aries.users.common.user_func as user_util

from collections import namedtuple

from aries.common import code
from aries.common.exceptions.exceptions import AuthInfoError
from aries.users.service.user_service import UserService

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')

MDN_PASSWORD = 0
QQ_APPLICATION = 1
WECHAT_APPLICATION = 2
WECHAT_PUBLIC = 3
QQ_MOBILE = 4
MDN_QUICK = 5


def get_named_tuple(login_success, login_type, login_data, login_info, err_code=None):
    Login = namedtuple('Login', 'login_success login_type login_data login_info err_code')
    login_instance = Login(
        login_success=login_success, login_type=login_type,
        login_data=login_data, login_info=login_info, err_code=err_code
    )
    return login_instance


class UserLoginInstance(object):
    result = False
    login_info = None
    err_code = None
    login_service = UserService(logger_info, logger_error)

    def factory(login_type, request_data):
        if login_type == MDN_PASSWORD:
            login_instance = MdnPasswordLogin(request_data)
            return login_instance
        elif login_type == QQ_APPLICATION:
            return QqApplicationLogin(request_data)
        elif login_type == WECHAT_APPLICATION or login_type == WECHAT_PUBLIC:
            return WechatLogin(request_data)
        elif login_type == QQ_MOBILE:
            return QqWebLogin(request_data)
        elif login_type == MDN_QUICK:
            return MdnQuickLogin(request_data)

    factory = staticmethod(factory)


class MdnPasswordLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        login_key = self.login_data['login_key']
        login_value = self.login_data['login_value']

        try:
            self.login_info = self.login_service.get_login_info_with_key_value(login_key, login_value)
        except Exception as e:
            logger_info.info(str(e))
        else:
            self.result = True

        return get_named_tuple(self.result, MDN_PASSWORD, self.login_data, self.login_info)


class QqApplicationLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        login_sns_open_id = self.login_data['login_sns_open_id']

        try:
            self.login_info = self.login_service.get_login_info_with_sns_open_id(login_sns_open_id)
        except Exception as e:
            logger_info.info(str(e))
        else:
            self.result = True

        return get_named_tuple(self.result, QQ_APPLICATION, self.login_data, self.login_info)


class WechatLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        login_type = self.login_data['login_type']
        login_sns_open_id = self.login_data['login_sns_open_id']

        try:
            response_json = user_util.get_wechat_account_information(login_type, login_sns_open_id)
            logger_info.info(response_json)

            login_sns_open_id = response_json['unionid']
            self.login_info = self.login_service.get_login_info_with_sns_open_id(login_sns_open_id)
        except AuthInfoError as e:
            logger_info.info(str(e))
            self.err_code = code.ERROR_1011_ACCESS_TOKEN_GET_FAIL
        except Exception as e:
            logger_info.info(str(e))
        else:
            self.result = True

        return get_named_tuple(self.result, login_type, self.login_data, self.login_info, self.err_code)


class QqWebLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        login_type = self.login_data['login_type']
        login_sns_open_id = self.login_data['login_sns_open_id']

        try:
            response_json = user_util.get_qq_account_information(login_sns_open_id)
            logger_info.info('[login_factory][QqWebLogin][get_login_info]['+response_json+']')

            qq_access_token = response_json['access_token']
            qq_exprires_in = response_json['expires_in']
            qq_refresh_token = response_json['refresh_token']

            logger_info.info('[login_factory][QqWebLogin][get_login_info][' + qq_access_token + ','
                             + qq_exprires_in + ',' + qq_refresh_token + ']')

            login_sns_open_id = user_util.get_qq_open_id(qq_access_token)
            self.login_info = self.login_service.get_login_info_with_sns_open_id(login_sns_open_id)
        except AuthInfoError as e:
            logger_info.info(str(e))
            self.err_code = code.ERROR_1011_ACCESS_TOKEN_GET_FAIL
        except Exception as e:
            logger_info.info(str(e))
        else:
            self.result = True

        return get_named_tuple(self.result, login_type, self.login_data, self.login_info, self.err_code)


class MdnQuickLogin(UserLoginInstance):
    def __init__(self, login_data):
        self.login_data = login_data

    def get_login_info(self):
        login_type = self.login_data['login_type']
        login_key = self.login_data['login_key']
        login_value = self.login_data['login_value']

        try:
            user_util.sms_authentication(login_key, login_value)
            self.login_info = self.login_service.get_login_info_with_mdn(login_key)
        except AuthInfoError as e:
            logger_info.info(str(e))
            self.err_code = code.ERROR_1003_SMS_VERIFICATION_FAILURE
        except Exception as e:
            logger_info.info(str(e))
        else:
            self.result = True

        return get_named_tuple(self.result, login_type, self.login_data, self.login_info, self.err_code)
