import json
import logging

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import F
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import urlmapper
from aries.common.models import ResultResponse
from aries.users.manager.address_manager_v2 import AddressManagerV2
from aries.users.manager.user_manager import UserManager
from aries.users.models import User, UserNotifyInfo, UserNews, UserInfo, UserAddressInfo
from aries.users.serializers import UserSerializer, UserInfoSerializer, UserAddressInformationSerializer

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class UserSearchListV2(APIView):

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            logger_info.info(access_token)
            user_manager = UserManager()
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        try:
            user_list = user_manager.get_user_list(request)
            result.set('total_count', len(user_list))
            result.set('search_items', user_list)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Bad request')

        return Response(result.get_response(), result.get_code())


class Customer(APIView):

    def get(self, request):
        # Response object
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            page = int(request.GET.get('page'))
            limit = int(request.GET.get('limit'))
            logger_info.info(open_id + ':' + access_token)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Get user list
        try:
            user_list = list()

            users = User.objects.all()
            user_count = users.count()

            paginator = Paginator(users, limit)
            user_objects = paginator.page(page).object_list
            serializer = UserSerializer(user_objects, many=True)
            user_data = serializer.data

            for user in user_data:
                user['connection_account'] = json.loads(user['connection_account'])
                user_list.append(user)

            result.set('total_count', user_count)
            result.set('accounts', user_list)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')

        return Response(result.get_response(), result.get_code())


class CustomerDetail(APIView):

    def get(self, request, user_id):
        # Response object
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            logger_info.info(open_id + ':' + access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Get User object
        try:
            # User data
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)

            user_data = serializer.data
            user_data['connection_account'] = json.loads(user_data['connection_account'])

            user_open_id = user.open_id

            addresses = UserAddressInfo.objects.filter(user=user)
            serializer = UserAddressInformationSerializer(addresses, many=True)
            address_data = serializer.data
            address_list = list()

            for address in address_data:
                address_list.append(address)

            headers = {'open-id': user_open_id}
            response = requests.get(urlmapper.get_url('COUPON_LIST'), headers=headers)

            if response.status_code == code.ARIES_200_SUCCESS:
                response_json = response.json()
                coupons = response_json['coupons']
            else:
                coupons = []

            result.set('user', user_data)
            result.set('addresses', address_list)
            result.set('coupons', coupons)
        except ObjectDoesNotExist:
            logger_info.info('User not found')
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'User not found')
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')

        return Response(result.get_response(), result.get_code())


class CustomerSearch(APIView):

    def get(self, request):
        # Response object
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            key = request.GET.get('key')
            value = request.GET.get('value')
            page = int(request.GET.get('page'))
            limit = int(request.GET.get('limit'))
            logger_info.info(open_id + ':' + access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Execute query
        try:
            query_str = {key: value}

            user_list = list()

            users = User.objects.filter(**query_str)
            user_count = users.count()

            paginator = Paginator(users, limit)
            user_objects = paginator.page(page).object_list
            serializer = UserSerializer(user_objects, many=True)
            user_data = serializer.data

            for user in user_data:
                user['connection_account'] = json.loads(user['connection_account'])
                user_list.append(user)

            result.set('total_count', user_count)
            result.set('accounts', user_list)

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Bad request')

        return Response(result.get_response(), result.get_code())


class UserNewsDetail(APIView):

    def post(self, request):
        request_data = request.data
        logger_info.info(request_data)

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Operation check
        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]

            url = urlmapper.get_url('ADMIN_VALIDATE')
            payload = {'access_token': access_token}
            response = requests.post(url, json=payload)

            if response.status_code != code.ARIES_200_SUCCESS:
                result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
                return Response(result.get_response(), result.get_code())

        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        try:
            open_id = request_data['open_id']
            news_type = request_data['type']
            title = request_data['title']
            title_cn = request_data['title_cn']
            content = request_data['content']
            content_cn = request_data['content_cn']
            detail = request_data['detail']
            detail_cn = request_data['detail_cn']

            user = User.objects.get(open_id=open_id)

            UserNews.objects.create(
                user=user,
                type=news_type,
                title=title,
                title_cn=title_cn,
                content=content,
                content_cn=content_cn,
                has_read=False,
                detail=detail,
                detail_cn=detail_cn
            )

            user_notify_info = UserNotifyInfo.objects.get(user=user)
            user_notify_info.has_news = True
            user_notify_info.news_count = F('news_count') + 1
            user_notify_info.save()
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class UserInformationDetail(APIView):

    def post(self, request):
        request_data = request.data
        logger_info.info(request_data)

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Operation check
        try:
            access_token = request_data['access_token']

            url = urlmapper.get_url('ADMIN_VALIDATE')
            payload = {'access_token': access_token}
            response = requests.post(url, json=payload)

            if response.status_code != code.ARIES_200_SUCCESS:
                result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
                return Response(result.get_response(), result.get_code())

        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())

        try:
            open_id = request_data['open_id']
            address_id = request_data['address_id']

            user = User.objects.get(open_id=open_id)
            serializer = UserSerializer(user)
            user_data = serializer.data

            user_info = UserInfo.objects.get(user=user)
            serializer = UserInfoSerializer(user_info)
            user_info_data = serializer.data

            address_manager = AddressManagerV2(logger_info, logger_error)
            user_address = address_manager.get_address(open_id, address_id)

            if user_address is None:
                user_address = ''

            result.set('user', user_data)
            result.set('user_info', user_info_data)
            result.set('user_address', user_address)

            return Response(result.get_response(), result.get_code())
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())
