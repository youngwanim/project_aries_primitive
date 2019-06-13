import json

from channels import Group
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.models import ResultResponse


class OrderNotification(APIView):

    def post(self, request):
        print(request.data)

        order_data = {
                "order_id": "S20170627AAAAAAAA",
                "order_status": 0,
                "order_status_history": "[]",
                "operation_status": 0,
                "operation_status_history": "[]",
                "user_name": "1BE3",
                "user_telephone": "01024351244",
                "shipping_method": 0,
                "shipping_status": 0,
                "shipping_rider_id": "",
                "shipping_rider_telephone": ""
        }

        result_json = {
            'delivery_index': 34,
            'order': order_data
        }

        order_noty = {
            'type': 'notification',
            'request_id': 'ABCD',
            'domain': 'order_list',
            'code': 200,
            'message': 'success',
            'result': result_json
        }

        payload = {'text': json.dumps(order_noty)}

        Group('operation').send(payload)
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())


class OperationNofitication(APIView):

    def post(self, request):
        print(request.data)

        payload = {'text': json.dumps(request.data)}
        Group('operation').send(payload)
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())

