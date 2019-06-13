import json
import logging
from datetime import datetime

from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import dateformatter
from aries.common import product_util
from aries.common.exceptions.exceptions import AuthInfoError
from aries.common.http_utils import api_request_util
from aries.common.models import ResultResponse
from aries.purchases.common.admin_func import get_user_address_data
from aries.purchases.manager.order_manager import OrderManager
from aries.purchases.models import Order
from aries.purchases.serializers import OrderListSerializer, OrderSerializer
from aries.purchases.service.dada_service import DadaService

logger_info = logging.getLogger('purchases_info')
logger_error = logging.getLogger('purchases_error')


class OrderOperation(APIView):

    def get(self, request):
        # Response object
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            api_request_util.get_admin_token_validate_v2(access_token)

            hub_id = 1
            delivery_schedule = int(request.GET.get('delivery_schedule'))
            delivery_date = request.GET.get('delivery_date')

            # Date information parsing
            # Format : '2017-04-06'
            target_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())
        except Exception as e:
            logger_error.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Bad request')
            return Response(result.get_response(), result.get_code())

        # Get order list
        try:
            order_list = list()
            preparing_list = list()

            if delivery_schedule <= 0:
                orders = Order.objects.filter(
                    hub_id=hub_id,
                    delivery_date=target_date
                ).order_by('-id')
            else:
                orders = Order.objects.filter(
                    hub_id=hub_id,
                    delivery_date=target_date,
                    delivery_schedule=delivery_schedule
                ).order_by('-id')

            serializer = OrderListSerializer(orders, many=True)
            order_data = serializer.data

            for order in order_data:
                order['order_status_history'] = json.loads(order['order_status_history'])
                order['operation_status_history'] = json.loads(order['operation_status_history'])
                order['delivery_schedule_time'] = product_util.get_delivery_schedule_str(order['delivery_schedule'])

                order_list.append(order)

                if 1 <= order['operation_status'] <= 4:
                    preparing_list.append(order)

            payload = {
                'orders': order_list,
                'preparing_orders': preparing_list
            }

            result.set('result', payload)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')

        return Response(result.get_response(), result.get_code())


class OrderOperationV2(APIView):

    def get(self, request, hub_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            api_request_util.get_admin_token_validate_v2(access_token)

            delivery_date = request.GET.get('delivery_date', None)
            start_date = request.GET.get('start_date', None)
            end_date = request.GET.get('end_date', None)
            delivery_year = request.GET.get('delivery_year', None)
            delivery_month = request.GET.get('delivery_month', None)
            delivery_schedule = request.GET.get('delivery_schedule', None)
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 100))

            date_information = (start_date, end_date, delivery_date, delivery_year, delivery_month)
            order_manager = OrderManager(logger_info, logger_error)
            order_list_result = order_manager.get_operation_orders(
                hub_id, date_information, delivery_schedule, page, limit
            )

            payload = order_manager.get_order_separation(order_list_result[0])

            result.set('result', payload)
            result.set('orders', payload['orders'])
            result.set('total_count', order_list_result[1])
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except Exception as e:
            logger_error.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')

        return Response(result.get_response(), result.get_code())


class OrderDetailOperation(APIView):

    def get(self, request, order_id):
        # Response object
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            api_request_util.get_admin_token_validate_v2(access_token)

            logger_info.info(access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
            return Response(result.get_response(), result.get_code())

        # Get order object
        try:
            order = Order.objects.get(order_id=order_id)
            serializer = OrderSerializer(order)

            order_data = serializer.data
            purchase_order = order.purchase_order

            order_data['order_status_history'] = json.loads(order_data['order_status_history'])
            order_data['operation_status_history'] = json.loads(order_data['operation_status_history'])
            order_data['order_details'] = json.loads(purchase_order.order_details)
            order_data['special_instruction'] = purchase_order.special_instruction
            order_data['extra_telephone'] = purchase_order.extra_telephone
            del order_data['purchase_order']

            result.set('result', order_data)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')

        return Response(result.get_response(), result.get_code())


class OrderDetailOperationV2(APIView):

    def get(self, request, order_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            api_request_util.get_admin_token_validate_v2(access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
            return Response(result.get_response(), result.get_code())

        try:
            order_manager = OrderManager(logger_info, logger_error)
            order_data = order_manager.get_order_detail(order_id)
            open_id = order_data['open_id']

            address_id = order_data['address_id']

            # Get user information
            user_data = api_request_util.get_user_info(open_id, access_token, address_id)

            if len(user_data['user_address']) >= 5:
                order_data['user_address'] = user_data['user_address']
            else:
                order_data['user_address'] = get_user_address_data(
                    order_data['delivery_recipient_name'],
                    order_data['delivery_address_lat'],
                    order_data['delivery_address_lng'],
                    order_data['delivery_address']
                )
            order_data['user'] = user_data['user']
            order_data['user_info'] = user_data['user_info']

            # Dada service
            dada_service = DadaService(logger_info, logger_error)
            order_data['shipping_order_detail'] = dada_service.read_dada_order_detail(order_id)

            result.set('order', order_data)
            result.set('result', order_data)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))

        return Response(result.get_response(), result.get_code())


class OrderPreparingOperation(APIView):

    def put(self, request, order_id):
        request_data = request.data
        logger_info.info(request_data)

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            api_request_util.get_admin_token_validate_v2(access_token)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
            return Response(result.get_response(), result.get_code())

        # Change order data
        try:
            order = Order.objects.get(order_id=order_id)

            """
            order.order_status = 11
            order_history = json.loads(order.order_status_history)
            order_history.append(self.get_order_status_history(11))
            order.order_status_history = json.dumps(order_history)

            order.operation_status = 10
            order_operation_history = json.loads(order.operation_status_history)
            order_operation_history.append(self.get_order_status_history(10))
            order.operation_status_history = json.dumps(order_operation_history)
            """

            # Do business logic to each status
            change_status = request_data['operation_status']
            if change_status == 1:
                logger_info.info('start packaging')
                if order.order_status == 0:
                    order_history = json.loads(order.order_status_history)
                    order_history.append(dateformatter.get_order_status_history(1))
                    request_data['order_status'] = 1
                    request_data['order_status_history'] = json.dumps(order_history)

                if order.operation_status == 0:
                    order_operation_history = json.loads(order.operation_status_history)
                    order_operation_history.append(dateformatter.get_order_status_history(1))
                    request_data['operation_status'] = 1
                    request_data['order_operation_history'] = json.dumps(order_operation_history)
            elif change_status == 2:
                logger_info.info('Packaging done')
                if order.operation_status == 1:
                    order_operation_history = json.loads(order.operation_status_history)
                    order_operation_history.append(dateformatter.get_order_status_history(2))
                    request_data['operation_status'] = 2
                    request_data['order_operation_history'] = json.dumps(order_operation_history)
            elif change_status == 5:
                logger_info.info('Delivery started')
                if order.order_status == 1:
                    order_history = json.loads(order.order_status_history)
                    order_history.append(dateformatter.get_order_status_history(2))
                    request_data['order_status'] = 2
                    request_data['order_status_history'] = json.dumps(order_history)

                if order.operation_status == 2:
                    order_operation_history = json.loads(order.operation_status_history)
                    order_operation_history.append(dateformatter.get_order_status_history(3))
                    request_data['operation_status'] = 5
                    request_data['order_operation_history'] = json.dumps(order_operation_history)
            elif change_status == 6:
                logger_info.info('Delivery completed')
                if order.order_status == 2:
                    order_history = json.loads(order.order_status_history)
                    order_history.append(dateformatter.get_order_status_history(10))
                    request_data['order_status'] = 10
                    request_data['order_status_history'] = json.dumps(order_history)

                if order.operation_status == 5:
                    order_operation_history = json.loads(order.operation_status_history)
                    order_operation_history.append(dateformatter.get_order_status_history(6))
                    request_data['operation_status'] = 6
                    request_data['order_operation_history'] = json.dumps(order_operation_history)

            serializer = OrderSerializer(order, data=request_data, partial=True)

            if serializer.is_valid():
                serializer.save()
                order_data = serializer.data
                result.set('result', order_data)

                purchase_order = order.purchase_order

                order_data['order_status_history'] = json.loads(order_data['order_status_history'])
                order_data['operation_status_history'] = json.loads(order_data['operation_status_history'])
                order_data['order_details'] = json.loads(purchase_order.order_details)
                order_data['special_instruction'] = purchase_order.special_instruction
                order_data['extra_telephone'] = purchase_order.extra_telephone

                # price information
                order_data['price_sub_total'] = purchase_order.price_sub_total
                order_data['price_delivery_fee'] = purchase_order.price_delivery_fee
                order_data['price_discount'] = purchase_order.price_discount
                order_data['price_total'] = purchase_order.price_total

                # Address information (Please check after purchase order model update)
                order_data['address_id'] = purchase_order.delivery_address_id

                del order_data['purchase_order']
                result.set('order', order_data)
            else:
                logger_info.info(serializer.errors)
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request_data invalid')

        return Response(result.get_response(), result.get_code())


class OrderSearchOperation(APIView):

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            api_request_util.get_admin_token_validate_v2(access_token)

            order_id = request.GET.get('order_id')
            name = request.GET.get('name')
            mdn = request.GET.get('mdn')
            open_id = request.GET.get('open_id')
            page = int(request.GET.get('page'))
            limit = int(request.GET.get('limit'))
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
            return Response(result.get_response(), result.get_code())

        # Execute query
        try:
            request_str = {'order_id__icontains': order_id,
                           'user_name__icontains': name,
                           'user_telephone__icontains': mdn,
                           'open_id__icontains': open_id}
            query_str = request_str.copy()
            for item in request_str.keys():
                if request_str[item] is None:
                    query_str.pop(item)

            logger_info.info(query_str)
            order_list = list()

            orders = Order.objects.filter(**query_str)
            order_count = orders.count()

            paginator = Paginator(orders, limit)
            order_objects = paginator.page(page).object_list
            serializer = OrderListSerializer(order_objects, many=True)
            order_data = serializer.data

            for order in order_data:
                order['order_status_history'] = json.loads(order['order_status_history'])
                order['operation_status_history'] = json.loads(order['operation_status_history'])
                order['order_start_date'] = order['order_start_date'][:19].replace('T', ' ')
                order['delivery_schedule_time'] = product_util.get_delivery_schedule_str(order['delivery_schedule'])

                order_list.append(order)

            result_json = {
                'total_count': order_count,
                'orders': order_list
            }

            result.set('result', result_json)

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Bad request')

        return Response(result.get_response(), result.get_code())


class OrderSearchV2(APIView):

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            api_request_util.get_admin_token_validate_v2(access_token)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
            return Response(result.get_response(), result.get_code())

        try:
            order_manager = OrderManager(logger_info, logger_error)

            order_list = order_manager.get_search_orders(request, False)
            result.set('result', {'orders': order_list, 'total_count': len(order_list)})
            result.set('orders', order_list)
            result.set('total_count', len(order_list))
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Bad request')

        return Response(result.get_response(), result.get_code())


class OrderSearchListV2(APIView):

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            api_request_util.get_admin_token_validate_v2(access_token)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        try:
            order_manager = OrderManager(logger_info, logger_error)
            order_list = order_manager.get_search_orders(request, True)
            result.set('total_count', len(order_list))
            result.set('search_items', order_list)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Bad request')

        return Response(result.get_response(), result.get_code())
