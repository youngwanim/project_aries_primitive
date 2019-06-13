import json

from aries.common import code
from aries.common.exceptions.exceptions import DataValidationError
from aries.common.models import ResultResponse
from aries.products.common.product_func import parse_category, parse_product_misc, get_discount_info_map
from aries.products.serializers import ProductSerializer
from aries.products.service.product_service import ProductService


class ProductManagerV3:

    SALES_TIME_LUNCH = 2
    SALES_TIME_DINNER = 3

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

    def get_product_data(self, product_id):
        """
        Get single product information
        :param product_id: product id
        :return: product json object
        """
        product_service = ProductService(self.logger_info, self.logger_error, 'default')
        product_data = product_service.read_product_data_with_id(product_id)

        return product_data

    def get_product_list(self, hub_id, current_date):
        """
        Get product information from specific target hub
        :param hub_id: current hub id
        :param current_date: current date
        :return: product json object list
        """
        product_service = ProductService(self.logger_info, self.logger_error, 'default')
        product_list_data = product_service.read_product_list_v3(hub_id, current_date)

        return product_list_data

    def get_product_info(self, hub_id, menu_id_list):
        """
        Get product information from menu id list
        :param hub_id: current hub id
        :param menu_id_list: [1, 2, 65, 100]
        :return: product list
        """
        sales_status = 1

        product_service = ProductService(self.logger_info, self.logger_error, 'default')
        product_info_list = []

        for menu_id in menu_id_list:
            query_str = {'hub': hub_id, 'status__lte': sales_status, 'menu': menu_id}
            product_data = product_service.read_product_with_query(query_str)
            product_info_list.append(product_data)

        return product_info_list

    def get_recommend_product(self, hub_id):
        """
        Get recommend product within two items
        :param hub_id: hub id
        :return: product json object list
        """
        product_service = ProductService(self.logger_info, self.logger_error, 'default')
        product_query = {'hub_id': hub_id, 'status': 1, 'type__lte': 7, 'sales_time': 0}

        product_list = product_service.read_recommend_list(product_query)

        return product_list

    def get_product_for_valid(self, product_id, cn_header):
        """
        Get product information from specific target product id
        :param product_id: product id
        :param cn_header: language header
        :return: product json object
        """
        product_service = ProductService(self.logger_info, self.logger_error, 'default')
        product = product_service.read_product_data_with_id(product_id)

        # Status label and etc parsing
        parse_product_misc(product, cn_header)

        # Category parsing
        parse_category(product, cn_header)

        return product

    def get_product_list_from_ids(self, product_list):
        """
        Get product list from product id list
        :param product_list:
        :return: json array of product data
        """
        product_service = ProductService(self.logger_info, self.logger_error, 'default')
        product_list_qs = product_service.read_product_list_with_query({'id__in': product_list})
        product_list = ProductSerializer(product_list_qs, many=True).data

        return product_list

    def get_product_list_with_query(self, hub_id, start_date, end_date):
        """
        Get product list with query string
        :param hub_id: current hub id
        :param start_date: start date for getting product
        :param end_date: end date for getting product
        :return: dictionary with lunch product list and dinner product list
        """
        query_product = {'hub': hub_id, 'sales_time': 0,
                         'start_date__lte': start_date, 'end_date__gte': end_date}
        product_service = ProductService(self.logger_info, self.logger_error, 'default')

        product_list_qs = product_service.read_product_list_with_query(query_product)
        product_list = ProductSerializer(product_list_qs, many=True).data

        return product_list

    def update_product(self, product_data):
        """
        Update product instance data.
        :param product_data: Product data for changing previous product
        :return: product data after change
        """
        if 'badge_en' in product_data:
            product_data['badge_en'] = json.dumps(product_data['badge_en'])
        if 'badge_cn' in product_data:
            product_data['badge_cn'] = json.dumps(product_data['badge_cn'])

        self.logger_info.info('[ProductManagerV2][update_product][' + str(product_data) + ']')

        product_service = ProductService(self.logger_info, self.logger_error)
        result_product = product_service.update_product_with_data(product_data)

        return result_product

    def get_time_bomb_discount_info(self, time_bomb_id, product_id_list, cn_header):
        """
        Attached discount info to product from product_list
        :param time_bomb_id: time bomb id
        :param product_id_list: product id list
        :param cn_header: language header value
        :return: discount data list
        """
        product_service = ProductService(self.logger_info, self.logger_error, 'default')
        discount_list = product_service.read_product_discount_info(time_bomb_id, product_id_list)

        return get_discount_info_map(discount_list, cn_header)

    def get_all_discount_info(self, time_bomb_id, cn_header):
        """
        Return discount dict
        :param time_bomb_id: time bomb id
        :param cn_header: language header value
        :return: discount data list
        """
        product_service = ProductService(self.logger_info, self.logger_error, 'default')
        discount_list = product_service.read_product_discount_info_with_id(time_bomb_id)

        return get_discount_info_map(discount_list, cn_header)

    def get_product_validation(self, discount_info_list):
        """
        Check product is available or not
        :param discount_info_list: Discount info from time bomb
        :return: If available, true or not.
        """
        product_service = ProductService(self.logger_info, self.logger_error, 'default')

        for discount_info in discount_info_list:
            if not product_service.has_product(discount_info['product_id']):
                raise DataValidationError('Request data invalid', None)
