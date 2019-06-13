import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code, product_util
from aries.common.exceptions.exceptions import DataValidationError
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse
from aries.common.product_util import get_date_information_v2, get_sales_time_str
from aries.products.common.menu_v2_func import request_validation
from aries.products.common.product_func import add_discount_information
from aries.products.manager.menu_manager_v2 import MenuManagerV2
from aries.products.manager.product_manager_v3 import ProductManagerV3
from aries.products.manager.time_bomb_manager import TimeBombManager


class ProductInfoWithMenu(APIView):
    """
    Product information from menu id for curation interface
    """

    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    SUCCESS_MSG = 'success'

    def post(self, request, hub_id=1):
        try:
            request_data = request.data
            request_validation(request_data)

            menu_id_list = request_data['menu_id_list']
            target_db = request_data['target_db']

            cn_header = False if target_db == 'default' else True

            sales_time_str = get_sales_time_str()
            date_info = get_date_information_v2(hub_id, sales_time_str)
            lang_info = parse_language_v2(request.META)

            os_type = lang_info.os_type

            product_manager = ProductManagerV3(self.logger_info, self.logger_error)
            product_data = product_manager.get_product_info(hub_id, menu_id_list)

            menu_manager = MenuManagerV2(self.logger_info, self.logger_error)
            product_list = []

            for product in product_data:
                product_list.append(menu_manager.get_menu_data(product, target_db, cn_header))

            # Check the current available time bomb
            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            time_bomb_id = time_bomb_manager.get_time_bomb_now(hub_id, os_type)

            # Get time bomb information
            if time_bomb_id is not None:
                discount_map = product_manager.get_all_discount_info(time_bomb_id, cn_header)

                for product in product_list:
                    if product['id'] in discount_map:
                        discount_info = discount_map[product['id']]
                        add_discount_information(product, discount_info)

        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except Exception as e:
            self.logger_info.info(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS_MSG)
            result.set('products', product_list)
            result.set('hub_id', int(hub_id))
            result.set('time_type', date_info.time_type)
            result.set('phase_next_day', date_info.phase_next_day)
            result.set('phase_date', date_info.current_date.isoformat())
            result.set('order_available', product_util.get_available_time(date_info.time_type))

        return Response(result.get_response(), result.get_code())
