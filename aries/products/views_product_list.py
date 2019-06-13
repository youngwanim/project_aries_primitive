import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import DataValidationError, BusinessLogicError
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse
from aries.common.product_util import get_date_information_v3
from aries.products.common.product_func import add_discount_information
from aries.products.manager.menu_manager_v2 import MenuManagerV2
from aries.products.manager.product_manager_v3 import ProductManagerV3
from aries.products.manager.time_bomb_manager import TimeBombManager

logger_info = logging.getLogger('products_info')
logger_error = logging.getLogger('products_error')


class ProductListV2(APIView):
    """
    Product list v2 class
    """
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    def get(self, request, hub_id):
        lang_info = parse_language_v2(request.META)
        date_info = get_date_information_v3(hub_id)

        target_db = lang_info.target_db
        cn_header = lang_info.cn_header
        os_type = lang_info.os_type
        time_type = date_info.time_type

        try:
            # Get product list from specific hub
            product_manager = ProductManagerV3(self.logger_info, self.logger_error)
            product_list = product_manager.get_product_list(hub_id, date_info.current_date)

            menu_manager = MenuManagerV2(self.logger_info, self.logger_error)

            for product in product_list:
                menu_manager.get_menu_data_for_list(product, target_db, cn_header, product['sales_time'])

            # Check the current available time bomb
            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            time_bomb_id = time_bomb_manager.get_time_bomb_now(hub_id, os_type, has_after=False)

            if time_bomb_id is not None:
                # Discount information add
                discount_map = product_manager.get_all_discount_info(time_bomb_id, cn_header)

                for product in product_list:
                    if product['id'] in discount_map:
                        discount_info = discount_map[product['id']]
                        add_discount_information(product, discount_info)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('hub_id', hub_id)
            result.set('current_time_type', time_type)
            result.set('phase_next_day', date_info.phase_next_day)
            result.set('phase_date', date_info.current_date.isoformat())
            result.set('products', product_list)

        return Response(result.get_response(), status=result.get_code())
