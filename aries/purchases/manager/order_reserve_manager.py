import json
from datetime import datetime

import requests

from aries.common import urlmapper, code, hub_data, payment_util
from aries.common.code_msg import get_msg
from aries.common.exceptions.exceptions import BusinessLogicError, DataValidationError
from aries.common.message_utils import message_mapper
from aries.purchases.serializers import PurchaseOrderSerializer


class OrderReserveManager:

    def __init__(self, logger_info, logger_error, request_data):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.request_data = request_data
        self.payment_params = dict()
        self.product_details = list()
        self.product_dict = dict()
        self.product_total_price = None
        self.order_details = dict()
        self.order_id = None

    def product_validation(self, validation_result, cn_header):
        original_product_list = self.request_data['product_list']

        response_list = validation_result['product_list']

        valid_list = list()
        invalid_list = list()

        original_product_count = len(original_product_list)
        response_product_count = len(response_list)

        if original_product_count != response_product_count:
            error_message = message_mapper.get(3001, cn_header)
            data_set = {'product_list': response_list, 'has_changed': True}
            raise BusinessLogicError(error_message, 3001, data_set)

        for product in original_product_list:
            for response_product in response_list:
                if product['product_id'] == response_product['prev_product_id']:
                    if product['quantity'] <= response_product['stock']:
                        valid_list.append({
                            'product_id': response_product['product_id'],
                            'quantity': product['quantity']
                        })
                    else:
                        invalid_list.append({
                            'product_id': response_product['product_id'],
                            'quantity': response_product['stock'],
                        })
                elif product['product_id'] == response_product['product_id']:
                    if product['quantity'] <= response_product['stock']:
                        valid_list.append({
                            'product_id': response_product['product_id'],
                            'quantity': product['quantity']
                        })
                    else:
                        invalid_list.append({
                            'product_id': response_product['product_id'],
                            'quantity': response_product['stock'],
                        })

        if len(invalid_list) > 0:
            self.logger_error.error(code.ERROR_3001_PRODUCT_ALREADY_SOLD)
            error_message = message_mapper.get(3001, cn_header)
            data_set = {'product_list': response_list, 'has_changed': True}
            raise BusinessLogicError(error_message, 3001, data_set)

        response_list = valid_list

        return response_list

    def delivery_time_validation(self, product_list, accept_lang, os_type, hub_id):
        headers = {'accept-language': accept_lang}
        payload = {'product_list': product_list, 'delivery_schedule': self.request_data['delivery_schedule'],
                   'os_type': os_type, 'hub_id': hub_id}
        response = requests.post(urlmapper.get_url('PRODUCT_VALIDATION'), headers=headers, json=payload)
        response_json = response.json()

        # If quantity of product to purchase quantity is not valid or delivery schedule invalid
        if response.status_code != code.ARIES_200_SUCCESS:
            self.logger_error.error(response_json['error_code'])
            raise BusinessLogicError(response_json['error_message'], None, None)

        return response_json

    def set_product_detail(self, product_json):
        # Setting product data
        product_title = product_json['product_title']
        self.payment_params['product_title'] = product_title
        self.request_data['product_title'] = product_title
        self.request_data['product_sub'] = product_json['product_sub']

        # Make Orders detail data
        product_list = product_json['product_list']
        product_total_price = 0.0

        # products detail
        for product in product_list:
            menu = product['menu']
            self.product_dict[product['id']] = menu['name']

            # Calculate product price
            # Check if discount product, get discount price
            price_discount_event = product['price_discount_event']
            price = product['price']
            price_discount = product['price_discount']

            if price_discount_event:
                original_price = price
                price = price_discount
            else:
                original_price = price
                price = price

            product_total_price += (price * product['quantity'])
            product_json = {'product_id': product['id'], 'type': product['type'],
                            'product_name': menu['name'], 'quantity': product['quantity'], 'price': price,
                            'price_discount_event': price_discount_event, 'original_price': original_price,
                            'menu_id': menu['id']}
            self.product_details.append(product_json)

        self.product_total_price = round(product_total_price, 2)
        self.payment_params['total_price'] = self.product_total_price
        self.order_details['products_detail'] = self.product_details

        return product_list

    def set_delivery_detail(self, cn_header):
        # Shipping method
        self.request_data['shipping_method'] = 1
        if 'delivery_on_site' in self.request_data:
            delivery_on_site = self.request_data['delivery_on_site']
        else:
            delivery_on_site = False
            self.request_data['delivery_on_site'] = False

        if delivery_on_site:
            delivery_type = 2
            self.request_data['shipping_method'] = 2
            self.request_data['shipping_cost'] = 0.0
            self.request_data['delivery_as_fast'] = False
        else:
            self.request_data['shipping_cost'] = 8.0
            delivery_type = self.request_data['shipping_method']

        # add shipping name
        delivery_name = hub_data.get_delivery_service_str(cn_header, delivery_type)
        self.request_data['shipping_name'] = delivery_name

        delivery_price = self.request_data['shipping_cost']

        # Check delivery price
        if float(hub_data.get_shipping_cost(delivery_type)) != float(delivery_price):
            self.logger_info.info('Some cost is incorrect')
            raise DataValidationError('Some costs are incorrect')

        delivery_detail_json = {'delivery_title': hub_data.get_delivery_str(cn_header, delivery_type),
                                'price': delivery_price}
        self.order_details['delivery_detail'] = delivery_detail_json

        delivery_date = self.request_data['delivery_date'].replace('.', '-')
        self.request_data['delivery_date'] = delivery_date

        time_table_delivery_type = delivery_type
        if delivery_on_site:
            time_table_delivery_type = 1

        time_table_address = '{}/{}/{}/{}/{}'.format(
            urlmapper.get_url('TIMETABLE_LIST'), str(self.request_data['hub_id']), delivery_date,
            str(self.request_data['delivery_schedule']), str(time_table_delivery_type)
        )

        response = requests.get(time_table_address)
        response_json = response.json()

        if response.status_code != code.ARIES_200_SUCCESS:
            self.logger_error.error(code.ERROR_3007_DELIVERY_SCHEDULE_INVALID)
            raise BusinessLogicError(message_mapper.get(3007, cn_header), 3007, None)

        self.logger_info.info(response_json)
        self.request_data['shipping_detail'] = json.dumps(response_json['shipping_detail'])
        self.request_data['delivery_start_time'] = response_json['delivery_start_time']
        self.request_data['delivery_end_time'] = response_json['delivery_end_time']

    def set_total_price(self, coupon_detail, discount_amount, open_id):
        self.order_details['coupons_detail'] = coupon_detail
        delivery_price = self.request_data['shipping_cost']

        total_price = round((self.product_total_price + discount_amount + delivery_price), 2)
        self.logger_info.info(str(self.product_total_price) + ' ' + str(discount_amount) + ' ' +
                              str(delivery_price) + ' ' + str(total_price))

        if float(self.request_data['price_sub_total']) != float(self.product_total_price) \
                or -float(self.request_data['price_discount']) != float(discount_amount) \
                or float(self.request_data['price_delivery_fee']) != float(delivery_price) \
                or float(self.request_data['price_total']) != float(total_price):
            error_code = code.ERROR_3006_PAYMENT_PRICE_INVALID
            self.logger_error.error(error_code)
            raise BusinessLogicError(get_msg(error_code), error_code, None)

        self.request_data['order_details'] = json.dumps(self.order_details)
        self.request_data['product_list'] = json.dumps(self.request_data['product_list'])
        self.request_data['coupon_list'] = json.dumps(self.request_data['coupon_list'])

        # Make order response
        datetime_now = datetime.now()
        telephone = self.request_data['user_telephone']
        delivery_date = self.request_data['delivery_date']
        hub_id = self.request_data['hub_id']

        order_hash = payment_util.get_order_hash(datetime_now, telephone, delivery_date, open_id)
        order_id = payment_util.get_order_id(order_hash, open_id, hub_id)

        self.order_id = order_id
        self.payment_params['order_id'] = order_id
        self.request_data['order_hash'] = order_hash
        self.request_data['order_id'] = order_id
        self.request_data['created_date'] = datetime_now
        self.payment_params['total_price'] = total_price

    def set_misc_params(self):
        if 'include_cutlery' not in self.request_data:
            self.request_data['include_cutlery'] = True

    def get_payment_param(self, cn_header):
        self.payment_params['cn_header'] = cn_header

        if 'wechat_code' in self.request_data:
            self.payment_params['wechat_code'] = self.request_data['wechat_code']

        if 'ip_addr' in self.request_data:
            self.payment_params['ip_addr'] = self.request_data['ip_addr']

        payment_type = self.request_data['payment_type']
        param_result = (payment_type, self.payment_params)

        return param_result

    def save_purchase_order(self):
        # No purchase order object. Create new one.
        serializer = PurchaseOrderSerializer(data=self.request_data)

        if not serializer.is_valid():
            self.logger_info.info(serializer.errors)
            raise DataValidationError('Request data invalid', None)

        serializer.save()
        save_result = self.order_id

        return save_result
