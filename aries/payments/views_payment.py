import os

import logging
import requests
import xmltodict
from alipay import AliPay
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import payment_util
from aries.common import resources
from aries.common.code_msg import get_msg
from aries.common.models import ResultResponse
from aries.common.resources import get_wechat_refund_url
from aries.payments.models import Payment, AlipayPaymentTransaction, WechatQueryTransaction
from aries.payments.serializers import AlipayRefundSerializer, WechatRefundSerializer


logger_info = logging.getLogger('payments_info')
logger_error = logging.getLogger('payments_error')


class PaymentDetail(APIView):

    def delete(self, request, order_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)

        # Request data parsing
        try:
            open_id = request.META['HTTP_OPEN_ID']
            payment = Payment.objects.get(open_id=open_id, order_id=order_id)
        except Exception as e:
            logger_error.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        payment_type = payment.payment_type

        # Refund business logic
        if payment_type == 0 or payment_type == 2:
            alipay_transaction = AlipayPaymentTransaction.objects.get(out_trade_no=order_id)

            # Check debug state value
            if settings.STAGE or settings.DEBUG:
                debug = True
            else:
                debug = False

            alipay = AliPay(
                appid=resources.get_alipay_app_id(),
                app_notify_url=resources.get_alipay_notify_url(),
                app_private_key_path=resources.get_viastelle_pri_key(),
                alipay_public_key_path=resources.get_viastelle_pub_key(),
                sign_type='RSA2',
                debug=debug
            )

            refund_result = alipay.api_alipay_trade_refund(
                out_trade_no=alipay_transaction.out_trade_no,
                trade_no=alipay_transaction.trade_no,
                refund_amount=alipay_transaction.total_amount,
                refund_reason='Customer asked'
            )

            if refund_result['code'] == '10000':
                refund_status = 0
                payment_status = 5
            else:
                refund_status = 1
                payment_status = 6

            try:
                logger_info.info(refund_result)

                refund_result['order_id'] = order_id
                refund_result['status'] = refund_status
                refund_result['alipay_refund_validation'] = True

                serializer = AlipayRefundSerializer(data=refund_result)
                if serializer.is_valid():
                    serializer.save()
                else:
                    logger_info.info(serializer.errors)

                payment.payment_status = payment_status
                payment.save()

            except Exception as e:
                logger_info.error(str(e))
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        get_msg(code.ERROR_4002_PAYMENT_IS_NOT_FOUND))
                result.set_error(code.ERROR_4002_PAYMENT_IS_NOT_FOUND)
                return Response(result.get_response(), result.get_code())

        elif payment_type == 1 or payment_type == 3:
            if payment_type == 1:
                wechat_app_id = 'viastelle'
                merchant_id = 'viastelle'
            else:
                wechat_app_id = 'viastelle'
                merchant_id = 'viastelle'

            transaction = WechatQueryTransaction.objects.get(order_id=order_id)
            total_fee = transaction.total_fee

            refund_data = {
                'appid': wechat_app_id,
                'mch_id': merchant_id,
                'nonce_str': payment_util.wechat_payment_str(transaction.order_id),
                'transaction_id': transaction.transaction_id,
                'out_trade_no': order_id,
                'out_refund_no': transaction.transaction_id,
                'total_fee': total_fee,
                'refund_fee': total_fee
            }

            if payment_type == 1:
                refund_data_xml = payment_util.get_payment_wechat_dict_to_xml(refund_data)
            else:
                refund_data_xml = payment_util.get_payment_wechat_public_dict_to_xml(refund_data)

            logger_info.info(refund_data_xml)

            # refund_data_signed = utils.calculate_signature(prepaid_object, api_key)
            # prepaid_data = utils.dict_to_xml(prepaid_object, prepaid_signature)

            api_cert_dir = '/home/nexttf/workspace/project_aries/config/keys'

            if payment_type == 1:
                api_cert = 'app_pay_apiclient_cert.pem'
                api_key = 'app_pay_apiclient_key.pem'
            else:
                api_cert = 'public_pay_apiclient_cert.pem'
                api_key = 'public_pay_apiclient_key.pem'

            api_cert_file = os.path.join(api_cert_dir, api_cert)
            api_key_file = os.path.join(api_cert_dir, api_key)

            """
            verify=True, cert=(self.cert_file, self.key_file))
            """

            headers = {'Content-Type': 'application/xml'}
            response = requests.post(
                url=get_wechat_refund_url(),
                headers=headers,
                data=refund_data_xml,
                verify=True,
                cert=(api_cert_file, api_key_file)
            )
            logger_info.info(response.text)

            try:
                refund_result = xmltodict.parse(response.text)['xml']
                logger_info.info(refund_result)

                if refund_result['return_code'] == 'SUCCESS':
                    refund_status = 0
                    payment_status = 5
                else:
                    refund_status = 1
                    payment_status = 6

                validation = payment_util.get_payment_wechat_sign_validation(refund_result)

                refund_result['status'] = refund_status
                refund_result['order_id'] = order_id
                refund_result['wechat_refund_validation'] = validation

                serializer = WechatRefundSerializer(data=refund_result)

                if serializer.is_valid():
                    serializer.save()
                else:
                    logger_info.info(serializer.errors)

                payment.payment_status = payment_status
                payment.save()

                if refund_status == 1:
                    logger_error.error(code.ERROR_4003_PAYMENT_REFUND_FAIL)
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            get_msg(code.ERROR_4003_PAYMENT_REFUND_FAIL))
                    result.set_error(code.ERROR_4003_PAYMENT_REFUND_FAIL)
                    return Response(result.get_response(), result.get_code())
            except Exception as e:
                logger_error.error(str(e))
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        get_msg(code.ERROR_4002_PAYMENT_IS_NOT_FOUND))
                result.set_error(code.ERROR_4002_PAYMENT_IS_NOT_FOUND)
                return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())
