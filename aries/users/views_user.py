import logging
import requests
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code, code_msg
from aries.common import urlmapper
from aries.common.code_msg import get_msg
from aries.common.models import ResultResponse
from aries.users.models import User, UserGrade, UserLoginInfo, UserInfo, UserNotifyInfo
from aries.users.serializers import UserAccountSerializer, UserSerializer, UserGradeSerializer, UserInfoSerializer

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class UserDetail(APIView):

    def get(self, request, open_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            user_instance = User.objects.get(access_token=access_token, open_id=open_id)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token not found')
            return Response(result.get_response(), result.get_code())

        user_serializer = UserAccountSerializer(user_instance)
        user_data = user_serializer.data

        user_grade = UserGrade.objects.get(user=user_instance)
        user_grade_serializer = UserGradeSerializer(user_grade)

        user_data['grade'] = user_grade_serializer.data
        result.set('user', user_data)

        return Response(result.get_response(), result.get_code())

    def put(self, request, open_id):
        request_data = request.data
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        logger_info.info(request_data)

        # Get access token
        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            user_instance = User.objects.get(access_token=access_token, open_id=open_id)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Update data
        try:
            user_serializer = UserSerializer(user_instance, data=request_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                logger_info.info(user_serializer.errors)
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
                return Response(result.get_response(), result.get_code())
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, e)
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class UserInfoDetail(APIView):

    def put(self, request, open_id):
        request_data = request.data
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            user_instance = User.objects.get(access_token=access_token, open_id=open_id)
            user_info = UserInfo.objects.get(user=user_instance)
            user_notify_info = UserNotifyInfo.objects.get(user=user_instance)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Update data
        try:
            user_notify_info.has_upcoming_order = True
            prev_count = user_notify_info.upcoming_order_count
            user_notify_info.upcoming_order_count = prev_count + 1
            user_notify_info.save()

            user_instance.has_upcoming_order = True
            user_instance.save()
        except Exception as e:
            logger_info.info(str(e))

        # Save data
        serializer = UserInfoSerializer(user_info, data=request_data, partial=True)

        if serializer.is_valid():
            serializer.save()
        else:
            logger_error.error(serializer.errors)
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class Password(APIView):

    def get(self, request, open_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # This open id is not open id
        mdn = open_id

        cn_header = False

        # Popup header check
        try:
            accept_lang = request.META['HTTP_ACCEPT_LANGUAGE']
            if 'zh' in accept_lang:
                cn_header = True
        except Exception as e:
            print(e)

        response = requests.get(urlmapper.get_url('USER_SMS_VERIFICATION') + open_id)
        if response.status_code != code.ARIES_200_SUCCESS:
            logger_info.info(response.text)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Verification info is not found')
            return Response(result.get_response(), result.get_code())

        try:
            user_login_info_count = UserLoginInfo.objects.filter(login_type=0, login_key=mdn).count()

            if user_login_info_count == 1:
                user_login_info = UserLoginInfo.objects.get(login_type=0, login_key=mdn)
                password = user_login_info.login_value
                masked_password = password[:3] + (len(password) - 3) * '*'
                result.set('password', masked_password)
                result.set('guide_message', 'Your password is ' + masked_password)
            else:
                user_count = User.objects.filter(mdn=mdn).count()

                if user_count >= 1:
                    result.set('password', get_msg(code.ERROR_1301_MDN_ALREADY_EXIST, cn_header))
                    result.set('guide_message', get_msg(code.ERROR_1301_MDN_ALREADY_EXIST, cn_header))
                else:
                    result.set('password', get_msg(code.ERROR_1302_MDN_INFO_NOT_FOUND, cn_header))
                    result.set('guide_message', get_msg(code.ERROR_1302_MDN_INFO_NOT_FOUND, cn_header))
            return Response(result.get_response(), result.get_code())
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Member info is not found')
            return Response(result.get_response(), result.get_code())

    def post(self, request, open_id):
        logger_info.info(request.data)

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            user = User.objects.get(open_id=open_id, access_token=access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        request_data = request.data
        login_key = request_data['login_key']
        login_value = request_data['login_value']

        try:
            count = UserLoginInfo.objects.filter(user=user, login_key=login_key, login_value=login_value).count()
            if count != 1:
                logger_error.error(code_msg.get_msg(code.ERROR_1014_INCORRECT_CURRENT_PASSWORD))
                result = ResultResponse.error_response(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                                       code_msg.get_msg(code.ERROR_1014_INCORRECT_CURRENT_PASSWORD),
                                                       code.ERROR_1014_INCORRECT_CURRENT_PASSWORD)
                return Response(result.get_response(), result.get_code())
            else:
                cache.set(login_key, 'password_find', 300)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        return Response(result.get_response(), result.get_code())

    def put(self, request, open_id):
        logger_info.info(request.data)

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            user = User.objects.get(open_id=open_id, access_token=access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        request_data = request.data
        login_key = request_data['login_key']
        login_value = request_data['login_value']

        try:
            cache_str = cache.get(login_key)
            if cache_str == 'password_find':
                login_info = UserLoginInfo.objects.get(user=user, login_key=login_key)
                login_info.login_value = login_value
                login_info.save()
                cache.delete(login_key)
            else:
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Login key data invalid')
                return Response(result.get_response(), result.get_code())
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, e)
            return Response(result.get_response(), result.get_code())

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        return Response(result.get_response(), result.get_code())


class UserValidation(APIView):

    def post(self, request):
        request_data = request.data
        logger_info.info(request_data)

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            access_token = request_data['access_token']
            open_id = request_data['open_id']
            user_qs = User.objects.filter(open_id=open_id, access_token=access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        try:
            user_count = user_qs.count()
            user = user_qs.get()
            user_grade = UserGrade.objects.get(user=user)

            user_serializer = UserSerializer(user)
            grade_serializer = UserGradeSerializer(user_grade)

            user_data = user_serializer.data
            user_data['grade'] = grade_serializer.data
            result.set('user', user_data)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        if user_count < 1:
            logger_info.info('Request_data_invalid')
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class UserInformationForPayment(APIView):

    def post(self, request):
        request_data = request.data
        logger_info.info(request_data)

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            open_id = request_data['open_id']
            user = User.objects.get(open_id=open_id)
            access_token = user.access_token
            result.set('access_token', access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class UserTemporaryDelete(APIView):

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            open_id = request.META.get('HTTP_OPEN_ID')
            user = User.objects.get(open_id=open_id)
            user.delete()
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())
