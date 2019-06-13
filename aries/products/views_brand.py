import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import product_util
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.products.manager.product_manager import ProductManager
from aries.products.manager.restaurant_manager import RestaurantManager


# V2 API for application api
class RestaurantBrandInfoPageDetail(APIView):
    LUNCH_TIME = '2'
    PRODUCT_BRAND = 4

    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    def get(self, request, restaurant_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        language_info = header_parser.parse_language_v2(request.META)
        date_info = product_util.get_date_information(1, self.LUNCH_TIME)
        target_db = language_info[1]

        try:
            restaurant_manager = RestaurantManager(self.logger_info, self.logger_error)
            brand_data = restaurant_manager.get_brand(target_db, restaurant_id)

            brand_id = brand_data['id']
            result.set('brand', brand_data)

            try:
                brand_time = product_util.get_sales_time()
                product_manager = ProductManager(self.logger_info, self.logger_error, language_info, date_info)
                product_list = product_manager.get_brand_product_list(self.PRODUCT_BRAND, brand_id, brand_time)
            except Exception as e:
                print(str(e))
                result.set('products', [])
            else:
                result.set('products', product_list)

        except ObjectDoesNotExist:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Brand info not found.')
        except Exception as e:
            self.logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Error : ' + str(e))

        return Response(result.get_response(), result.get_code())
