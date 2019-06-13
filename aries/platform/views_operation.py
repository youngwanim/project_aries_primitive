import binascii
import json
import os

import logging
import requests
from django.core.cache import cache
from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code, code_msg
from aries.common import urlmapper
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.common.utils import promotion_util
from aries.platform.common.operation_func import get_time_bomb_info_from_menu
from aries.platform.models import OperationStatus, AuthToken, Operator, HubOperationStatus, OperationPopup
from aries.platform.serializers import AuthTokenSerializer, PopupSerializer


logger_info = logging.getLogger('platform_info')
logger_error = logging.getLogger('platform_error')


class Operation(APIView):
    ANDROID = 0
    IOS = 1
    ETC = 2

    def get(self, request, os_name):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        current_status = 0
        operation_status = 0
        device_os = self.ETC

        language_info = header_parser.parse_language_v2(request.META)
        cn_header = language_info.cn_header
        accept_lang = language_info.accept_lang
        os_type = language_info.os_type

        try:
            operation_status = OperationStatus.objects.latest('id')
            current_status = operation_status.status

            # User-agent latest version
            if request.META.get('HTTP_USER_AGENT'):
                user_agent = request.META['HTTP_USER_AGENT']
                logger_info.info(user_agent)

            if os_name == "android":
                device_os = self.ANDROID
            elif os_name == "ios":
                device_os = self.IOS
            else:
                device_os = self.ETC

        except Exception as e:
            logger_info.info(str(e))

        # Get popup information
        try:
            popup = OperationPopup.objects.latest('id')
            serializer = PopupSerializer(popup)
            popup_data = serializer.data

            if cn_header:
                popup_data['main_image'] = popup_data['main_image_cn']
                popup_data['main_title'] = popup_data['main_title_cn']
                popup_data['button_text'] = popup_data['button_text_cn']
                popup_data['share_image'] = popup_data['share_image_cn']
                popup_data['content'] = popup_data['content_cn']

            del popup_data['main_image_cn']
            del popup_data['main_title_cn']
            del popup_data['button_text_cn']
            del popup_data['content_cn']

            if popup_data['target_type'] == 4:
                product_id = promotion_util.parse_promotion_extra(popup_data['target_detail'])
                popup_data['target_detail'] = product_id

            # Time bomb information
            time_bomb_info = get_time_bomb_info_from_menu(1, accept_lang, os_type)
            promotion_time_bomb = 102

            if time_bomb_info is not None:
                if time_bomb_info['status'] == 1 or time_bomb_info['status'] == 2:
                    popup_data['main_image'] = time_bomb_info['popup_image']
                    popup_data['share_image'] = time_bomb_info['popup_image']
                    popup_data['target_type'] = promotion_time_bomb
                    popup_data['target_detail'] = str(time_bomb_info['id'])

            result.set('popup', popup_data)
        except Exception as e:
            logger_info.info(str(e))
            result.set('popup', '')

        # Get geometric information
        try:
            if cache.get('hub_list'):
                result.set('hub_list', cache.get('hub_list'))
            else:
                response = requests.get(urlmapper.get_url('PRODUCT_HUBS'))

                if response.status_code == code.ARIES_200_SUCCESS:
                    response_json = response.json()
                    result.set('hub_list', response_json['hub_list'])
                    cache.set('hub_list', response_json['hub_list'], 3600)
                else:
                    result.set('hub_list', [])
        except Exception as e:
            logger_info.info(str(e))
            result.set('hub_list', [])

        if current_status != 0:
            # Maintain phase
            message = json.loads(operation_status.current_status_comment)

            if cn_header:
                comment = message['comment_cn']
            else:
                comment = message['comment_en']

            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, comment)

            if current_status == 1:
                result.set_error(code.ERROR_9990_PERIOD_MAINTENANCE)
            else:
                result.set_error(code.ERROR_9991_EMERGENCY_MAINTENANCE)

            return Response(result.get_response(), result.get_code())
        else:
            # Operating normal
            result.set('force_update', operation_status.force_update)

            if device_os is self.ANDROID:
                # Version guide
                result.set('android_min_version_code', operation_status.android_min_version_code)
                result.set('android_latest_version_code', operation_status.android_latest_version_code)
                result.set('android_latest_version_name', operation_status.android_latest_version_name)
                # Old version case
                result.set('min_version_code', operation_status.android_min_version_code)
                result.set('latest_version_code', operation_status.android_latest_version_code)
                result.set('latest_version_name', operation_status.android_latest_version_name)
            elif device_os is self.IOS:
                result.set('ios_min_version_code', operation_status.ios_min_version_code)
                result.set('ios_latest_version_code', operation_status.ios_latest_version_code)
                result.set('ios_latest_version_name', operation_status.ios_latest_version_name)
            else:
                result.set('version', operation_status.application_version)
                result.set('version_name', operation_status.application_version_name)

            return Response(result.get_response(), result.get_code())

    def post(self, request):
        print(request.data)
        request_data = request.data

        try:
            operation_status = OperationStatus.objects.latest('id')
            current_status = operation_status.current_status
            version = request_data['version']
            os_type = request_data['os_type']
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            return Response(result.get_response(), result.get_code())

        if current_status != 0:
            # Maintain phase
            result = ResultResponse(code.ARIES_503_SERVICE_NOT_AVAILABLE,
                                    operation_status.current_status_comment)

            if current_status == 1:
                result.set_error(code.ERROR_9990_PERIOD_MAINTENANCE)
            else:
                result.set_error(code.ERROR_9991_EMERGENCY_MAINTENANCE)

            return Response(result.get_response(), result.get_code())
        else:
            # Normal phase
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('os_type', os_type)

            if os_type == 0:
                latest_version = float(operation_status.current_android_version)
            elif os_type == 1:
                latest_version = operation_status.current_ios_version
            else:
                latest_version = operation_status.current_android_version

            if version < latest_version:
                result.set('need_update', True)
                if operation_status.force_update:
                    result.set('force_update', True)
                else:
                    result.set('force_update', False)
            else:
                result.set('need_update', False)
                result.set('force_update', False)

            result.set('latest_version', latest_version)

            return Response(result.get_response(), result.get_code())


class OperationV2(APIView):

    ANDROID = 0
    IOS = 1

    def get(self, request, hub_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        current_status = 0
        operation_status = 0

        language_info = header_parser.parse_language_v2(request.META)
        cn_header = language_info.cn_header
        accept_lang = language_info.accept_lang
        os_type = language_info.os_type

        try:
            operation_status = OperationStatus.objects.latest('id')
            current_status = operation_status.status

            # User-agent latest version
            if request.META.get('HTTP_USER_AGENT'):
                user_agent = request.META['HTTP_USER_AGENT']
                logger_info.info(user_agent)

        except Exception as e:
            logger_info.info(str(e))

        # Get popup information
        try:
            popup = OperationPopup.objects.latest('id')
            serializer = PopupSerializer(popup)
            popup_data = serializer.data

            if cn_header:
                popup_data['main_image'] = popup_data['main_image_cn']
                popup_data['main_title'] = popup_data['main_title_cn']
                popup_data['button_text'] = popup_data['button_text_cn']
                popup_data['share_image'] = popup_data['share_image_cn']
                popup_data['content'] = popup_data['content_cn']

            del popup_data['main_image_cn']
            del popup_data['main_title_cn']
            del popup_data['button_text_cn']
            del popup_data['content_cn']

            if popup_data['target_type'] == 4:
                product_id = promotion_util.parse_promotion_extra(popup_data['target_detail'])
                popup_data['target_detail'] = product_id

            # Time bomb information
            time_bomb_info = get_time_bomb_info_from_menu(hub_id, accept_lang, os_type)

            if time_bomb_info is not None:
                if time_bomb_info['status'] == 1 or time_bomb_info['status'] == 2:
                    popup_data['main_image'] = time_bomb_info['popup_image']
                    popup_data['share_image'] = time_bomb_info['popup_image']
                    popup_data['target_type'] = 102
                    popup_data['target_detail'] = str(time_bomb_info['id'])

            result.set('popup', popup_data)
        except Exception as e:
            logger_info.info(str(e))
            result.set('popup', '')

        # Get geometric information
        try:
            if cache.get('hub_list'):
                result.set('hub_list', cache.get('hub_list'))
            else:
                response = requests.get(urlmapper.get_url('PRODUCT_HUBS'))

                if response.status_code == code.ARIES_200_SUCCESS:
                    response_json = response.json()
                    result.set('hub_list', response_json['hub_list'])
                    cache.set('hub_list', response_json['hub_list'], 3600)
                else:
                    result.set('hub_list', [])
        except Exception as e:
            logger_info.info(str(e))
            result.set('hub_list', [])

        if current_status != 0:
            # Maintain phase
            message = json.loads(operation_status.current_status_comment)

            if cn_header:
                comment = message['comment_cn']
            else:
                comment = message['comment_en']

            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, comment)

            if current_status == 1:
                result.set_error(code.ERROR_9990_PERIOD_MAINTENANCE)
            else:
                result.set_error(code.ERROR_9991_EMERGENCY_MAINTENANCE)

            return Response(result.get_response(), result.get_code())
        else:
            # Operating normal
            result.set('force_update', operation_status.force_update)

            if os_type is self.ANDROID:
                # Version guide
                result.set('android_min_version_code', operation_status.android_min_version_code)
                result.set('android_latest_version_code', operation_status.android_latest_version_code)
                result.set('android_latest_version_name', operation_status.android_latest_version_name)
                # Old version case
                result.set('min_version_code', operation_status.android_min_version_code)
                result.set('latest_version_code', operation_status.android_latest_version_code)
                result.set('latest_version_name', operation_status.android_latest_version_name)
            elif os_type is self.IOS:
                result.set('ios_min_version_code', operation_status.ios_min_version_code)
                result.set('ios_latest_version_code', operation_status.ios_latest_version_code)
                result.set('ios_latest_version_name', operation_status.ios_latest_version_name)
            else:
                result.set('version', operation_status.application_version)
                result.set('version_name', operation_status.application_version_name)

            return Response(result.get_response(), result.get_code())


class OperationSign(APIView):

    def post(self, request):
        request_data = request.data
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        print(request_data)

        try:
            user_open_id = request_data['account']
            password = request_data['password']

            # sha_client = hashlib.sha512()
            # sha_client.update(bytes(password.encode('utf-8')))
            # password = sha_client.hexdigest()
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Operation check
        try:
            operation_status = HubOperationStatus.objects.latest('id')

            if operation_status.status == 1:
                result = ResultResponse(code.ARIES_503_SERVICE_NOT_AVAILABLE,
                                        operation_status.current_status_comment)
                return Response(result.get_response(), result.get_code())
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Check account
        try:
            operator = Operator.objects.get(account=user_open_id, password=password)
            scope = operator.scope
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                    code_msg.get_msg(code.ERROR_1006_ID_OR_PASSWORD_INVALID))
            result.set_error(code.ERROR_1006_ID_OR_PASSWORD_INVALID)
            return Response(result.get_response(), result.get_code())

        # create platform & platform check
        while True:
            auth_token = binascii.hexlify(os.urandom(24)).decode()
            token_count = AuthToken.objects.filter(access_token=auth_token).count()

            if token_count == 0:
                break

        auth_token = auth_token.upper()

        # Create today time
        current_time = str(datetime.now())
        result.set('server_time', current_time)
        result.set('name', operator.name)
        result.set('hub_id', operator.hub_id)

        # complete auth_token data
        request_data['user_open_id'] = user_open_id
        request_data['user_account'] = user_open_id
        request_data['access_token'] = auth_token
        request_data['scope'] = scope

        prev_token_count = AuthToken.objects.filter(user_open_id=user_open_id).count()

        if prev_token_count == 1:
            prev_token = AuthToken.objects.get(user_open_id=user_open_id)
            prev_token.access_token = auth_token
            prev_token.scope = scope
            prev_token.save()
            result.set('token', auth_token)
        else:
            token_serializer = AuthTokenSerializer(data=request_data)

            if token_serializer.is_valid():
                token_serializer.save()
                result.set('token', auth_token)
            else:
                print(token_serializer.errors)
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
                return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class OperationVerification(APIView):

    def post(self, request):
        try:
            request_data = request.data
            access_token = request_data['access_token']
            auth_token = AuthToken.objects.get(access_token=access_token)
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        try:
            scope = auth_token.scope

            if 'admin' in scope:
                result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            else:
                result = ResultResponse(code.ARIES_401_UNAUTHORIZED, ' Token or user not found')
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())
