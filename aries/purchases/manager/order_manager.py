import json
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q

from aries.common import product_util
from aries.purchases.common.admin_constant import get_menu_en, get_menu_cn
from aries.purchases.factory.order_factory import OrderInstance
from aries.purchases.models import Order
from aries.purchases.serializers import OrderSerializer


class OrderManager:
    UPCOMING_ORDER = 0
    PAST_ORDER = 1
    OPERATION_ORDER = 10

    order_count = 0

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

    def get_orders(self, order_type, query_map):
        order_qs = Order.objects.filter(**query_map).order_by('-id')
        self.order_count = len(order_qs)
        order_instance = OrderInstance.factory(order_type)
        order_list = order_instance.get_order_list(order_qs)
        return order_list

    def get_search_orders(self, request, has_list):
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        open_id = request.GET.get('open_id', '')
        query_string = request.GET.get('query', '')

        filter_str = {}
        if len(start_date) > 1 and len(end_date) > 1:
            filter_str['delivery_date__gte'] = start_date
            filter_str['delivery_date__lte'] = end_date

        if len(open_id) > 1:
            filter_str['open_id'] = open_id

        if len(query_string) <= 1:
            orders = Order.objects.filter(**filter_str)
        else:
            orders = Order.objects.filter(
                Q(order_id__icontains=query_string) |
                Q(user_name__icontains=query_string) |
                Q(user_telephone__icontains=query_string) |
                Q(open_id__icontains=query_string)
            )

        paginator = Paginator(orders, limit)
        order_objects = paginator.page(page).object_list

        serializer = OrderSerializer(order_objects, many=True)
        order_data = serializer.data

        if has_list:
            orders_list = [order['order_id'] for order in order_data]
            search_list = [{'id': index + ((page - 1) * limit) + 1, 'detail': orders_list[index]}
                           for index in range(len(orders_list))]

            order_data = search_list
        else:
            order_instance = OrderInstance.factory(self.OPERATION_ORDER)
            order_data = order_instance.get_order_list(order_data)

        return order_data

    def get_operation_orders(self, hub_id, date_info, delivery_schedule, page, limit):
        query_dict = {
            'hub_id': hub_id
        }

        if delivery_schedule is not None:
            if int(delivery_schedule) != -1:
                query_dict['delivery_schedule'] = int(delivery_schedule)

        if date_info[2] is not None:
            target_date = datetime.strptime(date_info[2], '%Y-%m-%d').date()
            query_dict['delivery_date'] = target_date
        elif date_info[3] is not None and date_info[4] is not None:
            month_date = product_util.get_month_schedule(date_info[3], date_info[4])
            query_dict['order_start_date__gte'] = month_date[0]
            query_dict['order_start_date__lte'] = month_date[1]
        else:
            query_dict['order_start_date__gte'] = date_info[0]
            query_dict['order_start_date__lte'] = date_info[1]

        orders = Order.objects.filter(**query_dict).order_by('-id')
        order_count = len(orders)

        paginator = Paginator(orders, limit)
        order_objects = paginator.page(page).object_list

        serializer = OrderSerializer(order_objects, many=True)
        order_data = serializer.data

        order_instance = OrderInstance.factory(self.OPERATION_ORDER)
        order_list = order_instance.get_order_list(order_data)

        result = (order_list, order_count)
        return result

    def get_order_separation(self, order_list):
        preparing_list = list()

        for order in order_list:
            if 1 <= order['operation_status'] <= 4:
                preparing_list.append(order)

        payload = {
            'orders': order_list,
            'preparing_orders': preparing_list
        }
        return payload

    def get_order_detail(self, order_id):
        order = Order.objects.get(order_id=order_id)
        serializer = OrderSerializer(order)

        order_data = serializer.data
        purchase_order = order.purchase_order

        # Order data
        order_data['order_status_history'] = json.loads(order_data['order_status_history'])
        order_data['operation_status_history'] = json.loads(order_data['operation_status_history'])
        order_data['order_details'] = json.loads(purchase_order.order_details)
        order_data['special_instruction'] = purchase_order.special_instruction
        order_data['extra_telephone'] = purchase_order.extra_telephone
        order_data['include_cutlery'] = purchase_order.include_cutlery

        # Order menu data
        product_details = order_data['order_details']['products_detail']

        for product_detail in product_details:
            product_detail['product_name_en'] = get_menu_en(product_detail['menu_id'])
            product_detail['product_name_cn'] = get_menu_cn(product_detail['menu_id'])

        # price information
        order_data['price_sub_total'] = purchase_order.price_sub_total
        order_data['price_delivery_fee'] = purchase_order.price_delivery_fee
        order_data['price_discount'] = purchase_order.price_discount
        order_data['price_total'] = purchase_order.price_total

        # Address information (Please check after purchase order model update)
        order_data['address_id'] = purchase_order.delivery_address_id

        del order_data['purchase_order']

        return order_data

    def get_order_list(self, order_id):
        order = Order.objects.get(order_id=order_id)
        serializer = OrderSerializer(order)
        order_data = serializer.data

        order_data['order_status_history'] = json.loads(order_data['order_status_history'])
        order_data['operation_status_history'] = json.loads(order_data['operation_status_history'])
        order_data['delivery_schedule_time'] = product_util.get_delivery_schedule_str(order_data['delivery_schedule'])

        return order_data
