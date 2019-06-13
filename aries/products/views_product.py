import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.code_msg import get_msg
from aries.common.http_utils import header_parser
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse
from aries.products.common.product_func import check_delivery_schedule, add_discount_information, get_discount_info_map
from aries.products.manager.menu_manager_v2 import MenuManagerV2
from aries.products.manager.product_manager_v3 import ProductManagerV3
from aries.products.manager.review_manager import ReviewManager
from aries.products.manager.time_bomb_manager import TimeBombManager
from aries.products.service.product_service import ProductService
from aries.products.service.time_bomb_service import TimeBombService
from .models import Product, Menu, HubStock
from .serializers import ProductListInfoSerializer, MenuValidationSerializer

logger_info = logging.getLogger('products_info')
logger_error = logging.getLogger('products_error')


class Products(APIView):
    """
    Product information
    """
    SUCCESS_MSG = 'success'

    def get(self, request, product_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS_MSG)

        lang_info = parse_language_v2(request.META)
        target_db = lang_info.target_db
        os_type = lang_info.os_type
        cn_header = lang_info.cn_header

        product_manager = ProductManagerV3(logger_info, logger_error)
        menu_manager = MenuManagerV2(logger_info, logger_error)

        # Get product data
        product = product_manager.get_product_data(product_id)
        menu_manager.get_menu_data(product, target_db, cn_header)

        hub_id = product['hub']

        # Check the current available time bomb
        time_bomb_manager = TimeBombManager(logger_info, logger_error)
        time_bomb_id = time_bomb_manager.get_time_bomb_now(hub_id, os_type)

        if time_bomb_id is not None:
            discount_map = product_manager.get_all_discount_info(time_bomb_id, cn_header)

            # Time bomb information parsing
            if product['id'] in discount_map:
                discount_info = discount_map[product['id']]
                add_discount_information(product, discount_info)

        result.set('product', product)

        return Response(result.get_response(), result.get_code())


class ProductDetail(APIView):
    """
    Product detail read including other information
    """
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    DEFAULT_HUB_ID = 1

    def get(self, request, product_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        lang_info = parse_language_v2(request.META)
        target_db = lang_info.target_db
        os_type = lang_info.os_type
        cn_header = lang_info.cn_header

        product_queryset = Product.objects.filter(id=product_id, type__lte=10)
        product_count = product_queryset.count()

        if product_count < 1:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Product not found')
            return Response(result.get_response(), status=result.get_code())

        # Create manager
        product_manager = ProductManagerV3(logger_info, logger_error)
        menu_manager = MenuManagerV2(logger_info, logger_error)
        review_manager = ReviewManager(logger_info, logger_error)

        # Get product information
        product = product_manager.get_product_data(product_id)
        hub_id = product['hub']

        # Parsing menu and restaurant data
        menu_manager.get_menu_data(product, target_db, cn_header)
        result.set('product', product)

        # Recommend product information
        product_list = product_manager.get_recommend_product(hub_id)
        for product_obj in product_list:
            menu_manager.get_menu_data(product_obj, target_db, cn_header)
        result.set('products', product_list)

        # Time bomb information
        time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
        time_bomb_id = time_bomb_manager.get_time_bomb_now(hub_id, os_type, has_after=False)

        if time_bomb_id is not None:
            discount_map = product_manager.get_all_discount_info(time_bomb_id, cn_header)

            if product['id'] in discount_map:
                discount_info = discount_map[product['id']]
                add_discount_information(product, discount_info)

        # Expert review
        expert_review = review_manager.get_expert_review(target_db, product['menu']['id'])
        result.set('expert_review', expert_review)

        # Review articles
        # reviews = review_manager.get_product_review(language_info[2], product_id)
        result.set('total_count', 0)
        result.set('page_size', 0)
        result.set('customer_reviews', [])

        return Response(result.get_response(), status=result.get_code())


class ProductValidation(APIView):
    """
    product quantity check
    """
    SUCCESS_MSG = 'success'

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS_MSG)

        language_info = header_parser.parse_language(request.META)
        cn_header = language_info[0]
        target_db = language_info[1]

        result_list = list()
        result_product_list = list()

        try:
            request_data = request.data
            os_type = request_data.get('os_type', 0)
            hub_id = request_data.get('hub_id', 1)
            product_list = request.data['product_list']
            delivery_schedule = request.data['delivery_schedule']
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        first_product = True
        product_order_name = ''
        sales_time = 0

        # Time bomb service
        product_service = ProductService(logger_info, logger_error)
        time_bomb_service = TimeBombService(logger_info, logger_error)

        time_bomb_id = time_bomb_service.get_current_time_bomb_id(hub_id, os_type)
        discount_info = {}

        if time_bomb_id is not None:
            discount_list = product_service.read_product_discount_info_with_id(time_bomb_id)
            discount_info.update(get_discount_info_map(discount_list, cn_header))

        for product in product_list:
            try:
                product_instance = Product.objects.get(id=product['product_id'])
                menu_instance = Menu.objects.using(target_db).get(id=product_instance.menu.id)
                hub_stock = HubStock.objects.get(hub=product_instance.hub, menu=menu_instance)

                # Check sales_time
                sales_time = product_instance.sales_time

                # Check real stock unit
                order_quantity = product['quantity']
                stock = hub_stock.stock

                if stock < order_quantity:
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Product already sold')
                    error_code = code.ERROR_3001_PRODUCT_ALREADY_SOLD
                    result.set_error(error_code)
                    error_message = get_msg(error_code, cn_header)
                    error_message += ' [' + menu_instance.name + ']'
                    result.set_error_message(error_message)
                    return Response(result.get_response(), result.get_code())

                # Check schedule time
                if not check_delivery_schedule(delivery_schedule):
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Schedule invalid')
                    error_code = code.ERROR_3015_PRODUCT_DELIVERY_TIME_INVALID
                    error_message = get_msg(error_code, cn_header)
                    result.set_error(error_code)
                    result.set_error_message(error_message)
                    return Response(result.get_response(), result.get_code())

                # Product information
                product_serializer = ProductListInfoSerializer(product_instance)
                product_data = product_serializer.data

                menu_serializer = MenuValidationSerializer(menu_instance)
                menu_data = menu_serializer.data

                product_data['menu'] = menu_data
                product_data['quantity'] = product['quantity']

                # Add time bomb information
                if product_data['id'] in discount_info:
                    add_discount_information(product_data, discount_info[product_data['id']])

                result_product_list.append(product_data)

                if first_product:
                    product_order_name = product_instance.menu.name
                    # product_order_name = menu_instance.name
                    first_product = False

                logger_info.info(str(stock) + ' ' + str(product['quantity']))

                if stock >= product['quantity']:
                    result_list.append(product['product_id'])

            except Exception as e:
                print(e)

        result.set('product_title', product_order_name)
        # Check if result list is zero, don't display more
        if int(len(result_list)-1) != 0:
            result.set('product_sub', '(and ' + str(len(result_list)-1) + ' more)')
        else:
            result.set('product_sub', '')

        result.set('sales_time', sales_time)
        result.set('product_count', len(result_list))
        result.set('product_index_list', result_list)
        result.set('product_list', result_product_list)

        return Response(result.get_response(), result.get_code())
