import datetime
import json
import uuid

import logging
import requests
from django.db.models import F
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import urlmapper
from aries.common.code_msg import get_msg
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse
from aries.users.common.sign_up_func import request_member_promotion, request_share_id_validation
from aries.users.manager.sign_in_manager import SignInManager
from aries.users.manager.user_manager_v2 import UserManagerV2
from aries.users.serializers import UserAccountSerializer, UserGradeSerializer, UserLoginInfoSerializer, \
    UserNotifyInfoSerializer
from aries.users.models import UserLoginInfo, User, UserGrade, ShoppingBag, UserInfo, UserNotifyInfo, SmsAuthHistory
from aries.users.service.user_referrel_service import UserReferralService
from aries.users.service.user_service import UserService

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class SignUp(APIView):
    signup_request = 0

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data
        lang_info = parse_language_v2(request.META)

        logger_info.info(request_data)

        try:
            login_type = request_data['login_type']
            login_key = request_data['login_key']
            login_value = request_data['login_value']
            login_sns_open_id = ''
            login_sns_access_token = ''
            login_sns_refresh_token = ''

            login_type = int(login_type)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Mobile app/web: 0, QQ: 1, WeChat: 2, Password registration: 3
        # Check sms verification & user count
        if login_type == 0:
            user_count = User.objects.filter(mdn=login_key).count()

            # MDN is only one in member pool
            if user_count >= 1:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        get_msg(code.ERROR_1005_USER_ALREADY_REGISTRATION))
                result.set_error(code.ERROR_1005_USER_ALREADY_REGISTRATION)
                logger_error.error(get_msg(code.ERROR_1005_USER_ALREADY_REGISTRATION))
                return Response(result.get_response(), result.get_code())

            today = datetime.datetime.today()
            sms_auth = SmsAuthHistory.objects.filter(date=today, target_mdn=login_key).latest('id')
            sms_auth_count = sms_auth.verification_count

            if not sms_auth.has_verified or sms_auth_count > 3:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        get_msg(code.ERROR_1008_SMS_VALIDATION_INFO_NOT_FOUND))
                result.set_error(code.ERROR_1008_SMS_VALIDATION_INFO_NOT_FOUND)
                logger_error.error(get_msg(code.ERROR_1008_SMS_VALIDATION_INFO_NOT_FOUND))
                return Response(result.get_response(), result.get_code())

            response = requests.get(urlmapper.get_url('USER_SMS_VERIFICATION') + login_key)

            if response.status_code != code.ARIES_200_SUCCESS:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        get_msg(code.ERROR_1008_SMS_VALIDATION_INFO_NOT_FOUND))
                result.set_error(code.ERROR_1008_SMS_VALIDATION_INFO_NOT_FOUND)
                logger_error.error(get_msg(code.ERROR_1008_SMS_VALIDATION_INFO_NOT_FOUND))
                return Response(result.get_response(), result.get_code())

            # create open id
            random_token = str(uuid.uuid4()).split('-')
            open_id = str(random_token[0] + random_token[2] + random_token[4]).upper()

            # get token from server
            if login_type is 0:
                payload = {'user_open_id': open_id, 'user_account': login_key}
            else:
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
            if login_type is 0:
                user_instance = User.objects.create(
                    open_id=open_id,
                    mdn=login_key,
                    name=login_key,
                    mdn_verification=True,
                    access_token=token,
                    parent_type=0
                )
            else:
                user_instance = User.objects.create(
                    open_id=open_id,
                    mdn='',
                    name=open_id[:6],
                    mdn_verification=False,
                    access_token=token
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

            user_notify_info = UserNotifyInfo.objects.create(
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

            user_serializer = UserAccountSerializer(user_instance)
            user_data = user_serializer.data

            # User notify data
            notify_info = UserNotifyInfo.objects.get(user=user_instance)
            notify_info_serializer = UserNotifyInfoSerializer(notify_info)
            notify_info_data = notify_info_serializer.data
            del notify_info_data['id']
            del notify_info_data['user']
            user_data['notification_info'] = notify_info_data

            # User grade data
            user_grade = UserGrade.objects.get(user=user_instance)
            grade_serializer = UserGradeSerializer(user_grade)
            user_data['grade'] = grade_serializer.data
            user_data['connection_account'] = json.loads(user_data['connection_account'])

            result.set('auto_registration', False)
            result.set('user', user_data)

            # If there is Member promotion, call member coupon interface
            member_promo_result = request_member_promotion(open_id, 0, lang_info.accept_lang)
            result.set_map(member_promo_result)
            logger_info.info('[views_sign][SignUp][post][' + str(member_promo_result) + ']')

            if member_promo_result['has_member_promotion']:
                user_notify_info.has_new_coupon = True
                user_notify_info.coupon_count = 1
                user_notify_info.save()

            # If there is a registration with referrer, update referrer count
            if 'referrer_id' in request_data:
                logger_info.info('[views_sign][SignUp][post][' + 'REFERRER SIGNUP' + ']')
                user_mdn = user_instance.mdn
                user_referral_service = UserReferralService(logger_info, logger_error)

                # Check if its mdn was used for registration before
                registration_check = user_referral_service.read_user_referral_info_check(user_mdn)

                if registration_check:
                    share_id = request_data['referrer_id']
                    referrer_open_id = request_share_id_validation(share_id)

                    # Save User referral history
                    logger_info.info('[views_sign][SignUp][post][' + str(open_id) + ']')
                    logger_info.info('[views_sign][SignUp][post][' + str(user_mdn) + ']')
                    logger_info.info('[views_sign][SignUp][post][' + str(share_id) + ']')
                    logger_info.info('[views_sign][SignUp][post][' + str(referrer_open_id) + ']')

                    ref = user_referral_service.create_user_referral_info(open_id, user_mdn, share_id, referrer_open_id)
                    logger_info.info('[views_sign][SignUp][post][' + str(ref) + ']')

                    user_service = UserService(logger_info, logger_error)
                    referrer_user = user_service.get_user_instance(referrer_open_id)
                    referrer_notify_info = user_service.get_user_notify_info(referrer_user)
                    referrer_notify_info.has_referral_event = True
                    referrer_notify_info.save()
                    logger_info.info('[views_sign][SignUp][post][Notification information saved]')

                    # Send notification
                    user_manager_v2 = UserManagerV2(logger_info, logger_error)
                    user_manager_v2.send_sign_up_push(referrer_open_id, True)
                    logger_info.info('[views_sign][SignUp][post][Send push completed]')
                else:
                    logger_info.info('[views_sign][SignUp][post][Referral already registration.]')

            # Change user info
            user_info = UserInfo.objects.get(user=user_instance)
            user_info.number_of_logon = F('number_of_logon') + 1
            user_info.date_account_last_modified = datetime.datetime.now()
            if 'os_type' in request_data:
                if request_data['os_type'] == 0 or request_data['os_type'] == 1:
                    user_info.os_type = request_data['os_type']
            user_info.save()

            return Response(result.get_response(), status=result.get_code())

        else:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Sign up method not supported')
            logger_info.info('Sign up method not supported')
            return Response(result.get_response(), result.get_code())


class SignIn(APIView):

    def post(self, request):
        request_data = request.data
        logger_info.info(request_data)

        lang_info = parse_language_v2(request.META)

        try:
            login_type = request_data['login_type']
            sign_in_manager = SignInManager(logger_info, logger_error)
            sign_in_manager.set_login_info(login_type, request_data, lang_info.accept_lang)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data is invalid')
            return Response(result.get_response(), result.get_code())

        if sign_in_manager.login_validation():
            result = sign_in_manager.do_sign_in()
            sign_in_manager.update_user_information(request_data)
        else:
            logger_info.info('ID or password is incorrect')
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'ID or password is incorrect.')

        return Response(result.get_response(), result.get_code())


class SignInValidation(APIView):

    def post(self, request):
        request_data = request.data

        try:
            open_id = request_data['open_id']
            access_token = request_data['access_token']
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data is invalid')
            return Response(result.get_response(), result.get_code())

        sign_in_manager = SignInManager(logger_info, logger_error)
        result = sign_in_manager.token_validation(open_id, access_token)

        return Response(result.get_response(), result.get_code())


class SignOut(APIView):
    sign_in_request = 0

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        logger_info.info(request.data)

        serializer = UserLoginInfoSerializer(data=request.data)

        if serializer.is_valid():
            request_data = serializer.data
        else:
            logger_info.info(serializer.errors)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'request data invalid')
            return Response(result.get_response(), result.get_code())

        try:
            login_type = request_data['login_type']

            if login_type == 0:
                login_key = request_data['login_key']
                login_info = UserLoginInfo.objects.filter(login_type=0, login_key=login_key)

                if login_info.count() >= 1:
                    login_info = UserLoginInfo.objects.get(login_type=0, login_key=login_key)
                else:
                    return Response(result.get_response(), result.get_code())

                user = login_info.user
                payload = {'user_open_id': user.open_id, 'user_account': login_key}
                response = requests.delete(urlmapper.get_url('PLATFORM_SERVER'), json=payload)
                logger_info.info(response.text)
            elif login_type == 1 or login_type == 4:
                # QQ case
                open_id = request_data['login_sns_open_id']
                access_token = request_data['login_sns_access_token']
                user = User.objects.get(open_id=open_id, access_token=access_token)
                login_info = UserLoginInfo.objects.filter(login_type=1, user=user)

                if login_info.count() >= 1:
                    login_info = UserLoginInfo.objects.get(login_type=1, user=user)
                    user = login_info.user

                    payload = {'user_open_id': user.open_id, 'user_account': login_info.login_sns_open_id}
                    response = requests.delete(urlmapper.get_url('PLATFORM_SERVER'), json=payload)
                    logger_info.info(response.text)
            else:
                # WeChat case
                open_id = request_data['login_sns_open_id']
                access_token = request_data['login_sns_access_token']
                user = User.objects.get(open_id=open_id, access_token=access_token)
                login_info = UserLoginInfo.objects.filter(login_type=2, user=user)

                if login_info.count() >= 1:
                    login_info = UserLoginInfo.objects.get(login_type=2, user=user)
                    user = login_info.user

                    payload = {'user_open_id': user.open_id, 'user_account': login_info.login_sns_open_id}
                    response = requests.delete(urlmapper.get_url('PLATFORM_SERVER'), json=payload)
                    logger_info.info(response.text)

            return Response(result.get_response(), result.get_code())

        except Exception as e:
            logger_info.info(str(e))
            return Response(result.get_response(), result.get_code())


class SignCallback(APIView):

    def get(self, request):
        print(request)

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        return Response(result.get_response(), result.get_code())
