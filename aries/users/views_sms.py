import datetime
from threading import Thread

import logging
import requests
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client

from aries.common import code_msg
from aries.common import urlmapper
from aries.common.code_msg import get_msg
from aries.common.models import ResultResponse
from aries.common import code
from aries.common.sms import SmsSingleSender
from aries.users.models import User, UserLoginInfo, SmsAuthHistory
from aries.users.serializers import UserSmsSerializer
import random

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


def verify_mdn(mdn_code):
    if mdn_code.startswith('010'):
        phone_number = '+82' + mdn_code[1:]
    else:
        phone_number = '+86' + mdn_code
    return phone_number


class SmsSender(Thread):

    def __init__(self, mdn, message, isEnglish):
        Thread.__init__(self)
        self.mdn = mdn
        self.message = message
        self.is_english = isEnglish

    def run(self):
        tencent_app_id = '1400040133'
        tencent_app_key = '060b61830d919d6ec773fcd18f0171e7'

        single_sender = SmsSingleSender(tencent_app_id, tencent_app_key)

        if self.mdn.startswith('010'):
            nation = '82'
            templ_id = 42027
        else:
            nation = '86'
            templ_id = 41958

        params = ['<' + self.message + '>', '1']
        result = single_sender.send_with_param(nation, self.mdn, templ_id, params, '', '', '')
        logger_info.info(result)

        return result


class SmsIdSender(Thread):

    def __init__(self, mdn, message):
        Thread.__init__(self)
        logger_info.info(mdn + ':' + message)
        self.mdn = mdn
        self.message = message

    def run(self):
        account_sid = "AC028c29fbdad8919f73351f8d74256721"
        auth_token = "5a8a1e6d150c248dd16b289b53eb8fea"

        client = Client(account_sid, auth_token)
        message = None

        try:
            message = client.messages.create(
                to=verify_mdn(self.mdn),
                from_="+16692316626",
                body="Your viastelle account(" + self.mdn + ") was changed by (" + self.message +
                     "). On next time, please login new account"
            )
        except Exception as e:
            print(e)

        return message


class SmsRequest(APIView):
    verification_code = 0

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)
        mdn = request_data['mdn']

        is_english = True
        if request.META.get('HTTP_ACCEPT_LANGUAGE'):
            accept_lang = request.META['HTTP_ACCEPT_LANGUAGE']
            if 'zh' in accept_lang:
                is_english = False

        if len(mdn) <= 10:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        if 'sms_type' in request_data and request_data['sms_type'] == 1:
            user_count = User.objects.filter(mdn=mdn).count()
            del request_data['sms_type']

            if user_count >= 1:
                error_code = code.ERROR_1005_USER_ALREADY_REGISTRATION
                result_msg = get_msg(error_code, not is_english)
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, result_msg)
                result.set_error(error_code)
                return Response(result.get_response(), result.get_code())

        user_count = User.objects.filter(mdn=mdn).count()
        serializer = UserSmsSerializer(data=request_data)

        if serializer.is_valid():
            user_model = serializer.data
            self.verification_code = '%06d' % random.randint(1, 999999)

            today = datetime.datetime.today()
            sms_auth_history = SmsAuthHistory.objects.create(
                date=today,
                target_mdn=mdn,
                verification_code=self.verification_code,
                has_verified=False
            )

            if sms_auth_history is None:
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
                return Response(result.get_response(), result.get_code())

            sender = SmsSender(user_model.get('mdn'), self.verification_code, is_english)
            sender.start()

            cache.set(user_model.get('mdn'), self.verification_code, 70)

            if user_count >= 1:
                result.set('member_check', True)
            else:
                result.set('member_check', False)
        else:
            logger_info.info('Request data invalid')
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        logger_info.info(result.get_response())
        return Response(result.get_response(), status=result.get_code())


class SmsVerification(APIView):

    def get(self, request, login_key):
        verification_code = str(cache.get(login_key))
        logger_info.info(login_key + ':' + str(cache.get(login_key)))

        if len(verification_code) < 6:
            logger_error.error('Unauthorized')
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'It needs verification')
            return Response(result.get_response(), result.get_code())

        try:
            cache_data = cache.get(login_key)
            if cache_data == 'complete':
                result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            else:
                logger_info.info('verification failed')
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Verification failed')
                return Response(result.get_response(), result.get_code())
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Verification failed')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        logger_info.info(request.data)

        access_token = ''
        open_id = ''

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            open_id = request.META['HTTP_OPEN_ID']

            user_count = User.objects.filter(open_id=open_id, access_token=access_token).count()
            if user_count == 1:
                user_info = True
            else:
                user_info = False
        except Exception as e:
            logger_info.info(str(e))
            user_info = False

        try:
            mdn = request.data['mdn']
            verification_code = request.data['verification_code']

            today = datetime.datetime.today()
            sms_auth_count = SmsAuthHistory.objects.filter(date=today, target_mdn=mdn).count()

            if sms_auth_count == 0:
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, "Request data validation fail")
                return Response(result.get_response(), result.get_code())

            sms_auth = SmsAuthHistory.objects.filter(date=today, target_mdn=mdn).latest('id')
            system_code = sms_auth.verification_code

            if system_code == verification_code:
                sms_auth.verification_count += 1
                sms_auth.has_verified = True
            else:
                sms_auth.verification_count += 1

            sms_auth.save()
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, "Request data validation fail")
            return Response(result.get_response(), result.get_code())

        cache_data = cache.get(mdn)

        if cache_data is None:
            logger_info.info('verify code is not found')
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, "Verify code is not found")
            return Response(result.get_response(), result.get_code())

        if verification_code == cache_data:
            # Verification success
            cache.set(mdn, 'complete', 300)

            # Update user information
            logger_info.info(user_info)

            if user_info:
                try:
                    # Original user information
                    original_user = User.objects.get(open_id=open_id, access_token=access_token)

                    # Check if already verification member
                    user_login_count = UserLoginInfo.objects.filter(login_key=mdn).count()
                    before_mdn_user_count = User.objects.filter(mdn=mdn).count()

                    if user_login_count == 0 and before_mdn_user_count == 1:
                        before_user = User.objects.get(mdn=mdn)

                        if before_user.open_id == original_user.open_id:
                            original_user.mdn_verification = True
                        else:
                            # 20180130 check
                            original_user.mdn = mdn
                            before_user.mdn = ''
                            before_user.mdn_verification = False

                        original_user.save()
                        before_user.save()
                    elif user_login_count == 1:
                        user_login_info = UserLoginInfo.objects.get(login_key=mdn)
                        user = user_login_info.user

                        if user.open_id != original_user.open_id:
                            # Other mobile member case
                            if "010" in user.name:
                                user.name = user.open_id[:6]
                            user.mdn = ''
                            user.mdn_verification = False
                            user.save()

                            new_mdn = 'dormant_' + mdn + '_' + ('%04d' % random.randint(1, 9999))
                            user_login_info.login_key = new_mdn
                            user_login_info.save()

                            # Send push service
                            sender = SmsIdSender(mdn, new_mdn)
                            sender.start()

                            # Original user information save
                            if "010" in original_user.name:
                                original_user.name = mdn
                            original_user.mdn = mdn
                            original_user.mdn_verification = True
                            original_user.save()

                            login_count = UserLoginInfo.objects.filter(user=original_user, login_type=0).count()

                            if login_count == 1:
                                user_login_origin = UserLoginInfo.objects.get(user=original_user, login_type=0)
                                user_login_origin.login_key = mdn
                                user_login_origin.save()

                            # Original user login information delete
                            payload = {'user_open_id': user.open_id, 'user_account': mdn}
                            response = requests.delete(urlmapper.get_url('PLATFORM_SERVER'), json=payload)
                            logger_info.info(response.text)
                        else:
                            # login info is same
                            user_login_info.login_key = mdn
                            user_login_info.save()

                            original_user.mdn = mdn
                            original_user.mdn_verification = True
                            original_user.save()
                    else:
                        # Check if parent type
                        if original_user.parent_type == 0:
                            original_user_mdn = original_user.mdn
                            original_login_info = UserLoginInfo.objects.get(user=original_user,
                                                                            login_key=original_user_mdn)
                            original_login_info.login_key = mdn
                            original_login_info.save()

                        # SNS member
                        original_user.mdn = mdn
                        original_user.mdn_verification = True
                        original_user.save()

                except Exception as e:
                    logger_error.error(str(e))
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            code_msg.get_msg(code.ERROR_1003_SMS_VERIFICATION_FAILURE))
                    result.set_error(code.ERROR_1003_SMS_VERIFICATION_FAILURE)
                    return Response(result.get_response(), result.get_code())

            result = ResultResponse(code.ARIES_200_SUCCESS, "SMS verification success")
        else:
            logger_info.info('Verification code is different')
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, "Verification code is different")
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())

