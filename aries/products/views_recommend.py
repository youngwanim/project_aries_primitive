import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse

from aries.products.common.product_func import add_discount_information
from aries.products.manager.menu_manager_v2 import MenuManagerV2
from aries.products.manager.product_manager_v3 import ProductManagerV3
from aries.products.manager.time_bomb_manager import TimeBombManager


class RecommendProductV2(APIView):
    """
    Recommend Product V2
    """
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    def get(self, request, hub_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        lang_info = header_parser.parse_language_v2(request.META)

        target_db = lang_info.target_db
        cn_header = lang_info.cn_header
        os_type = lang_info.os_type

        product_manager = ProductManagerV3(self.logger_info, self.logger_error)
        product_list = product_manager.get_recommend_product(hub_id)

        menu_manager = MenuManagerV2(self.logger_info, self.logger_error)

        for product in product_list:
            menu_manager.get_menu_data(product, target_db, cn_header)

        # Check the current available time bomb
        time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
        time_bomb_id = time_bomb_manager.get_time_bomb_now(hub_id, os_type, has_after=False)

        if time_bomb_id is not None:
            # Discount information add
            discount_map = product_manager.get_all_discount_info(time_bomb_id, cn_header)

            for product in product_list:
                # Time bomb information parsing
                if product['id'] in discount_map:
                    discount_info = discount_map[product['id']]
                    add_discount_information(product, discount_info)

        result.set('hub_id', hub_id)
        result.set('products', product_list)

        return Response(result.get_response(), status=result.get_code())
