from aries.common import product_util
from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.message_utils import message_mapper
from aries.products.serializers import ProductListInfoSerializer, MenuValidationSerializer
from aries.products.service.menu_service import MenuService
from aries.products.service.product_service import ProductService


class QuantityManager:

    def __init__(self, logger_info, logger_error, target_db):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.target_db = target_db
        self.product_service = ProductService(self.logger_info, self.logger_error, target_db)
        self.menu_service = MenuService(self.logger_info, self.logger_error, target_db)

    def check_quantity(self, product_list, delivery_schedule):
        """Check a product quantity and return dictionary including result params

        Keyword arguments:
        product_list -- product list to validate
        delivery_schedule -- delivery schedule to receive foods
        """
        result_list = []
        result_product_list = []
        result_map = {}

        first_product_check = True
        sales_time = 0

        for product in product_list:
            product_instance = self.product_service.read_product_with_id(product['product']['id'])
            hub_instance = product_instance.hub
            menu_instance = product_instance.menu
            hub_stock = self.menu_service.read_hub_stock_instance(hub_instance, menu_instance)

            # Check real stock unit
            order_quantity = product['quantity']
            stock = hub_stock.stock

            if stock < order_quantity:
                msg = '[quantity_manager][QuantityManager][check_quantity][Product already sold]'
                self.logger_error.error(msg)
                error_msg = message_mapper.get_with_target_db(3001, self.target_db) + '[' + menu_instance.name + ']'
                raise BusinessLogicError(error_msg, 3001, None)

            # Check real time
            sales_time = product_instance.sales_time
            if not product_util.get_selling_time_delivery_schedule(sales_time, delivery_schedule):
                msg = '[quantity_manager][QuantityManager][check_quantity][Schedule invalid]'
                self.logger_error.error(msg)
                error_msg = message_mapper.get_with_target_db(3015, self.target_db) + '[' + menu_instance.name + ']'
                raise BusinessLogicError(error_msg, 3015, None)

            # Product information
            product_data = ProductListInfoSerializer(product_instance).data
            menu_data = MenuValidationSerializer(menu_instance).data

            product_data['menu'] = menu_data
            product_data['quantity'] = product['quantity']

            result_product_list.append(product_data)

            if first_product_check:
                product_order_name = product_instance.menu.name
                result_map['product_title'] = product_order_name
                first_product_check = False

            self.logger_info.info('[quantity_manager][QuantityManager][check_quantity][' +
                                  str(stock) + ' ' + str(product['quantity']) + ']')

            if stock >= product['quantity']:
                result_list.append(product['product_id'])

        if int(len(result_list)-1) != 0:
            result_map['product_sub'] = '(and ' + str(len(result_list)-1) + ' more)'
        else:
            result_map['product_sub'] = ''

        result_map['sales_time'] = sales_time
        result_map['product_count'] = len(result_list)
        result_map['product_index_list'] = result_list
        result_map['product_list'] = result_product_list

        return result_map
