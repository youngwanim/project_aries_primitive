import binascii
import os

import logging
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common.code_msg import get_msg
from aries.platform.models import AuthToken
from aries.platform.serializers import AuthTokenSerializer
from aries.common import code
from aries.common.models import ResultResponse
from aries.users.models import User


logger_info = logging.getLogger('platform_info')
logger_error = logging.getLogger('platform_error')


class Token(APIView):

    scope = 'end_user'

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)

        try:
            user_open_id = request_data['user_open_id']
        except KeyError as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # create platform & platform check
        while True:
            auth_token = binascii.hexlify(os.urandom(24)).decode()
            token_count = AuthToken.objects.filter(access_token=auth_token).count()

            if token_count == 0:
                break

        auth_token = auth_token.upper()

        # complete auth_token data
        request_data['access_token'] = auth_token
        request_data['scope'] = self.scope

        prev_token_count = AuthToken.objects.filter(user_open_id=user_open_id).count()

        if prev_token_count == 1:
            prev_token = AuthToken.objects.get(user_open_id=user_open_id)
            prev_token.access_token = auth_token
            prev_token.scope = self.scope
            prev_token.save()
            result.set('token', auth_token)
        else:
            token_serializer = AuthTokenSerializer(data=request_data)

            if token_serializer.is_valid():
                token_serializer.save()
                result.set('token', auth_token)
            else:
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
                return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())

    def put(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)

        try:
            user_open_id = request_data['user_open_id']
            user_account = request_data['user_account']
            new_user_account = request_data['new_user_account']

            auth_token = AuthToken.objects.get(user_open_id=user_open_id, user_account=user_account)
            auth_token.user_account = new_user_account
            auth_token.save()

            return Response(result.get_response(), result.get_code())

        except Exception as e:
            logger_info.info(str(e))
            return Response(result.get_response(), result.get_code())

    def delete(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)

        try:
            user_open_id = request_data['user_open_id']
            user_account = request_data['user_account']

            auth_token = AuthToken.objects.get(user_open_id=user_open_id, user_account=user_account)

            user = User.objects.get(open_id=user_open_id, access_token=auth_token.access_token)
            user.access_token = ''
            user.save()

            auth_token.delete()
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class TokenDetail(APIView):

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            user_open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
        except KeyError as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Get access token with open id
        try:
            auth_token = AuthToken.objects.get(access_token=access_token, user_open_id=user_open_id)

            if auth_token.access_token_state != 0:
                logger_error.error('token_expired')
                result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token is expired')
                return Response(result.get_response(), result.get_code())

        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token is not found')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data

        logger_info.info(request_data)

        try:
            access_token = request_data['access_token']
            access_token = access_token.split(' ')[1]
            scope = request_data['scope']

            token_count = AuthToken.objects.filter(access_token=access_token, scope=scope).count()

            if token_count <= 0:
                result = ResultResponse(code.ARIES_401_UNAUTHORIZED, get_msg(code.ARIES_401_UNAUTHORIZED))
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')

        return Response(result.get_response(), result.get_code())


class TokenDetailForAdmin(APIView):

    scope = 'operator'

    def post(self, request):
        request_data = request.data
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        logger_info.info(request_data)

        try:
            user_open_id = request_data['operator_id']
        except KeyError as e:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # create platform & platform check
        while True:
            auth_token = binascii.hexlify(os.urandom(24)).decode()
            token_count = AuthToken.objects.filter(access_token=auth_token).count()

            if token_count == 0:
                break

        auth_token = auth_token.upper()

        # complete auth_token data
        request_data['access_token'] = auth_token
        request_data['scope'] = self.scope

        prev_token_count = AuthToken.objects.filter(user_open_id=user_open_id).count()

        if prev_token_count == 1:
            prev_token = AuthToken.objects.get(user_open_id=user_open_id)
            prev_token.access_token = auth_token
            prev_token.scope = self.scope
            prev_token.save()
            result.set('token', auth_token)
        else:
            token_serializer = AuthTokenSerializer(data=request_data)

            if token_serializer.is_valid():
                token_serializer.save()
                result.set('token', auth_token)
            else:
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
                return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())
