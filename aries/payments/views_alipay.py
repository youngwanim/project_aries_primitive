import json

import logging
import requests

from alipay import AliPay
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import resources
from aries.common import urlmapper
from aries.common.code_msg import get_msg
from aries.common.models import ResultResponse
from aries.payments.models import Payment, AlipayNotification, AlipayQueryTransaction, AlipayPaymentTransaction
from aries.payments.serializers import PaymentSerializer, AlipayPaymentSerializer, AlipayNotificationSerializer, \
    AlipayQuerySerializer
from aries.purchases.models import Order, PurchaseOrder

logger_info = logging.getLogger('payments_info')
logger_error = logging.getLogger('payments_error')


class Payments(APIView):
    PAYMENT_CREATED = 0
    ALIPAY_APP_PAYMENT = 0
    ALIPAY_MOBILE_PAYMENT = 2
    ALIPAY_NOTIFICATION_PAYMENT = 3

    def post(self, request):
        request_data = request.data

        if request_data.get('notification_order'):
            notification_order = request_data.get('notification_order')
        else:
            notification_order = False

        logger_info.info('Payment Initation : ' + str(request_data))
        try:
            order_id = request_data['order_id']
            payment_data = request_data['payment_raw_data']
            payment_type = request_data['payment_type']
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        if payment_type == 0:
            request_data['payment_raw_data'] = json.dumps(payment_data)
        elif payment_type == 2 or payment_type == 3:
            request_data['payment_raw_data'] = json.dumps(payment_data)

        logger_info.info('Raw_Data : ' + str(request_data['payment_raw_data']))

        # Check if the payment exists
        payment_count = Payment.objects.filter(order_id=order_id).count()

        if payment_count != 0:
            payment = Payment.objects.get(order_id=order_id)

            if payment.payment_status == 0 or payment.payment_status == 1:
                result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
                return Response(result.get_response(), result.get_code())

        # Set payment status
        request_data['payment_status'] = self.PAYMENT_CREATED
        payment_serializer = PaymentSerializer(data=request_data)

        if payment_serializer.is_valid():
            payment_serializer.save()
            payment = Payment.objects.get(order_id=order_id)
        else:
            print(payment_serializer.errors)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Set alipay client
        alipay_client = AliPay(
            debug=settings.DEBUG,
            appid=resources.get_alipay_app_id(),
            app_notify_url=urlmapper.get_url('ALIPAY_CALLBACK_URL'),
            app_private_key_path=resources.get_viastelle_pri_key(),
            alipay_public_key_path=resources.get_viastelle_pub_key(),
            sign_type='RSA2'
        )

        if payment_type == self.ALIPAY_APP_PAYMENT and not notification_order:
            # RSA signing check for sync
            alipay_app_result = payment_data['alipay_trade_app_pay_response']
            sign = payment_data['sign']
            content = json.loads(payment_data['content'])

            sign_result = alipay_client.verify(content, sign)
            response_code = int(alipay_app_result['code'])

            alipay_app_result['order_id'] = order_id
            alipay_app_result['alipay_trade_app_pay_response'] = content
            alipay_app_result['alipay_trade_app_pay_validation'] = sign_result

            serializer = AlipayPaymentSerializer(data=alipay_app_result)

            if serializer.is_valid():
                serializer.save()
            else:
                logger_info.info(serializer.errors)
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
                return Response(result.get_response(), result.get_code())

            # Check validation
            if response_code == 10000:
                payment.payment_status = 1
                payment.save()
            else:
                payment.payment_status = 4
                payment.save()
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        get_msg(code.ERROR_4004_PAYMENT_INTERFACE_FAILED))
                result.set_error(code.ERROR_4004_PAYMENT_INTERFACE_FAILED)
                return Response(result.get_response(), result.get_code())

        elif payment_type == self.ALIPAY_MOBILE_PAYMENT or notification_order:
            # Mobile payment
            logger_info.info('MOBILE_PAYMENT' + str(payment_data))

            # Query to alipay server
            query_response = alipay_client.api_alipay_trade_query(
                out_trade_no=order_id,
            )

            logger_info.info('-----------------')
            logger_info.info(str(query_response))

            payment_count = AlipayPaymentTransaction.objects.filter(out_trade_no=order_id).count()
            if payment_count <= 0:
                # Query response to AlipayPaymentSerializer
                logger_info.info(type(payment_data))
                alipay_payment = {
                    'alipay_trade_validation': False,
                    'code': query_response['code'],
                    'msg': query_response['msg'],
                    'app_id': payment_data['app_id'],
                    'charset': payment_data['charset'],
                    'out_trade_no': payment_data['out_trade_no'],
                    'seller_id': payment_data['seller_id'],
                    'timestamp': query_response['send_pay_date'],
                    'total_amount': payment_data['total_amount'],
                    'trade_no': payment_data['trade_no']
                }

                serializer = AlipayPaymentSerializer(data=alipay_payment)
                if serializer.is_valid():
                    serializer.save()
                else:
                    logger_info.info(serializer.errors)

            query_count = AlipayQueryTransaction.objects.filter(order_id=order_id).count()
            if query_count <= 0:
                serializer = AlipayQuerySerializer(data=query_response)
                query_response['order_id'] = order_id

                if serializer.is_valid():
                    serializer.save()
                else:
                    logger_info.info(serializer.errors)

            logger_info.info('Before code == 10000')

            if query_response['code'] == '10000':
                payment.payment_status = 1
                payment.save()
            else:
                payment.payment_status = 4
                payment.save()
                logger_error.error(code.ERROR_4004_PAYMENT_INTERFACE_FAILED)
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        get_msg(code.ERROR_4004_PAYMENT_INTERFACE_FAILED))
                result.set_error(code.ERROR_4004_PAYMENT_INTERFACE_FAILED)
                return Response(result.get_response(), result.get_code())

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        return Response(result.get_response(), result.get_code())


class AlipayNotificationHandler(APIView):
    PAYMENT_CREATED = 0
    ALIPAY_APP_PAYMENT = 0
    ALIPAY_MOBILE_PAYMENT = 2
    ALIPAY_NOTIFICATION_PAYMENT = 3

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Request data parsing
        try:
            request_data = request.data
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Set alipay client
        alipay_client = AliPay(
            debug=settings.DEBUG,
            appid=resources.get_alipay_app_id(),
            app_notify_url=urlmapper.get_url('ALIPAY_CALLBACK_URL'),
            app_private_key_path=resources.get_viastelle_pri_key(),
            alipay_public_key_path=resources.get_viastelle_pub_key(),
            sign_type='RSA2'
        )

        # Notification verification from ALIPAY
        noti_origin_data = json.dumps(request_data)
        noti_data = json.loads(noti_origin_data)

        sign = noti_data.pop('sign')
        sign_type = noti_data['sign_type']
        trade_status = noti_data['trade_status']

        verify_result = alipay_client.verify(noti_data, sign)
        logger_info.info('[notification_data]:' + noti_origin_data)
        logger_info.info(verify_result)

        if not verify_result:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                    get_msg(code.ERROR_4004_PAYMENT_INTERFACE_FAILED))
            result.set_error(code.ERROR_4004_PAYMENT_INTERFACE_FAILED)
            return Response(result.get_response(), result.get_code())

        # Check the order exists
        try:
            order_id = noti_data['out_trade_no']
            noti_data['order_id'] = order_id
            noti_data['sign'] = sign
            noti_data['sign_type'] = sign_type
            noti_data['alipay_notification_validation'] = verify_result

            order_count = Order.objects.filter(order_id=order_id).count()
            purchase_order_count = PurchaseOrder.objects.filter(order_id=order_id).count()

            if order_count == 0 and purchase_order_count == 1 and trade_status == 'TRADE_SUCCESS':
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
                    'payment_type': self.ALIPAY_MOBILE_PAYMENT,
                    'payment_data': noti_data,
                    'alipay_notification_order': True
                }

                response = requests.post(url, headers=headers, json=payload)
                logger_info.info(response.text)

            notification_count = AlipayNotification.objects.filter(
                order_id=order_id
            ).count()

            if notification_count == 0:
                serializer = AlipayNotificationSerializer(data=noti_data)
            else:
                notification_instance = AlipayNotification.objects.get(order_id=order_id)
                serializer = AlipayNotificationSerializer(notification_instance, data=noti_data, partial=True)

            if serializer.is_valid():
                serializer.save()
            else:
                logger_info.info(serializer.errors)
        except Exception as e:
            logger_info.info(str(e))

        return Response(result.get_response(), result.get_code())
