import hashlib
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.models import ResultResponse
from aries.platform.models import Operator
from aries.platform.serializers import AccountSerializer


logger_info = logging.getLogger('platform_info')
logger_error = logging.getLogger('platform_error')


class AdminOperator(APIView):

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
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Get account list
        try:
            account_list = list()

            accounts = Operator.objects.all()
            account_count = accounts.count()

            paginator = Paginator(accounts, limit)
            account_objects = paginator.page(page).object_list
            serializer = AccountSerializer(account_objects, many=True)
            account_data = serializer.data

            for account in account_data:
                del account['password']
                account_list.append(account)

            result.set('total_count', account_count)
            result.set('accounts', account_list)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        # Response object
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            request_data = request.data
            logger_info.info(open_id + ':' + access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Add account
        try:
            sha_client = hashlib.sha512()
            sha_client.update(bytes(request_data['password'].encode('utf-8')))
            password = sha_client.hexdigest()
            request_data['password'] = password

            serializer = AccountSerializer(data=request_data)

            if serializer.is_valid():
                serializer.save()
            else:
                logger_info.info(serializer.errors)
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data not valid')
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')

        return Response(result.get_response(), result.get_code())


class AdminOperatorDetail(APIView):

    def get(self, request, operator_id):
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

        # Get account object
        try:
            account = Operator.objects.get(id=operator_id)
            serializer = AccountSerializer(account)

            account_data = serializer.data
            del account_data['password']

            result.set('account', account_data)
        except ObjectDoesNotExist:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Object not found')
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')

        return Response(result.get_response(), result.get_code())

    def put(self, request, operator_id):
        # Response object
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            logger_info.info(open_id + ':' + access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Change account information
        try:
            password = request_data['password']
            if len(password) >= 1:
                sha_client = hashlib.sha512()
                sha_client.update(bytes(password.encode('utf-8')))
                request_data['password'] = sha_client.hexdigest()

            account = Operator.objects.get(id=operator_id)
            serializer = AccountSerializer(account, data=request_data, partial=True)

            if serializer.is_valid():
                serializer.save()
            else:
                logger_info.info(serializer.errors)
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data not valid')
        except ObjectDoesNotExist:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Object not found')
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')

        return Response(result.get_response(), result.get_code())

    def delete(self, request, operator_id):
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

        # Delete account
        try:
            account = Operator.objects.get(id=operator_id)
            account.delete()
        except ObjectDoesNotExist:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Account not found')
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')

        return Response(result.get_response(), result.get_code())
