import json

import logging
import requests
import xmltodict
from rest_framework.response import Response
from rest_framework.views import APIView
from wechatpy import WeChatPay
from wechatpy.pay import utils

from aries.common import code
from aries.common import payment_util
from aries.common import urlmapper
from aries.common.code_msg import get_msg
from aries.common.models import ResultResponse
from aries.common.resources import get_wechat_query_url
from aries.payments.models import Payment
from aries.payments.serializers import PaymentSerializer, WechatQuerySerializer, WechatPaymentSerializer, \
    WechatNotificationSerializer
from aries.purchases.models import Order, PurchaseOrder

logger_info = logging.getLogger('payments_info')
logger_error = logging.getLogger('payments_error')


class WechatPayment(APIView):

    PAYMENT_CREATED = 0
    WECHAT_APP_PAYMENT = 1
    WECHAT_MOBILE_PAYMENT = 3

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)

        # Payment registration and validation check
        try:
            payment_type = request_data['payment_type']
            order_id = request_data['order_id']
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Check if the payment exists
        payment_count = Payment.objects.filter(order_id=order_id).count()

        if payment_count != 0:
            payment = Payment.objects.get(order_id=order_id)

            if payment.payment_status == 0 or payment.payment_status == 1:
                result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
                return Response(result.get_response(), result.get_code())

        # Get raw data for validation
        raw_data = {}

        # Wechat app payment
        request_data['payment_raw_data'] = json.dumps(raw_data)

        try:
            wechat_serializer = WechatPaymentSerializer(data=request_data)

            if wechat_serializer.is_valid():
                wechat_serializer.save()
            else:
                logger_info.info(wechat_serializer.errors)
        except Exception as e:
            print(e)
            logger_info.info(str(e))

        if payment_type == 1:
            wechat_app_id = 'viastelle'
            merchant_id = 'viastelle'
            api_key = 'viastelle'
            nonce_str = payment_util.wechat_payment_str(order_id)
        else:
            wechat_app_id = 'viastelle'
            merchant_id = 'viastelle'
            api_key = 'viastelle'
            nonce_str = payment_util.wechat_payment_str(order_id)

        wechat_client = WeChatPay(wechat_app_id, api_key, merchant_id,
                                  sub_mch_id=None, mch_cert=None, mch_key=None)

        try:
            query_data = {
                'appid': wechat_app_id,
                'mch_id': merchant_id,
                'out_trade_no': order_id,
                'nonce_str': nonce_str
            }

            prepaid_signature = utils.calculate_signature(query_data, api_key)
            query_data_signed = utils.dict_to_xml(query_data, prepaid_signature)

            url = get_wechat_query_url()
            headers = {'Content-Type': 'application/xml'}
            response = requests.post(url, headers=headers, data=query_data_signed)
            logger_info.info(response.text)

            response_data = response.content
            query_result = xmltodict.parse(response_data)['xml']
            query_result['order_id'] = order_id
            request_data['transaction_id'] = query_result['transaction_id']

            query_serializer = WechatQuerySerializer(data=query_result)

            if query_serializer.is_valid():
                query_serializer.save()
                query_data = query_serializer.data
            else:
                logger_info.info(query_serializer.errors)
                # Error case - refund request

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                    get_msg(code.ERROR_4005_PAYMENT_SYNC_ERROR))
            result.set_error(code.ERROR_4005_PAYMENT_SYNC_ERROR)
            return Response(result.get_response(), result.get_code())

        # Set payment status
        request_data['payment_status'] = self.PAYMENT_CREATED
        payment_serializer = PaymentSerializer(data=request_data)

        # Payment object save
        if payment_serializer.is_valid():
            payment_serializer.save()
            payment = Payment.objects.get(order_id=order_id)
        else:
            logger_info.info(payment_serializer.errors)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Verification payment
        if payment_type == self.WECHAT_APP_PAYMENT or payment_type == self.WECHAT_MOBILE_PAYMENT:
            if query_data['return_code'] == 'SUCCESS' and query_data['result_code'] == 'SUCCESS':
                # Payment success and check price
                # if query_data['total_fee'] == int(price_total):

                del query_result['order_id']

                if not wechat_client.check_signature(query_result):
                    payment.payment_status = 4
                else:
                    payment.payment_status = 1

                payment.save()
            else:
                payment.payment_status = 4
                payment.save()

                logger_error.error(code.ERROR_4001_PAYMENT_VALIDATION_FAILED)
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        get_msg(code.ERROR_4001_PAYMENT_VALIDATION_FAILED))
                result.set_error(code.ERROR_4001_PAYMENT_VALIDATION_FAILED)
                return Response(result.get_response(), result.get_code())
        else:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class WechatPayNotificationApp(APIView):

    def post(self, request):
        request_data = request.data
        logger_info.info(request_data)

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # XML data to dict
        try:
            notification_data = xmltodict.parse(request_data)['xml']
            logger_info.info(notification_data)
            order_id = notification_data['out_trade_no']
            order_count = Order.objects.filter(order_id=order_id).count()

            if order_count <= 0:
                # Order has not created
                purchase_order = PurchaseOrder.objects.get(order_id=order_id)
                open_id = purchase_order.open_id

                url = urlmapper.get_url('USER_PAYMENT_TOKEN')
                payload = {
                    'open_id': purchase_order.open_id
                }
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    response_json = response.json()
                    access_token = response_json['access_token']
                else:
                    return Response(result.get_response, result.get_code())

                url = urlmapper.get_url('ORDER')
                headers = {
                    'open-id': open_id,
                    'authorization': 'bearer ' + access_token
                }
                payload = {
                    'order_id': order_id,
                    'payment_type': 1,
                    'payment_data': request_data
                }

                response = requests.post(url, headers=headers, json=payload)
                logger_info.info(response.text)

                notification_data['order_id'] = order_id
                noti_serializer = WechatNotificationSerializer(data=notification_data)
            else:
                # Order has created
                order = Order.objects.get(order_id=order_id)

                notification_data['order_id'] = order_id
                noti_serializer = WechatNotificationSerializer(order, data=notification_data, partial=True)

            if noti_serializer.is_valid():
                noti_serializer.save()
            else:
                logger_error.error(noti_serializer.errors)

        except Exception as e:
            logger_info.info(str(e))

        return Response(result.get_response(), result.get_code())
