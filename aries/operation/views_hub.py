import json

from channels import Group
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.models import ResultResponse
from aries.common.utils import push_sender


class HubMessageSender(APIView):

    def post(self, request):
        print(request.data)

        request_data = request.data
        payload = {
            'code': 200,
            'message': 'success',
            'type': request_data['type'],
            'order': request_data['order']
        }
        payload = {'text': json.dumps(payload)}

        Group('operation').send(payload)

        custom = {
            'visibility': 'public',
            'target': request_data['type'],
            'extra': request_data['order_id']
        }

        ret = push_sender.sendPushToAdmin(request_data['title'], request_data['order_id'], custom)
        print(ret)
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())
