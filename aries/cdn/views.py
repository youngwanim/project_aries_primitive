from functools import partial

from django.core.files.storage import FileSystemStorage

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import oss
from aries.common import code
from aries.common.models import Result
from aries.common.result import ResultSerializer

import base64
import requests
import hashlib
import uuid


class CdnFile(APIView):
    UPLOAD_DIR = '/static/cdn'

    def post(self, request):

        result = Result(code.ARIES_4_REQUEST_DATA_INVALID, "File upload fail", None)

        if 'file' in request.FILES:

            # File object create
            file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)

            # File name information processing
            uploaded_file_url = fs.path(filename)
            upload_filename = self.make_file_name(filename)
            upload_file_ext = filename.split('.')[-1]

            print(upload_filename)

            url = 'http://viastelle-main.oss-cn-shanghai.aliyuncs.com/' + upload_filename
            host = 'viastelle-main.oss-cn-shanghai.aliyuncs.com'

            hash_value = hashlib.md5()
            with open(uploaded_file_url, 'rb') as mdfile:
                for buf in iter(partial(mdfile.read, 128), b''):
                    hash_value.update(buf)

            content_md5 = base64.b64encode(hash_value.digest()).decode('utf-8')
            print(content_md5)

            headers = {
                'Content-MD5': content_md5,
                'Content-Length': str(file.size),
                'Content-Type': 'image/' + upload_file_ext,
                'Host': host,
                'Date': oss.get_gmt_date(),
                'Authorization': oss.get_oss_header(upload_filename, 'PUT', content_md5,
                                                    upload_file_ext, '/viastelle-main/')
            }
            print(headers)

            with open(uploaded_file_url, 'rb') as upload_file:
                data = upload_file.read()
                response = requests.put(url, headers=headers, data=data)

            if response.status_code is 200:
                response_dict = dict()
                response_dict['url'] = url
                result = Result(code.ARIES_0_SUCCESS, "File upload success", response_dict)
            else:
                result = Result(code.ARIES_5_API_CONNECT_FAIL, "File upload fail", None)
            fs.delete(filename)
        else:
            print('no file!!')

        result_serializer = ResultSerializer(result)
        return Response(result_serializer.data, status=status.HTTP_200_OK)

    def make_file_name(self, filename):
        random_str = str(uuid.uuid4()).replace('-', '')[:6]
        return filename.split('.')[0] + '-' + random_str + '.' + filename.split('.')[-1]

    def delete(self, request):
        print(request.data)

