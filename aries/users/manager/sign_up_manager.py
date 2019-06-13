import datetime
import json
import uuid

import logging
import requests
from django.db.models import F
from rest_framework.response import Response

from aries.common import code
from aries.common import urlmapper
from aries.common.models import ResultResponse
from aries.users.common.sign_up_func import request_member_promotion
from aries.users.models import User, UserLoginInfo, UserInfo, UserNotifyInfo, UserGrade, ShoppingBag

MDN_PASSWORD = 0
QQ_APPLICATION = 1
WECHAT_APPLICATION = 2
WECHAT_PUBLIC = 3
QQ_MOBILE = 4
MDN_QUICK = 5

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class SignUpManager:

    def sign_up(self, login_type, request_data):
        if login_type == QQ_APPLICATION:
            login_key = request_data['login_sns_open_id']
            login_sns_open_id = request_data['login_sns_open_id']
            login_sns_access_token = request_data['login_sns_access_token']

            # Auto sign-up section
            login_value = ''
            login_sns_refresh_token = ''

            # create open id
            random_token = str(uuid.uuid4()).split('-')
            open_id = str(random_token[0] + random_token[2] + random_token[4]).upper()

            # get token from server
            payload = {'user_open_id': open_id, 'user_account': login_sns_open_id}
            response = requests.post(urlmapper.get_url('PLATFORM_SERVER'), json=payload)

            if response.status_code == code.ARIES_200_SUCCESS:
                response_json = response.json()
                token = response_json['token']
                token = str(token).upper()
            else:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'API connection fail')
                result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)
                logger_error.error(response.text)
                return Response(result.get_response(), result.get_code())

            # Sign-up user
            user_instance = User.objects.create(
                open_id=open_id,
                mdn='',
                name=open_id[:6],
                mdn_verification=False,
                access_token=token,
                parent_type=QQ_APPLICATION
            )

            UserLoginInfo.objects.create(
                user=user_instance,
                login_type=QQ_APPLICATION,
                login_key=login_key,
                login_value=login_value,
                login_sns_open_id=login_sns_open_id,
                login_sns_access_token=login_sns_access_token,
                login_sns_refresh_token=login_sns_refresh_token
            )

            UserInfo.objects.create(
                user=user_instance,
                number_of_logon=0
            )

            UserNotifyInfo.objects.create(
                user=user_instance
            )

            UserGrade.objects.create(
                user=user_instance,
                type=0,
                extra_meal_point=0,
                upgrade_date=datetime.datetime.now()
            )

            ShoppingBag.objects.create(
                user=user_instance,
            )

            user_notify_info = UserNotifyInfo.objects.get(user=user_instance)
            user_notify_info.coupon_count = 1
            user_notify_info.save()

            # Connection information
            user_instance.connection_count = F('connection_count') + 1
            connect_info = json.loads(user_instance.connection_account)
            connect_info.append({'login_type': QQ_APPLICATION, 'login_sns_open_id': login_sns_open_id})
            user_instance.connection_account = json.dumps(connect_info)
            user_instance.save()

            login_info = UserLoginInfo.objects.get(login_sns_open_id=login_sns_open_id)
            auto_registration = True

            result = (login_info, login_sns_open_id, auto_registration)

        elif login_type == WECHAT_APPLICATION or login_type == WECHAT_PUBLIC:
            login_key = request_data['login_key']
            login_value = request_data['login_value']
            login_sns_open_id = request_data['login_sns_open_id']
            login_sns_access_token = request_data['login_sns_access_token']
            login_sns_refresh_token = request_data['login_sns_refresh_token']

            # create open id
            random_token = str(uuid.uuid4()).split('-')
            open_id = str(random_token[0] + random_token[2] + random_token[4]).upper()

            # get token from server
            payload = {'user_open_id': open_id, 'user_account': login_sns_open_id}
            response = requests.post(urlmapper.get_url('PLATFORM_SERVER'), json=payload)

            if response.status_code == code.ARIES_200_SUCCESS:
                response_json = response.json()
                token = response_json['token']
                token = str(token).upper()
            else:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'API connection fail')
                result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)
                logger_error.error(response.text)
                return Response(result.get_response(), result.get_code())

            # Sign-up user
            user_instance = User.objects.create(
                open_id=open_id,
                mdn='',
                name=open_id[:6],
                mdn_verification=False,
                access_token=token,
                parent_type=WECHAT_APPLICATION
            )

            UserLoginInfo.objects.create(
                user=user_instance,
                login_type=WECHAT_APPLICATION,
                login_key=login_key,
                login_value=login_value,
                login_sns_open_id=login_sns_open_id,
                login_sns_access_token=login_sns_access_token,
                login_sns_refresh_token=login_sns_refresh_token
            )

            UserInfo.objects.create(
                user=user_instance,
                number_of_logon=0
            )

            UserNotifyInfo.objects.create(
                user=user_instance
            )

            UserGrade.objects.create(
                user=user_instance,
                type=0,
                extra_meal_point=0,
                upgrade_date=datetime.datetime.now()
            )

            ShoppingBag.objects.create(
                user=user_instance,
            )

            user_notify_info = UserNotifyInfo.objects.get(user=user_instance)
            user_notify_info.coupon_count = 1
            user_notify_info.save()

            # Connection information
            user_instance.connection_count = F('connection_count') + 1
            connect_info = json.loads(user_instance.connection_account)
            connect_info.append({'login_type': WECHAT_APPLICATION,
                                 'login_sns_open_id': login_sns_open_id})
            user_instance.connection_account = json.dumps(connect_info)
            user_instance.save()

            login_info = UserLoginInfo.objects.get(login_sns_open_id=login_sns_open_id)
            result = (login_info, login_sns_open_id, True)

        elif login_type == QQ_MOBILE:
            login_key = request_data['login_key']
            login_value = request_data['login_value']
            login_sns_open_id = request_data['login_sns_open_id']
            login_sns_access_token = request_data['login_sns_access_token']
            login_sns_refresh_token = request_data['login_sns_refresh_token']

            # create open id
            random_token = str(uuid.uuid4()).split('-')
            open_id = str(random_token[0] + random_token[2] + random_token[4]).upper()

            # get token from server
            payload = {'user_open_id': open_id, 'user_account': login_sns_open_id}
            response = requests.post(urlmapper.get_url('PLATFORM_SERVER'), json=payload)

            if response.status_code == code.ARIES_200_SUCCESS:
                response_json = response.json()
                token = response_json['token']
                token = str(token).upper()
            else:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'API connection fail')
                result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)
                logger_error.error(response.text)
                return Response(result.get_response(), result.get_code())

            # Sign-up user
            user_instance = User.objects.create(
                open_id=open_id,
                mdn='',
                name=open_id[:6],
                mdn_verification=False,
                access_token=token,
                parent_type=QQ_APPLICATION
            )

            UserLoginInfo.objects.create(
                user=user_instance,
                login_type=QQ_APPLICATION,
                login_key=login_key,
                login_value=login_value,
                login_sns_open_id=login_sns_open_id,
                login_sns_access_token=login_sns_access_token,
                login_sns_refresh_token=login_sns_refresh_token
            )

            UserInfo.objects.create(
                user=user_instance,
                number_of_logon=0
            )

            UserNotifyInfo.objects.create(
                user=user_instance
            )

            UserGrade.objects.create(
                user=user_instance,
                type=0,
                extra_meal_point=0,
                upgrade_date=datetime.datetime.now()
            )

            ShoppingBag.objects.create(
                user=user_instance,
            )

            user_notify_info = UserNotifyInfo.objects.get(user=user_instance)
            user_notify_info.coupon_count = 1
            user_notify_info.save()

            # Connection information
            user_instance.connection_count = F('connection_count') + 1
            connect_info = json.loads(user_instance.connection_account)
            connect_info.append({'login_type': QQ_APPLICATION,
                                 'login_sns_open_id': login_sns_open_id})
            user_instance.connection_account = json.dumps(connect_info)
            user_instance.save()

            login_info = UserLoginInfo.objects.get(login_sns_open_id=login_sns_open_id)
            result = (login_info, login_sns_open_id, True)

        elif login_type == MDN_QUICK:
            login_type = request_data['login_type']
            login_key = request_data['login_key']
            login_value = ''
            login_sns_open_id = ''
            login_sns_access_token = ''
            login_sns_refresh_token = ''

            # create open id
            random_token = str(uuid.uuid4()).split('-')
            open_id = str(random_token[0] + random_token[2] + random_token[4]).upper()

            # get token from server
            payload = {'user_open_id': open_id, 'user_account': login_key}
            response = requests.post(urlmapper.get_url('PLATFORM_SERVER'), json=payload)

            if response.status_code == code.ARIES_200_SUCCESS:
                response_json = response.json()
                token = response_json['token']
                token = str(token).upper()
            else:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'API connection fail')
                result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)
                logger_error.error(response.text)
                return Response(result.get_response(), result.get_code())

            # Sign-up user
            user_instance = User.objects.create(
                open_id=open_id,
                mdn=login_key,
                name=login_key,
                mdn_verification=True,
                access_token=token,
                parent_type=MDN_QUICK
            )

            UserLoginInfo.objects.create(
                user=user_instance,
                login_type=login_type,
                login_key=login_key,
                login_value=login_value,
                login_sns_open_id=login_sns_open_id,
                login_sns_access_token=login_sns_access_token,
                login_sns_refresh_token=login_sns_refresh_token
            )

            UserInfo.objects.create(
                user=user_instance,
                number_of_logon=0
            )

            UserNotifyInfo.objects.create(
                user=user_instance
            )

            UserGrade.objects.create(
                user=user_instance,
                type=0,
                extra_meal_point=0,
                upgrade_date=datetime.datetime.now()
            )

            ShoppingBag.objects.create(
                user=user_instance,
            )

            user_notify_info = UserNotifyInfo.objects.get(user=user_instance)
            user_notify_info.coupon_count = 1
            user_notify_info.save()

            # Change user info
            user_info = UserInfo.objects.get(user=user_instance)
            user_info.number_of_logon = F('number_of_logon') + 1
            user_info.date_account_last_modified = datetime.datetime.now()
            if 'os_type' in request_data:
                if request_data['os_type'] == 0 or request_data['os_type'] == 1:
                    user_info.os_type = request_data['os_type']
            user_info.save()

            user_login_info = UserLoginInfo.objects.get(login_key=login_key)
            result = (user_login_info, login_key, True)

        else:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'NOT SUPPORT LOGIN TYPE')
            result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)
            return Response(result.get_response(), result.get_code())

        return result
