from functools import partial

from django.core.files.storage import FileSystemStorage

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code_msg
from aries.common import oss
from aries.common import code
from aries.common import urlmapper
from aries.common.code_msg import get_msg
from aries.common.models import ResultResponse

import base64
import requests
import hashlib
import uuid


class CdnFile(APIView):

    MEGA = 1048576

    def post(self, request, folder_name):
        print(request.META)
        print(request.FILES)

        result = ResultResponse(code.ARIES_200_SUCCESS, 'Upload success')

        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Token or open id invalid')
            return Response(result.get_response(), result.get_code())

        if 'file' in request.FILES:

            # File object create
            file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)

            # File size check
            file_size = file.size

            if file_size >= self.MEGA*5:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, get_msg(code.ERROR_1102_FILE_OVERSIZE))
                result.set_error(code.ERROR_1102_FILE_OVERSIZE)
                return Response(result.get_response(), result.get_code())

            # File name information processing
            uploaded_file_url = fs.path(filename)
            upload_filename = self.make_file_name(filename)
            upload_file_ext = filename.split('.')[-1]

            upload_name = folder_name + '/' + upload_filename
            print(upload_name)

            # Check file format to png or jpg
            if upload_file_ext.lower() != 'png' and upload_file_ext.lower() != 'jpg'\
                    and upload_file_ext.lower() != 'jpeg':
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        code_msg.get_msg(code.ERROR_1011_ACCESS_TOKEN_GET_FAIL))
                result.set_error(code.ERROR_1101_NOT_SUPPORTED_FILE_FORMAT)
                print('Error')
                fs.delete(filename)
                return Response(result.get_response(), result.get_code())

            url = 'http://viastelle-user-storage.oss-cn-shanghai.aliyuncs.com/' + upload_name
            host = 'viastelle-user-storage.oss-cn-shanghai.aliyuncs.com'

            hash_value = hashlib.md5()
            with open(uploaded_file_url, 'rb') as mdfile:
                for buf in iter(partial(mdfile.read, 128), b''):
                    hash_value.update(buf)

            content_md5 = base64.b64encode(hash_value.digest()).decode('utf-8')

            headers = {
                'Content-MD5': content_md5,
                'Content-Length': str(file_size),
                'Content-Type': 'image/' + upload_file_ext,
                'Host': host,
                'Date': oss.get_gmt_date(),
                'Authorization': oss.get_oss_header(upload_filename, 'PUT', content_md5,
                                                    upload_file_ext, '/viastelle-user-storage/' + folder_name + '/')
            }

            with open(uploaded_file_url, 'rb') as upload_file:
                data = upload_file.read()
                response = requests.put(url, headers=headers, data=data)

            if response.status_code is 200:
                result.set('file_name', upload_name)

                # Check profile image
                if folder_name.lower() == 'profile':
                    url = urlmapper.get_url('USER_INFO') + '/' + open_id + '/detail'
                    headers = {'AUTHORIZATION': 'bearer ' + access_token,
                               'OPEN-ID': open_id}
                    payload = {'profile_image': upload_name}
                    user_response = requests.put(url, headers=headers, json=payload)
                    print(user_response.text)
            else:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, "File upload fail")
            fs.delete(filename)
        else:
            print('no file!!')
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, "File upload fail")

        return Response(result.get_response(), result.get_code())

    def delete(self, request):
        print(request.data)

    def make_file_name(self, filename):
        random_str = str(uuid.uuid4()).replace('-', '')[:6]
        return filename.split('.')[0] + '-' + random_str + '.' + filename.split('.')[-1]

    def get_file_category(self, filename):
        print(filename)

