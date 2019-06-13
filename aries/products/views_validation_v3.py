import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse

from aries.products.manager.hub_manager_v2 import HubManagerV2
from aries.products.manager.menu_manager import MenuManager
from aries.products.manager.product_manager_v3 import ProductManagerV3
from aries.products.manager.restaurant_manager import RestaurantManager

logger_info = logging.getLogger('products_info')
logger_error = logging.getLogger('products_error')


class ProductValidationBasic(APIView):
    SUCCESS = 'success'

    def post(self, request, hub_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS)

        lang_info = header_parser.parse_language_v2(request.META)

        cn_header = lang_info.cn_header
        target_db = lang_info.target_db
        os_type = lang_info.os_type

        try:
            product_list = request.data['product_list']
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        product_manager = ProductManagerV3(logger_info, logger_error)
        menu_manager = MenuManager(logger_info, logger_error)
        restaurant_manager = RestaurantManager(logger_info, logger_error)
        hub_manager = HubManagerV2(logger_info, logger_error)

        product_list = hub_manager.get_product_list(product_list, hub_id)
        stock_list = hub_manager.get_stock_list(hub_id, product_list, target_db, os_type)

        if len(stock_list) >= 1:
            for product in stock_list:
                # Get product data
                product_data = product_manager.get_product_for_valid(product['product_id'], cn_header)

                # Set time bomb information
                if 'time_bomb_info' in product:
                    product['time_bomb_info']['stock'] = product['stock']
                    product['time_bomb_info']['has_stock'] = True
                    product_data['price_discount'] = product['price_discount']
                    product_data['event_product'] = product['event_product']
                    product_data['price_discount_event'] = True

                product['product'] = product_data

                # Get menu data
                menu_id = product_data['menu']
                menu_data = menu_manager.get_menu_data(target_db, menu_id, product_data['sales_time'], cn_header)

                menu_data['review_statics'] = menu_manager.get_menu_statics(menu_id)
                menu_data['restaurant'] = restaurant_manager.get_restaurant_data(menu_data['restaurant'], target_db)

                product['product']['menu'] = menu_data

                # Delete unusable field
                del product['product_id']
                del product['menu_id']
                del product['prev_product_id']

            result.set('product_list', stock_list)
        else:
            result.set('product_list', [])

        return Response(result.get_response(), result.get_code())


class ProductValidationV3(APIView):
    SUCCESS = 'success'

    def post(self, request, hub_id, time):
        result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS)
        logger_info.info(str(time))

        lang_info = header_parser.parse_language_v2(request.META)

        cn_header = lang_info.cn_header
        target_db = lang_info.target_db
        os_type = lang_info.os_type

        try:
            product_list = request.data['product_list']
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        product_manager = ProductManagerV3(logger_info, logger_error)
        menu_manager = MenuManager(logger_info, logger_error)
        restaurant_manager = RestaurantManager(logger_info, logger_error)
        hub_manager = HubManagerV2(logger_info, logger_error)

        product_list = hub_manager.get_product_list(product_list, hub_id)
        stock_list = hub_manager.get_stock_list(hub_id, product_list, target_db, os_type)

        if len(stock_list) >= 1:
            for product in stock_list:
                # Get product data
                product_data = product_manager.get_product_for_valid(product['product_id'], cn_header)

                # Set time bomb information
                if 'time_bomb_info' in product:
                    product['time_bomb_info']['stock'] = product['stock']
                    product['time_bomb_info']['has_stock'] = True
                    product_data['price_discount'] = product['price_discount']
                    product_data['event_product'] = product['event_product']
                    product_data['price_discount_event'] = True

                product['product'] = product_data

                # Get menu data
                menu_id = product_data['menu']
                menu_data = menu_manager.get_menu_data(target_db, menu_id, product_data['sales_time'], cn_header)

                menu_data['review_statics'] = menu_manager.get_menu_statics(menu_id)
                menu_data['restaurant'] = restaurant_manager.get_restaurant_data(menu_data['restaurant'], target_db)

                product['product']['menu'] = menu_data

                # Delete unusable field
                del product['product_id']
                del product['menu_id']
                del product['prev_product_id']
            result.set('product_list', stock_list)
        else:
            result.set('product_list', [])

        return Response(result.get_response(), result.get_code())


class PurchaseValidationV3(APIView):
    SUCCESS = 'success'

    def post(self, request, hub_id, time):
        result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS)
        logger_info.info(str(time))

        lang_info = header_parser.parse_language_v2(request.META)

        cn_header = lang_info.cn_header
        target_db = lang_info.target_db
        os_type = lang_info.os_type

        try:
            product_list = request.data['product_list']
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        product_manager = ProductManagerV3(logger_info, logger_error)
        menu_manager = MenuManager(logger_info, logger_error)
        restaurant_manager = RestaurantManager(logger_info, logger_error)
        hub_manager = HubManagerV2(logger_info, logger_error)

        product_list = hub_manager.get_product_list(product_list, hub_id)
        stock_list = hub_manager.get_stock_list(hub_id, product_list, target_db, os_type)

        for product in stock_list:
            # Get product data
            product_data = product_manager.get_product_for_valid(product['product_id'], cn_header)

            # Set time bomb information
            if 'time_bomb_info' in product:
                product['time_bomb_info']['stock'] = product['stock']
                product['time_bomb_info']['has_stock'] = True
                product_data['price_discount'] = product['price_discount']
                product_data['event_product'] = product['event_product']
                product_data['price_discount_event'] = True

            product['product'] = product_data

            # Get menu data
            menu_id = product_data['menu']
            menu_data = menu_manager.get_menu_data(target_db, menu_id, product_data['sales_time'], cn_header)

            menu_data['review_statics'] = menu_manager.get_menu_statics(menu_id)
            menu_data['restaurant'] = restaurant_manager.get_restaurant_data(menu_data['restaurant'], target_db)

            product['product']['menu'] = menu_data

        result.set('product_list', stock_list)

        return Response(result.get_response(), result.get_code())
