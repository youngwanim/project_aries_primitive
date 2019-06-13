import json
import logging
import requests

from datetime import date, datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import dateformatter
from aries.common import hub_data
from aries.common import payment_util
from aries.common import product_util
from aries.common import resources
from aries.common import urlmapper
from aries.common.code_msg import get_msg
from aries.common.http_utils import api_request_util

from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.purchases.manager.order_manager import OrderManager
from aries.purchases.manager.order_manager_v2 import OrderManagerV2
from aries.purchases.models import PurchaseOrder, Order, CustomerCoupon, EventOrderHistory
from aries.purchases.serializers import OrderSerializer, UpcomingOrderSerializer, UpcomingPurchaseOrderSerializer, \
    PurchaseOrderSerializer
from aries.purchases.service.event_order_service import EventOrderService

logger_info = logging.getLogger('purchases_info')
logger_error = logging.getLogger('purchases_error')


class Orders(APIView):
    PURCHASE_ORDER_STATUS_CREATED = 0
    ORDER_STATUS_CREATED = 0

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data

        logger_info.info(request_data)

        language_info = header_parser.parse_language(request.META)
        cn_header = language_info[0]

        order_data = dict()
        coupon_instance_list = list()

        # for getting daily order index
        order_manager_v2 = OrderManagerV2(logger_info, logger_error)

        # Step 1. Request data parsing
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            order_id = request_data['order_id']
            payment_data = request_data['payment_data']
            notification_order = request_data.get('alipay_notification_order', False)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid(Token or Open id)')
            return Response(result.get_response(), result.get_code())

        # Step 1.5
        order_count = Order.objects.filter(order_id=order_id, open_id=open_id).count()

        if order_count == 1:
            order = Order.objects.get(order_id=order_id, open_id=open_id)
            purchase_order = PurchaseOrder.objects.get(order_id=order_id, open_id=open_id)
            purchase_order_serializer = UpcomingPurchaseOrderSerializer(purchase_order)
            purchase_order_data = purchase_order_serializer.data
            purchase_order_data['order_details'] = json.loads(purchase_order_data['order_details'])
            purchase_order_data['shipping_detail'] = json.loads(purchase_order_data['shipping_detail'])
            del purchase_order_data['product_list']
            del purchase_order_data['coupon_list']
            del purchase_order_data['order_hash']

            order_data = UpcomingOrderSerializer(order).data
            order_data['order_start_date'] = dateformatter.get_ordering_complete_date_fmt(order.order_start_date)
            order_data['order_status_history'] = json.loads(order_data['order_status_history'])
            order_data['purchase_order'] = purchase_order_data
            order_data['order_cancel_date'] = ''

            # Get Timetable
            order_data['timetable'] = json.loads('[]')

            result.set('upcoming_order', order_data)
            return Response(result.get_response(), result.get_code())

        # Step 2. Check payment data validation and coupon check
        try:
            purchase_order = PurchaseOrder.objects.get(order_id=order_id, open_id=open_id,
                                                       status=self.PURCHASE_ORDER_STATUS_CREATED)

            order_data['purchase_order'] = purchase_order.id

            payment_type = purchase_order.payment_type

            # Check payment data validation
            payload = {'open_id': open_id, 'order_id': order_id, 'payment_type': payment_type,
                       'payment_raw_data': payment_data, 'price_unit': purchase_order.price_unit,
                       'price_total': purchase_order.price_total}

            if notification_order:
                payload['notification_order'] = True
            else:
                payload['notification_order'] = False

            payment_url = payment_util.get_payment_app_url(purchase_order.payment_type)
            response = requests.post(payment_url, json=payload)
            logger_info.info(response.text)
            payment_result = response.json()

            if response.status_code != code.ARIES_200_SUCCESS:
                if response.status_code == code.ARIES_400_BAD_REQUEST:
                    result = ResultResponse(code.ARIES_400_BAD_REQUEST,
                                            get_msg(code.ERROR_9000_INTERNAL_API_CALL_FAILED, cn_header))
                elif payment_result['error_code'] == code.ERROR_4001_PAYMENT_VALIDATION_FAILED:
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            get_msg(code.ERROR_4001_PAYMENT_VALIDATION_FAILED, cn_header))
                    result.set_error(code.ERROR_4001_PAYMENT_VALIDATION_FAILED)
                elif payment_result['error_code'] == code.ERROR_4005_PAYMENT_SYNC_ERROR:
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            get_msg(code.ERROR_4005_PAYMENT_SYNC_ERROR, cn_header))
                purchase_order.status = 3
                purchase_order.save()
                return Response(result.get_response(), result.get_code())

            logger_info.info('Payment finished')

            # Order saved and coupon using section
            coupon_list = json.loads(purchase_order.coupon_list)
            logger_info.info(coupon_list)

            for coupon in coupon_list:
                coupon_id = coupon['coupon_id']
                coupon_count = CustomerCoupon.objects.filter(id=coupon_id).count()

                if coupon_count == 1:
                    coupon_instance = CustomerCoupon.objects.get(id=coupon_id)
                    coupon_instance.status = 1
                    coupon_instance.used_date = datetime.now()
                    coupon_instance_list.append(coupon_instance)
                else:
                    logger_error.error(get_msg(code.ERROR_4001_PAYMENT_VALIDATION_FAILED))
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            get_msg(code.ERROR_4001_PAYMENT_VALIDATION_FAILED))
                    result.set_error(code.ERROR_4001_PAYMENT_VALIDATION_FAILED)
                    purchase_order.status = 3
                    purchase_order.save()
                    return Response(result.get_response(), result.get_code())

        except Exception as e:
            logger_error.error(str(e))
            error_code = code.ERROR_3002_PURCHASE_ORDER_NOT_FOUND
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, get_msg(error_code), cn_header)
            result.set_error(error_code)
            return Response(result.get_response(), result.get_code())

        # Step 3 Order data section
        logger_info.info('Order data section')

        # Order data
        order_data['open_id'] = open_id
        order_data['hub_id'] = purchase_order.hub_id
        order_data['order_id'] = order_id
        order_data['order_status'] = self.ORDER_STATUS_CREATED
        history_date = dateformatter.get_yyyymmdd_now()
        history_payload = [{'status': 0, 'datetime': history_date}]
        order_data['order_status_history'] = json.dumps(history_payload)
        order_data['order_daily_index'] = order_manager_v2.get_daily_order_index()

        # Delivery data
        is_on_site_pickup = purchase_order.delivery_on_site
        address_id = purchase_order.delivery_address_id

        # Check if it was on-site pickup or not
        if is_on_site_pickup:
            logger_info.info('On site pickup')
            hub_name = hub_data.get_hub_name(cn_header, purchase_order.hub_id)
            complete_address = hub_name + '\n - ' + hub_data.get_hub_address(cn_header, purchase_order.hub_id)
            order_data['delivery_on_site'] = purchase_order.delivery_on_site
            order_data['delivery_address'] = complete_address
        else:
            logger_info.info('NOT on site pickup')
            try:
                headers = {'open-id': str(open_id), 'authorization': 'bearer ' + access_token,
                           'Content-Type': 'application/json'}
                response = requests.get(urlmapper.get_url('PRODUCT_ADDRESS_DETAIL') + '/' + str(address_id),
                                        headers=headers)
            except Exception as e:
                logger_info.info(str(e))

            if response.status_code == code.ARIES_200_SUCCESS:
                response_json = response.json()['user_address']
                logger_info.info(response_json)

                # Set delivery address
                recipient_name = response_json['recipient_name']
                recipient_mdn = response_json['recipient_mdn']

                if len(recipient_mdn) <= 0 and len(recipient_name) <= 0:
                    delivery_address = response_json['name']
                else:
                    delivery_address = response_json['name'] + ' - ' + response_json['detail']

                if len(delivery_address) > 300:
                    delivery_address = delivery_address[:300]
                order_data['delivery_address'] = delivery_address
                order_data['delivery_address_lat'] = response_json['latitude']
                order_data['delivery_address_lng'] = response_json['longitude']
                order_data['delivery_recipient_name'] = recipient_name
                order_data['delivery_recipient_mdn'] = recipient_mdn
            else:
                # New address check
                logger_info.info('Address not found error')
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                        'Address not found')
                result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)
                return Response(result.get_response(), result.get_code())

        logger_info.info('After on site pickup')
        order_data['user_name'] = purchase_order.user_name
        order_data['user_telephone'] = purchase_order.user_telephone
        order_data['user_receipt'] = purchase_order.user_receipt
        order_data['delivery_date'] = purchase_order.delivery_date
        order_data['delivery_schedule'] = purchase_order.delivery_schedule
        order_data['delivery_as_fast'] = purchase_order.delivery_as_fast
        order_data['delivery_customer_name'] = purchase_order.user_name
        order_data['delivery_telephone_state'] = 0
        order_data['delivery_telephone'] = 'Delivery telephone'
        pre_time = purchase_order.delivery_start_time
        post_time = purchase_order.delivery_end_time
        delivery_date = str(purchase_order.delivery_date).replace('-', '.')
        order_data['delivery_time'] = delivery_date + ', ' + pre_time + '~' + post_time

        # Shipping data
        order_data['shipping_method'] = purchase_order.shipping_method
        order_data['shipping_status'] = 0

        # Step 4
        logger_info.info('STEP 4')
        order_count = Order.objects.filter(order_id=order_id, open_id=open_id).count()

        if order_count == 1:
            logger_info.info('Order exists')

            order = Order.objects.get(order_id=order_id, open_id=open_id)
            purchase_order = PurchaseOrder.objects.get(order_id=order_id, open_id=open_id)
            purchase_order_serializer = UpcomingPurchaseOrderSerializer(purchase_order)
            purchase_order_data = purchase_order_serializer.data
            purchase_order_data['order_details'] = json.loads(purchase_order_data['order_details'])
            purchase_order_data['shipping_detail'] = json.loads(purchase_order_data['shipping_detail'])
            del purchase_order_data['product_list']
            del purchase_order_data['coupon_list']
            del purchase_order_data['order_hash']

            order_data = UpcomingOrderSerializer(order).data
            order_data['order_start_date'] = dateformatter.get_ordering_complete_date_fmt(order.order_start_date)
            order_data['order_status_history'] = json.loads(order_data['order_status_history'])
            order_data['purchase_order'] = purchase_order_data
            order_data['order_cancel_date'] = ''

            # Get Timetable
            order_data['timetable'] = json.loads('[]')

            result.set('upcoming_order', order_data)
            return Response(result.get_response(), result.get_code())

        # Step 5
        # Create order object and send order data to client
        logger_info.info('Step 5')

        try:
            order_serializer = OrderSerializer(data=order_data)

            if order_serializer.is_valid():
                order_serializer.save()
                logger_info.info('Order valid and save success')

                # Order save success and coupon save
                for coupon_ins in coupon_instance_list:
                    coupon_ins.save()

                # User notification url call
                url = urlmapper.get_url('USER_NOTIFICATION') + '/coupon/1/' + str(len(coupon_instance_list))
                headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}
                requests.get(url, headers=headers)

                # Get special instruction and include cutlery information
                include_cutlery = purchase_order.include_cutlery
                special_inst = purchase_order.special_instruction

                # Special instruction and include cutlery save call
                url = urlmapper.get_url('USER_CART_INFO_SAVE')
                headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}
                json_data = {'include_cutlery': include_cutlery, 'special_instruction': special_inst}
                requests.put(url, headers=headers, json=json_data)

                # After user notification
                logger_info.info('After user notification request')
                purchase_order_serializer = UpcomingPurchaseOrderSerializer(purchase_order)
                purchase_order_data = purchase_order_serializer.data
                purchase_order_data['order_details'] = json.loads(purchase_order_data['order_details'])
                purchase_order_data['shipping_detail'] = json.loads(purchase_order_data['shipping_detail'])
                del purchase_order_data['product_list']
                del purchase_order_data['coupon_list']
                del purchase_order_data['order_hash']

                order_data = order_serializer.data
                order = Order.objects.get(id=order_data['id'])
                order_data = UpcomingOrderSerializer(order).data
                order_data['order_start_date'] = dateformatter.get_ordering_complete_date_fmt(order.order_start_date)
                order_data['order_status_history'] = json.loads(order_data['order_status_history'])
                order_data['purchase_order'] = purchase_order_data
                order_data['order_cancel_date'] = ''

                # Get Timetable
                logger_info.info('Get time table')
                order_data['timetable'] = json.loads('[]')

                result.set('upcoming_order', order_data)

                # Check on first purchase
                logger_info.info('Check first purchase')
                first_order_count = Order.objects.filter(open_id=open_id, order_status__lte=10).count()
                if first_order_count == 1:
                    hub_id = purchase_order.hub_id
                    event_order_service = EventOrderService(logger_info, logger_error)
                    event_order_service.create_event_order(0, hub_id, open_id, order_id)
            else:
                logger_error.error(order_serializer.errors)
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Internal server error')
                return Response(result.get_response(), result.get_code())

            purchase_order.status = 1
            purchase_order.save()
            logger_info.info('Purchase order save')

            # Product stock update
            product_list = json.loads(purchase_order.product_list)
            payload = {'trade_type': 0, 'product_list': product_list, 'validate_str': 'GoDbAcKeNdS'}
            url = urlmapper.get_url('PRODUCT_STOCK')
            response = requests.post(url, json=payload)
            logger_info.info(response.text)

            # Order complete
            headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}
            payload = {'order_id': order_id}
            url = urlmapper.get_url('OPERATION_ORDER_COMPLETE')
            response = requests.post(url, headers=headers, json=payload)
            logger_info.info(response.text)

        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Internal server error')
            return Response(result.get_response(), result.get_code())

        # Step 6
        # Save payment method and notify to admin server
        # Upcoming order notification added
        logger_info.info('Step 6')

        headers = {'AUTHORIZATION': request.META['HTTP_AUTHORIZATION']}
        payload = {'latest_payment_method': purchase_order.payment_type}
        url = urlmapper.get_url('USER_INFO') + '/' + open_id + '/info'
        response = requests.put(url, headers=headers, json=payload)
        logger_info.info(response.json())

        try:
            # Hub message
            logger_info.info('Hub message')

            order_manager = OrderManager(logger_info, logger_error)
            order_list_detail = order_manager.get_order_list(order_id)
            payload = {
                'code': 200, 'message': 'success', 'order': order_list_detail, 'type': 1,
                'order_id': order_id, 'title': 'Here comes a new order'
            }
            url = urlmapper.get_url('HUB_MESSAGE_ANDROID')
            response = requests.post(url, json=payload)
            logger_info.info(response.text)
        except Exception as e:
            logger_info.info(str(e))

        return Response(result.get_response(), result.get_code())


class OrdersDetail(APIView):
    ORDERS_DETAIL_PUT = 'orders_detail_put'
    ORDERS_DETAIL_STATUS_HISTORY = 'orders_detail_status_history'

    # Get detailed order information
    def get(self, request, order_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        lang_info = header_parser.parse_language_v2(request.META)
        accept_lang = lang_info.accept_lang
        os_type = lang_info.os_type

        # Check order_id length
        if len(order_id) < 17:
            logger_error.error(code.ERROR_9001_PARAMETER_VALIDATION_FAILED)
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                    get_msg(code.ERROR_9001_PARAMETER_VALIDATION_FAILED))
            result.set_error(code.ERROR_9001_PARAMETER_VALIDATION_FAILED)
            return Response(result.get_response(), result.get_code())

        # Request data parsing
        try:
            order = Order.objects.get(open_id=open_id, order_id=order_id)
            purchase_order = PurchaseOrder.objects.get(order_id=order.order_id)

            purchase_order_serializer = UpcomingPurchaseOrderSerializer(purchase_order)
            purchase_order_data = purchase_order_serializer.data
            purchase_order_data['order_details'] = json.loads(purchase_order_data['order_details'])
            purchase_order_data['shipping_detail'] = json.loads(purchase_order_data['shipping_detail'])
            del purchase_order_data['product_list']
            del purchase_order_data['coupon_list']
            del purchase_order_data['order_hash']

            if purchase_order_data['extra_telephone'] is None:
                purchase_order_data['extra_telephone'] = ''
            if purchase_order_data['special_instruction'] is None:
                purchase_order_data['special_instruction'] = ''

            order_serializer = UpcomingOrderSerializer(order)
            order_data = order_serializer.data
            order_data['purchase_order'] = purchase_order_data
            start_date = order.order_start_date.strftime(resources.DATE_WITH_AM_PM)
            order_data['order_start_date'] = dateformatter.get_yymmdd_time(start_date)
            del order_data['order_status_history']

            if order.order_status == 11:
                order_cancel_date = order.order_cancel_date
                if order_cancel_date is not None:
                    order_cancel_date = order.order_cancel_date.strftime(resources.DATE_WITH_AM_PM)
                    order_data['order_cancel_date'] = dateformatter.get_yymmdd_time(order_cancel_date)
                else:
                    order_data['order_cancel_date'] = ''
            else:
                order_data['order_cancel_date'] = ''

            result.add(order_data)

            product_list = json.loads(purchase_order.product_list)

            headers = {'accept-language': accept_lang}
            json_data = {
                'product_list': product_list,
                'open_id': open_id,
                'order_id': order_id,
                'hub_id': purchase_order_data['hub_id']
            }

            response = requests.post(urlmapper.get_url('MENU_VALIDATE'), headers=headers, json=json_data)
            response_json = response.json()

            result.set('reviews', response_json['reviews'])
            result.set('review_items', response_json['review_items'])
        except Exception as e:
            logger_info.info(str(e))
            print(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Get user default hub id
        user_information = api_request_util.get_user_information(open_id, access_token)
        hub_id = user_information[1]['user']['default_hub_id'] if user_information[0] else 1

        # Recommend product list
        product_list = api_request_util.get_recommend_products(accept_lang, hub_id, os_type)
        result.set('products', product_list)

        return Response(result.get_response(), result.get_code())

    # Order Information edit
    def put(self, request, order_id):
        logger_info.info(order_id)
        request_data = request.data

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Request data parsing
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Get purchase order instance
        try:
            order = Order.objects.get(open_id=open_id, order_id=order_id)
            purchase_order = PurchaseOrder.objects.get(open_id=open_id, order_id=order.order_id)
        except Exception as e:
            logger_error.error(str(e))
            error_code = code.ERROR_3002_PURCHASE_ORDER_NOT_FOUND
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, get_msg(error_code))
            result.set_error(error_code)
            return Response(result.get_response(), result.get_code())

        # Check order status to edit
        if order.order_status != 0:
            error_code = code.ERROR_3009_ORDER_EDIT_NOT_AVAILABLE
            logger_error.error(error_code)
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, get_msg(error_code))
            result.set_error(error_code)
            return Response(result.get_response(), result.get_code())

        # Applying changed items to purchase order information
        try:
            # Check delivery schedule
            original_schedule = purchase_order.delivery_schedule
            new_schedule = request_data['delivery_schedule']

            if original_schedule != request_data['delivery_schedule']:
                hub_id = purchase_order.hub_id
                delivery_date = str(purchase_order.delivery_date)[:10]
                method = purchase_order.shipping_method
                if purchase_order.delivery_on_site:
                    method = 1

                query_str = '/' + str(hub_id) + '/' + delivery_date + '/' + str(new_schedule) + '/' + str(method)
                url = urlmapper.get_url('TIMETABLE_LIST') + query_str

                response = requests.get(url)
                response_json = response.json()

                if response.status_code != code.ARIES_200_SUCCESS:
                    api_result = response.json()
                    result = ResultResponse(api_result['code'],
                                            api_result['message'])
                    result.set_error(api_result['error_code'])
                    return Response(result.get_response(), result.get_code())

                if response_json['availability']:
                    start_time = response_json['delivery_start_time']
                    end_time = response_json['delivery_end_time']
                    request_data['delivery_start_time'] = start_time
                    request_data['delivery_end_time'] = end_time

                    if start_time[1:2] == '0':
                        start_time_prefix = start_time[:2]
                        start_time_postfix = start_time[2:]
                    else:
                        start_time_prefix = start_time[:1]
                        start_time_postfix = start_time[1:]

                    if end_time[1:2] == '0':
                        end_time_prefix = end_time[:2]
                        end_time_postfix = end_time[2:]
                    else:
                        end_time_prefix = end_time[:1]
                        end_time_postfix = end_time[1:]

                    post_str = start_time_prefix + start_time_postfix + '-' + end_time_prefix + end_time_postfix
                    order.delivery_time = order.delivery_time[:12] + post_str
                    order.delivery_schedule = new_schedule
                    order.save()
                else:
                    error_code = code.ERROR_3007_DELIVERY_SCHEDULE_INVALID
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            get_msg(error_code))
                    result.set_error(error_code)
                    return Response(result.get_response(), result.get_code())

            # Check Address information
            old_address_id = purchase_order.delivery_address_id
            new_address_id = request_data['delivery_address_id']

            if old_address_id != new_address_id:
                # Check if hub_id was changed
                product_list = json.loads(purchase_order.product_list)
                payload = {'product_list': product_list, 'delivery_schedule': new_schedule}
                response = requests.post(urlmapper.get_url('PRODUCT_VALIDATION'), json=payload)

                if response.status_code == code.ARIES_200_SUCCESS:
                    response_json = response.json()
                else:
                    logger_error.error(response.text)
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            code.ERROR_9000_INTERNAL_API_CALL_FAILED)
                    result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)
                    return Response(result.get_response(), result.get_code())

                # Product validation check
                product_count = response_json['product_count']

                if product_count != len(product_list):
                    logger_error.error(code.ERROR_3010_DELIVERY_CHANGE_NOT_ALLOWED)
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            code.ERROR_3010_DELIVERY_CHANGE_NOT_ALLOWED)
                    result.set_error(code.ERROR_3010_DELIVERY_CHANGE_NOT_ALLOWED)
                    return Response(result.get_response(), result.get_code())

                # If product is valid, change product stock and more address change business logic
                # TBD

                headers = {'open-id': str(open_id), 'authorization': 'bearer ' + access_token}
                response = requests.get(urlmapper.get_url('PRODUCT_ADDRESS_DETAIL') + '/' +
                                        str(new_address_id), headers=headers)

                if response.status_code == code.ARIES_200_SUCCESS:
                    response_json = response.json()
                else:
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                            code.ERROR_9000_INTERNAL_API_CALL_FAILED)
                    result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)
                    return Response(result.get_response(), result.get_code())

                # Register address to database
                address = response_json['user_address']
                order.delivery_address = address['name'] + ' ' + address['detail']
                order.save()

                request_data['delivery_address_id'] = new_address_id

            order_serializer = PurchaseOrderSerializer(purchase_order, data=request_data, partial=True)

            if order_serializer.is_valid():
                order_serializer.save()

                purchase_order = PurchaseOrder.objects.get(id=order_serializer.data['id'])

                purchase_order_serializer = UpcomingPurchaseOrderSerializer(purchase_order)
                purchase_order_data = purchase_order_serializer.data
                purchase_order_data['order_details'] = json.loads(purchase_order_data['order_details'])
                purchase_order_data['shipping_detail'] = json.loads(purchase_order_data['shipping_detail'])
                del purchase_order_data['product_list']
                del purchase_order_data['coupon_list']
                del purchase_order_data['order_hash']

                order_serializer = UpcomingOrderSerializer(order)
                order_data = order_serializer.data
                order_start_date = datetime.strptime((str(order.order_start_date)[:-10]), '%Y-%m-%d %H:%M')
                order_data['order_start_date'] = order_start_date.strftime('%Y-%m-%d %I:%M %p')
                order_data['order_status_history'] = json.loads(order_data['order_status_history'])
                order_data['purchase_order'] = purchase_order_data
                order_data['order_cancel_date'] = ''

                # Get Timetable
                order_status = order_data['order_status']
                if order_status == 0:
                    hub_id = purchase_order.hub_id
                    sales_time = product_util.get_sales_time_to_str(purchase_order.sales_time)
                    response = requests.get(urlmapper.get_time_table_url(hub_id, sales_time))
                    response_json = response.json()
                    order_data['timetable'] = response_json['timetable']
                else:
                    order_data['timetable'] = json.loads('[]')

                result.set('upcoming_order', order_data)
            else:
                logger_info.info(order_serializer.errors)
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
                return Response(result.get_response(), result.get_code())

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())

    # Order cancel request
    def delete(self, request, order_id):
        # Request data parsing
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            logger_info.info(open_id + ':' + access_token + ':' + order_id)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Get purchase order instance
        try:
            order = Order.objects.get(open_id=open_id, order_id=order_id)
            purchase_order = PurchaseOrder.objects.get(open_id=open_id, order_id=order.order_id)
        except Exception as e:
            logger_error.error(str(e))
            error_code = code.ERROR_3002_PURCHASE_ORDER_NOT_FOUND
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, get_msg(error_code))
            result.set_error(error_code)
            return Response(result.get_response(), result.get_code())

        # Check order status to edit
        if order.order_status != 0:
            error_code = code.ERROR_3009_ORDER_EDIT_NOT_AVAILABLE
            logger_error.error(error_code)
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, get_msg(error_code))
            result.set_error(error_code)
            return Response(result.get_response(), result.get_code())

        # Refund payment
        header = {'open-id': open_id}
        url = urlmapper.get_url('PAYMENT') + '/' + order_id + '/detail'
        response = requests.delete(url, headers=header)

        order.order_status = 11
        order_history = json.loads(order.order_status_history)
        order_history.append(dateformatter.get_order_status_history(11))
        order.order_status_history = json.dumps(order_history)

        order.operation_status = 10
        order_operation_history = json.loads(order.operation_status_history)
        order_operation_history.append(dateformatter.get_order_status_history(10))
        order.operation_status_history = json.dumps(order_operation_history)

        # Add order cancel date
        order.order_cancel_date = datetime.today()
        order.save()

        if response.status_code != code.ARIES_200_SUCCESS:
            purchase_order.status = 6
            purchase_order.save()

            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR,
                                    get_msg(code.ERROR_4003_PAYMENT_REFUND_FAIL))
            result.set_error(code.ERROR_4003_PAYMENT_REFUND_FAIL)
            return Response(result.get_response(), result.get_code())
        else:
            # Refund success
            purchase_order.status = 5
            purchase_order.save()

            # Coupon restore
            coupon_list = json.loads(purchase_order.coupon_list)

            for coupon in coupon_list:
                coupon_id = coupon['coupon_id']
                coupon = CustomerCoupon.objects.get(id=coupon_id)
                current_date = date.today()

                if current_date <= coupon.end_date:
                    coupon.status = 0
                    coupon.used_date = current_date
                    coupon.save()
                    url = urlmapper.get_url('USER_NOTIFICATION') + '/coupon/0/1'
                    headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}
                    requests.get(url, headers=headers)
                else:
                    coupon.status = 2
                    coupon.used_date = current_date
                    coupon.save()

        # Product stock update
        product_list = json.loads(purchase_order.product_list)
        payload = {'trade_type': 1, 'product_list': product_list, 'validate_str': 'GoDbAcKeNdS'}
        url = urlmapper.get_url('PRODUCT_STOCK')
        response = requests.post(url, json=payload)
        logger_info.info(response.text)

        # Order canceled
        headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}
        payload = {'order_id': order_id}
        url = urlmapper.get_url('OPERATION_ORDER_CANCELED')
        response = requests.post(url, headers=headers, json=payload)
        logger_info.info(response.text)

        # First purchase canceled
        first_purchase_count = EventOrderHistory.objects.filter(open_id=open_id).count()
        if first_purchase_count == 1:
            first_purchase = EventOrderHistory.objects.get(open_id=open_id)
            first_purchase.event_target = False
            first_purchase.save()

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        return Response(result.get_response(), result.get_code())


class UpcomingOrders(APIView):

    DATE_WITH_AM_PM = '%Y-%m-%d %I:%M %p'

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        lang_info = header_parser.parse_language_v2(request.META)

        accept_lang = lang_info.accept_lang
        os_type = lang_info.os_type

        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authorization error')
            return Response(result.get_response(), result.get_code())

        try:
            # Get upcoming order list
            order_manager = OrderManager(logger_info, logger_error)
            order_list = order_manager.get_orders(order_manager.UPCOMING_ORDER, {
                'open_id': open_id,
                'order_status__lt': 3
            })
            result.set('upcoming_orders', order_list)

            # Get user default hub id
            user_information = api_request_util.get_user_information(open_id, access_token)
            hub_id = user_information[1]['user']['default_hub_id'] if user_information[0] else 1

            # Recommend product list
            product_list = api_request_util.get_recommend_products(accept_lang, hub_id, os_type)
            result.set('products', product_list)

            # Check upcoming order notification
            api_request_util.read_upcoming_order(open_id, access_token)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class PastOrders(APIView):
    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        lang_info = header_parser.parse_language_v2(request.META)

        accept_lang = lang_info.accept_lang
        os_type = lang_info.os_type

        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authorization error')
            return Response(result.get_response(), result.get_code())

        try:
            # Get past order list
            order_manager = OrderManager(logger_info, logger_error)
            order_list = order_manager.get_orders(order_manager.PAST_ORDER, {
                'open_id': open_id,
                'order_status__gt': 9
            })
            result.set('past_orders', order_list)

            # Get user default hub id
            user_information = api_request_util.get_user_information(open_id, access_token)
            hub_id = user_information[1]['user']['default_hub_id'] if user_information[0] else 1

            # Recommend product list
            product_list = api_request_util.get_recommend_products(accept_lang, hub_id, os_type)
            result.set('products', product_list)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())