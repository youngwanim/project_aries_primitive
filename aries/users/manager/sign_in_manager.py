import datetime
import json

import requests
from django.db.models import F

from aries.common import code
from aries.common import urlmapper
from aries.common.models import ResultResponse
from aries.users.common.sign_up_func import request_member_promotion
from aries.users.manager.user_login_factory import UserLoginInstance
from aries.users.models import User, UserGrade, UserNotifyInfo, UserNews, UserInfo
from aries.users.serializers import UserAccountSerializer, UserGradeSerializer, UserNotifyInfoSerializer


class SignInManager:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.user = None
        self.login_info = None
        self.login_account_info = None
        self.auto_registration = None
        self.accept_lang = None

    def set_login_info(self, login_type, request_data, accept_lang='zh'):
        user_login_instance = UserLoginInstance.factory(login_type, request_data)
        login_result = user_login_instance.get_login_info()
        self.login_info = login_result[0]
        self.login_account_info = login_result[1]
        self.auto_registration = login_result[2]
        self.user = User.objects.get(id=self.login_info.user.id)
        self.accept_lang = accept_lang

    def login_validation(self):
        if self.login_info is None:
            return False
        else:
            return True

    def get_token(self):
        payload = {'user_open_id': self.user.open_id, 'user_account': self.login_account_info}
        response = requests.post(urlmapper.get_url('PLATFORM_SERVER'), json=payload)

        if response.status_code == code.ARIES_200_SUCCESS:
            response_json = response.json()
            token = response_json['token']
            result = (True, token)
        else:
            result = (False, None)

        return result

    def update_notification_info(self, open_id, access_token, notify_info):
        url = urlmapper.get_url('NOTIFICATION_COUNT')
        headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}

        notification_response = requests.get(url, headers=headers)

        if notification_response.status_code == code.ARIES_200_SUCCESS:
            notification_json_res = notification_response.json()
            notify_info.coupon_count = notification_json_res['coupon_count']
            notify_info.upcoming_order_count = notification_json_res['upcoming_order_count']
            notify_info.save()

    def update_user_information(self, request_data):
        # Change user info
        user_info = UserInfo.objects.get(user=self.user)
        user_info.number_of_logon = F('number_of_logon') + 1
        user_info.date_account_last_modified = datetime.datetime.now()

        if 'os_type' in request_data:
            if request_data['os_type'] == 0 or request_data['os_type'] == 1:
                user_info.os_type = request_data['os_type']
        user_info.save()

    def do_sign_in(self):
        token_result = self.get_token()

        if token_result[0]:
            token = token_result[1]
        else:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Token validation fail')
            return result

        self.user.access_token = token
        self.user.save()

        user_serializer = UserAccountSerializer(self.user)
        user_data = user_serializer.data

        user_grade = UserGrade.objects.get(user=self.user)
        user_grade_serializer = UserGradeSerializer(user_grade)

        user_data['grade'] = user_grade_serializer.data
        user_data['connection_account'] = json.loads(user_data['connection_account'])

        # User notify data
        notify_info = UserNotifyInfo.objects.get(user=self.user)

        # User notify information update
        user_news_count = UserNews.objects.filter(user=self.user, has_read=False).count()
        notify_info.news_count = user_news_count
        self.update_notification_info(user_data['open_id'], user_data['access_token'], notify_info)

        notify_info_serializer = UserNotifyInfoSerializer(notify_info)
        notify_info_data = notify_info_serializer.data
        del notify_info_data['id']
        del notify_info_data['user']
        user_data['notification_info'] = notify_info_data

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        result.set('user', user_data)
        result.set('auto_registration', self.auto_registration)

        # Member promotion coupon issue section
        if self.auto_registration:
            member_promo_result = request_member_promotion(self.user.open_id, 0, self.accept_lang)
            result.set_map(member_promo_result)

            if member_promo_result['has_member_promotion']:
                notify_info.has_new_coupon = True
                notify_info.coupon_count = 1
                notify_info.save()

        return result

    def token_validation(self, open_id, access_token):
        user = User.objects.filter(open_id=open_id, access_token=access_token)

        if user.count() <= 0 or user.count() > 1:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
            result.set('user', '')
            result.set('auto_registration', False)
            return result

        user = User.objects.get(open_id=open_id, access_token=access_token)

        user_serializer = UserAccountSerializer(user)
        user_data = user_serializer.data

        user_grade = UserGrade.objects.get(user=user)
        user_grade_serializer = UserGradeSerializer(user_grade)

        user_data['grade'] = user_grade_serializer.data
        user_data['connection_account'] = json.loads(user_data['connection_account'])

        # User notify data
        notify_info = UserNotifyInfo.objects.get(user=user)

        # User notify information update
        user_news_count = UserNews.objects.filter(user=user, has_read=False).count()
        notify_info.news_count = user_news_count
        self.update_notification_info(user_data['open_id'], user_data['access_token'], notify_info)

        notify_info_serializer = UserNotifyInfoSerializer(notify_info)
        notify_info_data = notify_info_serializer.data
        del notify_info_data['id']
        del notify_info_data['user']
        user_data['notification_info'] = notify_info_data

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        result.set('user', user_data)
        result.set('auto_registration', False)

        return result
