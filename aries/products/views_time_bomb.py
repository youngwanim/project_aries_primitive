import json
import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import DataValidationError
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse

from aries.products.common.product_func import add_discount_information
from aries.products.common.time_bomb_func import time_bomb_expired_template_en, time_bomb_expired_template_cn
from aries.products.manager.menu_manager_v2 import MenuManagerV2
from aries.products.manager.product_manager_v3 import ProductManagerV3
from aries.products.manager.stock_manager import StockManager
from aries.products.manager.time_bomb_manager import TimeBombManager


class TimeBomb(APIView):
    """
    Time Bomb information from hub id for sale event
    """
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    OS_TYPE = ['ANDROID', 'IOS', 'MOBILE_WEB']

    STATUS_NO_TIME_BOMB = 0
    STATUS_AVAILABLE = 1
    STATUS_SOLD_OUT = 2
    STATUS_TIME_EXPIRED = 3

    def get(self, request, time_bomb_id):
        lang_info = parse_language_v2(request.META)
        lang_type = 1 if lang_info.cn_header else 0
        cn_header = lang_info.cn_header
        target_db = lang_info.target_db
        os_type = lang_info.os_type
        self.logger_info.info('os_type : ' + self.OS_TYPE[os_type])

        try:
            # Get time bomb data
            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            time_bomb_exists = time_bomb_manager.check_time_bomb_exists(time_bomb_id)

            # Default product list setting
            product_list = []

            if time_bomb_exists:
                time_bomb = time_bomb_manager.get_time_bomb(time_bomb_id, lang_type, os_type)

                hub_id = time_bomb['hub']

                # Get product data and check sold out
                if time_bomb['status'] == self.STATUS_AVAILABLE:
                    product_manager = ProductManagerV3(self.logger_info, self.logger_error)
                    product_id_list = time_bomb['products']
                    product_list = product_manager.get_product_list_from_ids(product_id_list)

                    # Get menu id and check stock
                    stock_manager = StockManager(self.logger_info, self.logger_error)
                    menu_id_list = [product['menu'] for product in product_list]

                    # Check if status is sold out or available
                    if stock_manager.check_sold_out(hub_id, menu_id_list):
                        time_bomb['status'] = self.STATUS_SOLD_OUT

                    # For menu data parsing
                    menu_manager = MenuManagerV2(self.logger_info, self.logger_error)

                    # Discount information
                    discount_map = product_manager.get_time_bomb_discount_info(time_bomb_id,
                                                                               product_id_list, cn_header)

                    # Stock information
                    stock_map = stock_manager.get_stock_map(hub_id, menu_id_list)

                    for product in product_list:
                        menu_manager.get_menu_data(product, target_db, cn_header)

                        if product['id'] in discount_map:
                            discount_info = discount_map[product['id']]

                            # Stock check
                            if product['menu']['id'] in stock_map:
                                discount_info['has_stock'] = True
                                discount_info['stock'] = stock_map[product['menu']['id']]

                            add_discount_information(product, discount_info)
            else:
                # Time bomb expired template
                if cn_header:
                    time_bomb = time_bomb_expired_template_cn()
                else:
                    time_bomb = time_bomb_expired_template_en()

            # Add action template
            # time_bomb_url = 'https://m.viastelle.com/#/promotions/timeBombInt'
            extra = {
                'share_image': '', 'share_title': '', 'share_description': '', 'share_enable': False,
                'link': 'https://stg-cli.viastelle.com/dist/#/promotions/timeBombInt'
            }

            if cn_header:
                extra['title'] = '推广'
            else:
                extra['title'] = 'PROMOTION'

            action_object = {
                'action_type': 13,
                'action_target': 'https://stg-cli.viastelle.com/dist/#/promotions/timeBombInt',
                'action_extra': json.dumps(extra)
            }

            # Stock api call interval
            api_call_interval = 60
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except Exception as e:
            self.logger_info.info(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set_map(time_bomb)
            result.set('action', action_object)
            result.set('stock_api_interval', api_call_interval)
            result.set('products', product_list)

        return Response(result.get_response(), result.get_code())


class TimeBombDetail(APIView):
    """
    Get current time bomb information with specific hub
    """
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    OS_TYPE = ['ANDROID', 'IOS', 'MOBILE_WEB']

    STATUS_NO_TIME_BOMB = 0
    STATUS_AVAILABLE = 1
    STATUS_SOLD_OUT = 2
    STATUS_TIME_EXPIRED = 3

    def get(self, request, hub_id):
        lang_info = parse_language_v2(request.META)
        lang_type = 1 if lang_info.cn_header else 0
        os_type = lang_info.os_type
        self.logger_info.info('os_type : ' + self.OS_TYPE[os_type])

        try:
            # Get time bomb data
            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            time_bomb_id = time_bomb_manager.get_time_bomb_now(hub_id, os_type)

            if time_bomb_id is None:
                time_bomb = {'status': 0}
            else:
                time_bomb = time_bomb_manager.get_time_bomb(time_bomb_id, lang_type, os_type)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except Exception as e:
            self.logger_info.info(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set_map(time_bomb)

        return Response(result.get_response(), result.get_code())


class TimeBombStock(APIView):
    """
    Get current time bomb product information with specific hub
    """
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    OS_TYPE = ['ANDROID', 'IOS', 'MOBILE_WEB']

    STATUS_NO_TIME_BOMB = 0
    STATUS_AVAILABLE = 1
    STATUS_SOLD_OUT = 2
    STATUS_TIME_EXPIRED = 3

    def get(self, request, time_bomb_id):
        lang_info = parse_language_v2(request.META)
        lang_type = 1 if lang_info.cn_header else 0
        cn_header = lang_info.cn_header
        target_db = lang_info.target_db
        os_type = lang_info.os_type
        self.logger_info.info('os_type : ' + self.OS_TYPE[os_type])

        try:
            # Get time bomb data
            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            time_bomb = time_bomb_manager.get_time_bomb(time_bomb_id, lang_type, os_type)

            hub_id = time_bomb['hub']

            # Default product list setting
            product_list = []

            # Get product data and check sold out
            if time_bomb['status'] == self.STATUS_AVAILABLE:
                product_manager = ProductManagerV3(self.logger_info, self.logger_error)
                product_id_list = time_bomb['products']
                product_list = product_manager.get_product_list_from_ids(product_id_list)

                # Get menu id and check stock
                stock_manager = StockManager(self.logger_info, self.logger_error)
                menu_id_list = [product['menu'] for product in product_list]

                # Check if status is sold out or available
                if stock_manager.check_sold_out(hub_id, menu_id_list):
                    time_bomb['status'] = self.STATUS_SOLD_OUT

                # For menu data parsing
                menu_manager = MenuManagerV2(self.logger_info, self.logger_error)

                # Discount information
                discount_map = product_manager.get_time_bomb_discount_info(time_bomb_id, product_id_list, cn_header)

                # Stock information
                stock_map = stock_manager.get_stock_map(hub_id, menu_id_list)

                for product in product_list:
                    menu_manager.get_menu_data(product, target_db, cn_header)

                    if product['id'] in discount_map:
                        discount_info = discount_map[product['id']]

                        # Stock check
                        if product['menu']['id'] in stock_map:
                            discount_info['has_stock'] = True
                            discount_info['stock'] = stock_map[product['menu']['id']]

                        add_discount_information(product, discount_info)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except Exception as e:
            self.logger_info.info(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('status', time_bomb['status'])
            result.set('products', product_list)

        return Response(result.get_response(), result.get_code())
