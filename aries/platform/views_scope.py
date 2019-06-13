from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.models import Result
from aries.common.result import ResultSerializer


class Scope(APIView):

    def post(self, request):
        print(request.data)

        request_data = request.data

        result = Result(code.ARIES_400_BAD_REQUEST, "Request data invalid", None)
        result_serializer = ResultSerializer(result)
        return Response(result_serializer.data, result.get_code())
