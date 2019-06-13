from aries.common import code
from aries.common import product_util
from aries.common.models import ResultResponse
from aries.products.manager.menu_manager import MenuManager

from aries.products.manager.product_factory import ProductsInstance
from aries.products.manager.restaurant_manager import RestaurantManager
from aries.products.models import Product
from aries.products.serializers import ProductListInfoSerializer
from aries.products.service.product_type_service import ProductTypeService

import aries.products.common.product_func as func_util


class ProductManager:
    PRODUCT_LIST = 0
    PRODUCT_DETAIL = 1
    PRODUCT_GENERAL = 2
    PRODUCT_SINGLE = 3
    RECOMMEND_BRAND = 1
    RECOMMEND_DETAIL = 2
    RECOMMEND_BAG = 3

    MENU_TYPE_PROMOTION = 20

    product_list = []
    promotion_list = []

    review_items = None

    ALL_DAY_TYPE = 0

    def __init__(self, logger_info, logger_error, language_info, date_info):
        self.logger_info = logger_info
        self.logger_error = logger_error

        if date_info is not None:
            self.date_info = date_info
            self.hub_id = date_info[0]
            self.time_type = date_info[1]
            self.phase_next_day = date_info[2]
            self.current_date = date_info[3]
            self.lunch_time = date_info[4]

        if language_info is not None:
            self.language_info = language_info
            self.cn_header = language_info[0]
            self.target_db = language_info[1]
            self.accept_lang = language_info[2]

        self.product_type_service = ProductTypeService(logger_info, logger_error)
        self.result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

    def get_product(self, product_id):
        product_instance = ProductsInstance.factory(self.PRODUCT_SINGLE, self.date_info)
        product_data = product_instance.get_products_data(product_id)
        return self.get_menu_data(product_data)

    def get_product_list(self, product_type):
        products_instance = ProductsInstance.factory(product_type, self.date_info)
        products_data = products_instance.get_products_data()

        self.product_list = [self.get_menu_data(product_item) for product_item in products_data]
        return self.product_list

    def get_product_detail_list(self, product_type, product):
        products_instance = ProductsInstance.factory(product_type, self.date_info)
        products_data = products_instance.get_products_data(self.ALL_DAY_TYPE, product)

        self.product_list = [self.get_menu_data(product_item) for product_item in products_data]
        return self.product_list

    def get_product_recommend_list(self, product_type):
        products_instance = ProductsInstance.factory(product_type, self.date_info)
        products_data = products_instance.get_products_data(self.ALL_DAY_TYPE)

        self.product_list = [self.get_menu_data(product_item) for product_item in products_data]
        return self.product_list

    def get_brand_product_list(self, product_type, brand_info, selected_time):
        products_instance = ProductsInstance.factory(product_type, self.date_info)
        products_data = products_instance.get_products_data(brand_info, selected_time)

        self.product_list = [self.get_menu_data(product_item) for product_item in products_data]
        return self.product_list

    def get_promotion_list(self):
        product_queryset = Product.objects.using('default').filter(
            hub=self.hub_id,
            type=self.MENU_TYPE_PROMOTION,
            start_date__lte=self.current_date,
            end_date__gte=self.current_date,
            sales_time=self.ALL_DAY_TYPE
        )
        products_data = ProductListInfoSerializer(product_queryset, many=True).data
        promotion_list = [self.get_review_data(product_item) for product_item in products_data]
        return promotion_list

    def get_product_type_list(self):
        product_type_list = self.product_type_service.read_product_type(self.cn_header)
        return product_type_list

    def get_menu_data(self, product):
        menu_manager = MenuManager(self.logger_info, self.logger_error)
        restaurant_manager = RestaurantManager(self.logger_info, self.logger_error)

        menu_id = product['menu']
        menu_data = menu_manager.get_menu_data(self.target_db, menu_id, product['sales_time'], self.cn_header)

        menu_data['review_statics'] = menu_manager.get_menu_statics(menu_id)
        menu_data['restaurant'] = restaurant_manager.get_restaurant_data(menu_data['restaurant'], self.target_db)

        product['menu'] = menu_data

        # Add type description
        product['type_name'] = product_util.get_type_name(product['type'], self.cn_header)
        product['type_index'] = product_util.TYPE_INDEX[product['type']]

        # SET menu or normal menu label data
        if not self.lunch_time and not self.phase_next_day and product['sales_time'] == 2:
            product['status'] = 3

        product['status_label'] = product_util.get_product_state_label(self.cn_header, product['status'])

        # Check description type and description
        if product['has_description']:
            desc_type = product['description_type']
            product['description'] = func_util.parse_description_msg(desc_type, self.cn_header)

        return func_util.parse_category(product, self.cn_header)

    def get_review_data(self, product):
        menu_manager = MenuManager(self.logger_info, self.logger_error)
        menu_id = product['menu']
        menu_data = menu_manager.get_menu_list_data(self.target_db, menu_id)
        menu_data['review_statics'] = menu_manager.get_menu_statics(menu_id)

        product['menu'] = menu_data

        return func_util.parse_category(product, self.cn_header)
