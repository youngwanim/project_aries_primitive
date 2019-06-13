import aries.products.common.product_func as func_util

from aries.common import product_util

from aries.products.common.menu_v2_func import get_menu_data
from aries.products.manager.menu_manager import MenuManager
from aries.products.manager.restaurant_manager import RestaurantManager
from aries.products.service.menu_service import MenuService


class MenuManagerV2:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    # Get product information as price, stock or something.
    def get_menu_data(self, product, target_db, cn_header):
        menu_manager = MenuManager(self.logger_info, self.logger_error)
        restaurant_manager = RestaurantManager(self.logger_info, self.logger_error)

        menu_id = product['menu']
        menu_data = menu_manager.get_menu_data(target_db, menu_id, product['sales_time'], cn_header)

        menu_data['review_statics'] = menu_manager.get_menu_statics(menu_id)
        menu_data['restaurant'] = restaurant_manager.get_restaurant_data(menu_data['restaurant'], target_db)

        product['menu'] = menu_data

        # Add type description
        product['type_name'] = product_util.get_type_name(product['type'], cn_header)
        product['type_index'] = product_util.TYPE_INDEX[product['type']]

        product['status_label'] = product_util.get_product_state_label(cn_header, product['status'])

        return func_util.parse_category(product, cn_header)

    # Get product information as price, stock or something.
    def get_menu_data_for_list(self, product, target_db, cn_header, sales_time):
        menu_service = MenuService(self.logger_info, self.logger_error, target_db)
        menu_data = get_menu_data(menu_service.read_menu_data_with_id(product['menu']), cn_header, sales_time)

        restaurant_manager = RestaurantManager(self.logger_info, self.logger_error)

        menu_data['review_statics'] = menu_service.read_menu_statics_data(menu_data)
        menu_data['restaurant'] = restaurant_manager.get_restaurant_data(menu_data['restaurant'], target_db)

        product['menu'] = menu_data

        # Add type description
        product['type_name'] = product_util.get_type_name(product['type'], cn_header)
        product['type_index'] = product_util.TYPE_INDEX[product['type']]

        product['status_label'] = product_util.get_product_state_label(cn_header, product['status'])

        # Check description type and description
        if product['has_description']:
            desc_type = product['description_type']
            product['description'] = func_util.parse_description_msg(desc_type, cn_header)

        return func_util.parse_category(product, cn_header)

    def get_menu_statics(self, menu_id):
        menu_service = MenuService(self.logger_info, self.logger_error, 'default')
        return menu_service.read_menu_statics(menu_id)
