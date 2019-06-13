from rest_framework.response import Response
from rest_framework.views import APIView

from aries.cdn.manager.cdn_manager import CdnManager
from aries.common import code
from aries.common.code_msg import get_msg
from aries.common.http_utils import api_request_util
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse


class CdnFile(APIView):

    def post(self, request, folder_name):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'Upload success')
        authentication = header_parser.parse_authentication(request)

        if authentication[1] is None:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, get_msg(code.ARIES_401_UNAUTHORIZED))
            return Response(result.get_response(), result.get_code())

        if not api_request_util.get_user_information(authentication[0], authentication[1]):
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, get_msg(code.ARIES_401_UNAUTHORIZED))
            return Response(result.get_response(), result.get_code())

        cdn_manager = CdnManager(request, folder_name=folder_name)

        if not cdn_manager.check_file_exists():
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, "File doesn't exists")
            return Response(result.get_response(), result.get_code())

        if not cdn_manager.check_file_size():
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, get_msg(code.ERROR_1102_FILE_OVERSIZE))
            result.set_error(code.ERROR_1102_FILE_OVERSIZE)
            return Response(result.get_response(), result.get_code())

        if not cdn_manager.get_content_md5():
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, "Get content md5 error")
            return Response(result.get_response(), result.get_code())

        if not cdn_manager.upload_file():
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, "File upload failed")
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())

    def delete(self, request):
        print(request.data)
