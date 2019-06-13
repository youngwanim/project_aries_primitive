import base64
import hashlib
import requests

from functools import partial
from django.core.files.storage import FileSystemStorage

from aries.common import oss

MEGA = 1048576
CDN_URL = [
    'http://viastelle-main.oss-cn-shanghai.aliyuncs.com/',
]
CDN_HOST = [
    'viastelle-main.oss-cn-shanghai.aliyuncs.com',
]

URL_MAIN = 0


class CdnManager:

    def __init__(self, request, folder_name, url_type=0):
        self.request = request
        self.oss_url = CDN_URL[url_type]
        self.oss_host = CDN_HOST[url_type]
        self.folder_name = folder_name
        self.origin_file_name = None
        self.upload_name = None
        self.uploaded_file_url = None
        self.upload_file_ext = None
        self.file_name = None
        self.file_size = None
        self.content_md5 = None
        self.fs = FileSystemStorage()

    def check_file_exists(self):

        if 'file' in self.request.FILES:
            file = self.request.FILES['file']
            self.origin_file_name = file.name
            self.file_name = self.fs.save(file.name, file)
            self.file_size = file.size
            return True
        else:
            return False

    def check_file_size(self):
        if self.file_size <= MEGA * 5:
            self.uploaded_file_url = self.fs.path(self.file_name)
            self.upload_file_ext = self.file_name.split('.')[-1]
            self.upload_name = self.folder_name + '/' + self.origin_file_name
            return True
        else:
            return False

    def get_content_md5(self):
        hash_value = hashlib.md5()
        try:
            with open(self.uploaded_file_url, 'rb') as md5_file:
                for buf in iter(partial(md5_file.read, 128), b''):
                    hash_value.update(buf)
            self.content_md5 = base64.b64encode(hash_value.digest()).decode('utf-8')
            return True
        except Exception as e:
            print(e)
            return False

    def upload_file(self):

        headers = {
            'Content-MD5': self.content_md5,
            'Content-Length': str(self.file_size),
            'Content-Type': 'image/' + self.upload_file_ext,
            'Host': self.oss_host,
            'Date': oss.get_gmt_date(),
            'Authorization': oss.get_oss_header(self.upload_name, 'PUT', self.content_md5,
                                                self.upload_file_ext, '/viastelle-main/')
        }
        with open(self.uploaded_file_url, 'rb') as upload_file:
            data = upload_file.read()
            response = requests.put(self.oss_url + self.upload_name, headers=headers, data=data)

        if response.status_code is 200:
            result = True
        else:
            result = False

        self.fs.delete(self.file_name)
        return result
