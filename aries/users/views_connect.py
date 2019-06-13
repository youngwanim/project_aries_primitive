import json
import logging

import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.parse import parse_qs

from aries.common import code, code_msg
from aries.common import resources
from aries.common import urlmapper
from aries.common.code_msg import get_msg
from aries.common.models import ResultResponse
from aries.users.models import User, UserLoginInfo

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class Sign(object):
    login_type = 0
    login_key = ''
    login_value = ''
    login_sns_open_id = ''
    login_sns_access_token = ''
    login_sns_refresh_token = ''

    def get_login_type(self):
        if self.login_type == 1 or self.login_type == 4:
            return 1
        elif self.login_type == 2 or self.login_type == 3:
            return 2
        else:
            return 0


class ConnectDetail(APIView):

    def post(self, request):
        print(request.data)
        request_data = request.data
        logger_info.info(request_data)

        sign_obj = Sign()

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]

            sign_obj.login_type = request_data['login_type']
            sign_obj.login_sns_open_id = request_data['login_sns_open_id']
            sign_obj.login_sns_access_token = request_data['login_sns_access_token']
            sign_obj.login_sns_refresh_token = ''

            user = User.objects.get(open_id=open_id, access_token=access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        if sign_obj.login_type == 0:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Not supported connect method')
            return Response(result.get_response(), result.get_code())

        # Check login information
        try:
            if sign_obj.login_type == 1:
                # In case of QQ
                login_info_count = UserLoginInfo.objects.filter(
                    login_sns_open_id=sign_obj.login_sns_open_id).count()

                if login_info_count >= 1:
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            code_msg.get_msg(code.ERROR_1010_USER_ALREADY_CONNECTION))
                    result.set_error(code.ERROR_1010_USER_ALREADY_CONNECTION)
                    return Response(result.get_response(), result.get_code())

                UserLoginInfo.objects.create(
                    user=user,
                    login_type=sign_obj.login_type,
                    login_key=sign_obj.login_key,
                    login_value=sign_obj.login_value,
                    login_sns_open_id=sign_obj.login_sns_open_id,
                    login_sns_access_token=sign_obj.login_sns_access_token,
                    login_sns_refresh_token=sign_obj.login_sns_refresh_token
                )

                user.connection_count += 1
                connect_info = json.loads(user.connection_account)
                new_info = {'login_type': sign_obj.get_login_type(), 'login_sns_open_id': sign_obj.login_sns_open_id}
                connect_info.append(new_info)
                user.connection_account = json.dumps(connect_info)
                user.save()

                result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
                result.set('login_type', sign_obj.get_login_type())
                result.set('login_sns_open_id', sign_obj.login_sns_access_token)
                return Response(result.get_response(), result.get_code())

            elif sign_obj.login_type == 2 or sign_obj.login_type == 3:
                # WeChat SNS login
                login_sns_open_id = request_data['login_sns_open_id']
                if sign_obj.login_type == 2:
                    # WeChat app login
                    payload = {'appid': 'wx87010cb61b99206d', 'secret': '21b9cf8d51b704fd244f40b351d7876e',
                               'code': login_sns_open_id, 'grant_type': 'authorization_code'}
                else:
                    # WeChat public account login
                    payload = {'appid': 'wx41b86399fee7a2ec', 'secret': '1b3d5dce9860be7e4fc04847df6a6177',
                               'code': login_sns_open_id, 'grant_type': 'authorization_code'}
                    sign_obj.login_type = 2

                response = requests.get(resources.WECHAT_ACCESS_TOKEN_URL, params=payload)
                if response.status_code != code.ARIES_200_SUCCESS:
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            code_msg.get_msg(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL))
                    result.set_error(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL)
                    logger_error.error(code_msg.get_msg(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL))
                    return Response(result.get_response(), result.get_code())

                response_json = response.json()
                print(response.text)

                if response_json.get('unionid'):
                    sign_obj.login_key = response_json['openid']
                    sign_obj.login_value = ''
                    sign_obj.login_sns_open_id = response_json['unionid']
                    sign_obj.login_sns_access_token = response_json['access_token']
                    sign_obj.login_sns_refresh_token = response_json['refresh_token']

                    wechat_count = UserLoginInfo.objects.filter(login_type=sign_obj.login_type,
                                                                login_sns_open_id=sign_obj.login_sns_open_id).count()

                    if wechat_count >= 1:
                        result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                                code_msg.get_msg(code.ERROR_1010_USER_ALREADY_CONNECTION))
                        result.set_error(code.ERROR_1010_USER_ALREADY_CONNECTION)
                        logger_error.error(code_msg.get_msg(code.ERROR_1010_USER_ALREADY_CONNECTION))
                        return Response(result.get_response(), result.get_code())
                else:
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            code_msg.get_msg(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL))
                    result.set_error(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL)
                    logger_error.error(code_msg.get_msg(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL))
                    return Response(result.get_response(), result.get_code())

                UserLoginInfo.objects.create(
                    user=user,
                    login_type=sign_obj.login_type,
                    login_key=sign_obj.login_key,
                    login_value=sign_obj.login_value,
                    login_sns_open_id=sign_obj.login_sns_open_id,
                    login_sns_access_token=sign_obj.login_sns_access_token,
                    login_sns_refresh_token=sign_obj.login_sns_refresh_token
                )

                user.connection_count += 1
                connect_info = json.loads(user.connection_account)
                new_info = {'login_type': sign_obj.get_login_type(), 'login_sns_open_id': sign_obj.login_sns_open_id}
                connect_info.append(new_info)
                user.connection_account = json.dumps(connect_info)
                user.save()

                result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
                result.set('login_type', sign_obj.get_login_type())
                result.set('login_sns_open_id', sign_obj.login_sns_open_id)
                return Response(result.get_response(), result.get_code())

            elif sign_obj.login_type == 4:
                # QQ mobile web connect
                login_sns_open_id = request_data['login_sns_open_id']

                payload = {'grant_type': 'authorization_code', 'client_id': '1106290901',
                           'client_secret': 'WbcNyj80WeBvgoSs', 'code': login_sns_open_id,
                           'redirect_uri': 'https://api.viastelle.com/users/signin/callback'}
                response = requests.get(resources.QQ_ACCESS_TOKEN_URL, params=payload)
                print(response.text)
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

                    qq_count = UserLoginInfo.objects.filter(login_sns_open_id=login_sns_access_token).count()

                    if qq_count >= 1:
                        result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                                code_msg.get_msg(code.ERROR_1010_USER_ALREADY_CONNECTION))
                        result.set_error(code.ERROR_1010_USER_ALREADY_CONNECTION)
                        logger_error.error(code_msg.get_msg(code.ERROR_1010_USER_ALREADY_CONNECTION))
                        return Response(result.get_response(), result.get_code())

                    UserLoginInfo.objects.create(
                        user=user,
                        login_type=sign_obj.get_login_type(),
                        login_key='',
                        login_value='',
                        login_sns_open_id=login_sns_access_token,
                        login_sns_access_token=qq_access_token,
                        login_sns_refresh_token=qq_refresh_token
                    )

                else:
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            get_msg(code.ERROR_1101_NOT_SUPPORTED_FILE_FORMAT))
                    result.set_error(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL)
                    logger_error.error(get_msg(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL))
                    return Response(result.get_response(), result.get_code())

                user.connection_count += 1
                connect_info = json.loads(user.connection_account)
                new_info = {'login_type': sign_obj.get_login_type(), 'login_sns_open_id': login_sns_access_token}
                connect_info.append(new_info)
                user.connection_account = json.dumps(connect_info)
                user.save()

                result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
                result.set('login_type', sign_obj.get_login_type())
                result.set('login_sns_open_id', login_sns_access_token)
                return Response(result.get_response(), result.get_code())

            else:
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
                return Response(result.get_response(), result.get_code())

        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, e)
            return Response(result.get_response(), result.get_code())

    def put(self, request):
        request_data = request.data
        logger_info.info(request_data)

        sign_obj = Sign()

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]

            sign_obj.login_type = request_data['login_type']
            sign_obj.login_sns_open_id = request_data['login_sns_open_id']
            sign_obj.login_sns_access_token = ''
            sign_obj.login_sns_refresh_token = ''

            user = User.objects.get(open_id=open_id, access_token=access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        try:
            login_info = UserLoginInfo.objects.filter(user=user, login_sns_open_id=sign_obj.login_sns_open_id)

            count = UserLoginInfo.objects.filter(user=user).count()

            if (count - login_info.count()) <= 0:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        code_msg.get_msg(code.ERROR_1013_ONLY_ONE_LOGIN_INFO))
                result.set_error(code.ERROR_1013_ONLY_ONE_LOGIN_INFO)
                logger_error.error(code_msg.get_msg(code.ERROR_1013_ONLY_ONE_LOGIN_INFO))
                return Response(result.get_response(), result.get_code())

            if login_info.count() == 1:
                login_info = UserLoginInfo.objects.get(user=user, login_sns_open_id=sign_obj.login_sns_open_id)
                login_info.delete()

                if user.connection_count == 2 and user.parent_type != 0:
                    # Full connection count - WeChat, QQ
                    # Delete success and change access_token

                    if sign_obj.login_type == 1 or sign_obj.login_type == 4:
                        # Delete QQ account, get a wechat account
                        new_login_info = UserLoginInfo.objects.get(user=user, login_type=2)
                    else:
                        # Delete wechat account, get a qq account
                        new_login_info = UserLoginInfo.objects.get(user=user, login_type=1)

                    payload = {'user_open_id': open_id, 'user_account': login_info.login_sns_open_id,
                               'new_user_account': new_login_info.login_sns_open_id}
                    response = requests.put(urlmapper.get_url('PLATFORM_SERVER'), json=payload)
                    logger_info.info(response.text)

                connect_info = json.loads(user.connection_account)
                logger_info.info(connect_info)

                if connect_info.remove({'login_type': sign_obj.login_type,
                                        'login_sns_open_id': sign_obj.login_sns_open_id}):
                    user.connection_account = json.dumps(connect_info)
                    user.connection_count -= 1
                    user.save()
                else:
                    user.connection_account = json.dumps(connect_info)
                    user.connection_count -= 1
                    user.save()

                result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
                result.set('login_type', sign_obj.login_type)
                result.set('login_sns_open_id', sign_obj.login_sns_open_id)
                return Response(result.get_response(), result.get_code())
            else:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        code_msg.get_msg(code.ERROR_1012_LOGIN_INFO_NOT_FOUND))
                result.set_error(code.ERROR_1012_LOGIN_INFO_NOT_FOUND)
                return Response(result.get_response(), result.get_code())

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, e)
            return Response(result.get_response(), result.get_code())
