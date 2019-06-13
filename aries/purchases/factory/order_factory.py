import json
import logging

from aries.common import dateformatter
from aries.common import product_util
from aries.common.http_utils import api_request_util
from aries.purchases.common.admin_constant import get_menu_en, get_menu_cn
from aries.purchases.models import PurchaseOrder
from aries.purchases.serializers import UpcomingPurchaseOrderSerializer, UpcomingOrderSerializer
from aries.purchases.service.dada_service import DadaService

UPCOMING_ORDER = 0
PAST_ORDER = 1

OPERATION_ORDER = 10

DATE_WITH_AM_PM = '%Y-%m-%d %I:%M %p'

logger_info = logging.getLogger('purchases_info')
logger_error = logging.getLogger('purchases_error')


class OrderInstance(object):
    order_data = ''

    def factory(order_type):
        if order_type == UPCOMING_ORDER:
            return UpcomingOrder()
        elif order_type == PAST_ORDER:
            return PastOrder()
        elif order_type == OPERATION_ORDER:
            return OperationOrders()
    factory = staticmethod(factory)


class UpcomingOrder(OrderInstance):

    def __init__(self):
        self.time_table_map = {}

    def get_order_list(self, order_data):
        order_list = [self.parse_order_list(order) for order in order_data]
        return order_list

    def parse_order_list(self, order):
        purchase_order = order.purchase_order
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
        start_date = order.order_start_date.strftime(DATE_WITH_AM_PM)
        order_data['order_start_date'] = dateformatter.get_yymmdd_time(start_date)
        order_data['order_status_history'] = json.loads(order_data['order_status_history'])
        order_data['purchase_order'] = purchase_order_data
        order_data['order_cancel_date'] = ''

        # Get Timetable
        order_status = order_data['order_status']
        if order_status == 0:
            hub_id = purchase_order.hub_id
            sales_time = 0

            if sales_time in self.time_table_map:
                order_data['timetable'] = self.time_table_map[sales_time]
            else:
                order_data['timetable'] = api_request_util.get_time_table(hub_id, sales_time)
                self.time_table_map[sales_time] = order_data['timetable']
        else:
            order_data['timetable'] = []

        return order_data


class PastOrder(OrderInstance):
    def get_order_list(self, order_data):
        order_list = [self.parse_order_list(order) for order in order_data]
        return order_list

    def parse_order_list(self, order):
        purchase_order = order.purchase_order
        order_serializer = UpcomingOrderSerializer(order)
        order_data = order_serializer.data

        orders = dict()
        orders['order_id'] = order_data['order_id']
        orders['order_status'] = order_data['order_status']
        orders['created_date'] = str(purchase_order.created_date)[:10]
        orders['product_title'] = purchase_order.product_title
        orders['product_sub'] = purchase_order.product_sub
        orders['price_total'] = purchase_order.price_total
        orders['delivery_on_site'] = purchase_order.delivery_on_site
        orders['delivery_schedule_time'] = product_util.get_delivery_schedule_str(order_data['delivery_schedule'])

        return orders


class OperationOrders(OrderInstance):
    def get_order_list(self, order_data):
        order_list = [self.parse_order_list(order) for order in order_data]
        return order_list

    def parse_order_list(self, order):
        try:
            purchase_order = PurchaseOrder.objects.get(id=order['purchase_order'])

            # Order data
            order['order_details'] = json.loads(purchase_order.order_details)
            product_details = order['order_details']['products_detail']

            for product_detail in product_details:
                product_detail['product_name_en'] = get_menu_en(product_detail['menu_id'])
                product_detail['product_name_cn'] = get_menu_cn(product_detail['menu_id'])

            # Dada service
            dada_service = DadaService(logger_info, logger_error)
            order['shipping_order_detail'] = dada_service.read_dada_order_detail(order['order_id'])

            # Include cutlery and special instruction added
            order['include_cutlery'] = purchase_order.include_cutlery
            order['special_instruction'] = purchase_order.special_instruction
        except Exception as e:
            print(e)

        order['order_status_history'] = json.loads(order['order_status_history'])
        order['operation_status_history'] = json.loads(order['operation_status_history'])
        order['delivery_schedule_time'] = product_util.get_delivery_schedule_str(order['delivery_schedule'])

        if order['order_cancel_date'] is None:
            order['order_cancel_date'] = ''
        if order['order_finish_date'] is None:
            order['order_finish_date'] = ''

        del order['purchase_order']
        return order
