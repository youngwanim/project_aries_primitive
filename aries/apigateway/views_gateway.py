import json

import logging
import requests

from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.models import ResultResponse


logger = logging.getLogger('gateway')


class DomainMapper(object):

    API_REQUEST_HOST_DEVELOPMENT = {
        'cdn': 'http://139.196.123.42:8080',
        'delivery': 'http://139.196.123.42:8080',
        'operation': 'http://139.196.123.42:8080',
        'payments': 'http://139.196.123.42:8080',
        'platform': 'http://139.196.123.42:8080',
        'products': 'http://139.196.123.42:8080',
        'purchases': 'http://139.196.123.42:8080',
        'push': 'http://139.196.123.42:8080',
        'ucc': 'http://139.196.123.42:8080',
        'users': 'http://139.196.123.42:8080',
    }

    API_REQUEST_HOST_STAGING = {
        'cdn': 'http://192.168.1.214',
        'delivery': 'http://192.168.1.214',
        'operation': 'http://192.168.1.214',
        'payments': 'http://192.168.1.214',
        'platform': 'http://192.168.1.214',
        'products': 'http://192.168.1.214',
        'purchases': 'http://192.168.1.214',
        'push': 'http://192.168.1.214',
        'ucc': 'http://192.168.1.214',
        'users': 'http://192.168.1.214',
    }

    API_REQUEST_HOST_RELEASE = {
        # Operation is not defined
        'operation': 'http://139.196.123.42:8080',
        'platform': 'http://192.168.1.103:80',
        'cdn': 'http://192.168.1.104:80',
        'ucc': 'http://192.168.1.104:80',
        'users': 'http://192.168.1.104:80',
        'products': 'http://192.168.1.113:80',
        'delivery': 'http://192.168.1.113:80',
        'payments': 'http://192.168.1.106:80',
        'purchases': 'http://192.168.1.106:80',
    }

    API_URLS = [API_REQUEST_HOST_DEVELOPMENT, API_REQUEST_HOST_STAGING, API_REQUEST_HOST_RELEASE]

    SERVER_DEVELOPMENT = 0
    SERVER_STAGING = 1
    SERVER_RELEASE = 2

    def __init__(self):
        if settings.DEBUG and not settings.STAGE:
            server_type = self.SERVER_DEVELOPMENT
        elif not settings.DEBUG and settings.STAGE:
            server_type = self.SERVER_STAGING
        else:
            server_type = self.SERVER_RELEASE

        self.mapper = self.API_URLS[server_type]

    def get_mapper(self):
        return self.mapper


class GatewayDetail(APIView):

    mapper = DomainMapper().get_mapper()

    def operation(self, request):

        path = request.path_info.split('/')
        print(path)
        for item in path:
            if len(item) <= 0:
                path.remove(item)

        domain = path[0]

        # Domain mapper
        if self.mapper.get(domain):
            domain_url = self.mapper.get(domain)
            if request.path_info == '/products':
                url = domain_url + request.path_info + '/'
            else:
                url = domain_url + request.path_info
        else:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'BAD REQUEST')
            return Response(result.get_response(), result.get_code())

        headers = {
            'authorization': request.META.get('HTTP_AUTHORIZATION'),
            'open-id': request.META.get('HTTP_OPEN_ID'),
            'content-type': request.content_type,
            'accept-language': request.META.get('HTTP_ACCEPT_LANGUAGE'),
            'hub-id': request.META.get('HTTP_HUB_ID'),
            'os-type': request.META.get('HTTP_OS_TYPE')
        }

        # Request section added
        method = request.method.lower()
        method_map = {
            'get': requests.get,
            'post': requests.post,
            'put': requests.put,
            'delete': requests.delete
        }

        for k, v in request.FILES.items():
            request.data.pop(k)

        # Query string parser
        if method == 'get':
            query_str = {}
            for query_key in request.GET:
                query_str[query_key] = request.GET[query_key]

            if len(query_str) >= 1:
                index = 0
                url += '?'

                for query_key in query_str.keys():
                    url = url + query_key + '=' + query_str[query_key]
                    if index < len(query_str)-1:
                        url += '&'
                    index += 1

        # Content type parse
        if request.content_type and 'application/json' in request.content_type.lower():
            data = json.dumps(request.data)
            headers['content-type'] = request.content_type
            response = method_map[method](url, headers=headers, data=data)
        elif 'file' in request.FILES:
            file = request.FILES['file']
            files = {'file': file}
            del headers['content-type']
            response = method_map[method](url, headers=headers, files=files)
        else:
            data = request.data
            response = method_map[method](url, headers=headers, data=data)

        if response.headers.get('Content-Type', '').lower() == 'application/json':
            data = response.json()
        else:
            data = response.content

        logger.info(request.META.get('REMOTE_ADDR') + ' ' + str(response.status_code) +
                    ' ' + request.path_info)

        return Response(data=data, status=response.status_code)

    def get(self, request):
        return self.operation(request)

    def post(self, request):
        return self.operation(request)

    def put(self, request):
        return self.operation(request)

    def patch(self, request):
        return self.operation(request)

    def delete(self, request):
        return self.operation(request)
