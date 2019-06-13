import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import product_util
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.products.manager.product_manager import ProductManager
from aries.products.manager.review_manager import ReviewManager
from aries.products.models import MenuReviewStatics


logger_info = logging.getLogger('products_info')
logger_error = logging.getLogger('products_error')


class ReviewStaticsDetail(APIView):

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data

        try:
            menu_id = request_data['menu_id']
            menu_rate = request_data['menu_rate']
            menu_prev_rate = request_data['menu_prev_rate']
            has_reviewed = request_data['has_reviewed']
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        review_manager = ReviewManager(logger_info, logger_error)
        if not review_manager.create_review(menu_id, menu_rate, menu_prev_rate, has_reviewed):
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Object data not found')

        return Response(result.get_response(), result.get_code())

    def put(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data

        try:
            menu_id = request_data['menu_id']
            menu_rate = request_data['menu_rate']
            prev_rate = request_data['prev_rate']
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        review_manager = ReviewManager(logger_info, logger_error)
        if not review_manager.update_review(menu_id, menu_rate, prev_rate):
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Object data not found')

        return Response(result.get_response(), result.get_code())

    def delete(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data
        logger_info.info(request_data)

        # Parsing request parameter
        try:
            menu_id = request_data['menu_id']
            prev_rate = request_data['prev_rate']
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Get a object
        try:
            menu_statics = MenuReviewStatics.objects.get(menu=menu_id)

            # Calculate rate
            original_rate = menu_statics.review_count * menu_statics.average_point
            original_rate -= prev_rate
            new_rate = round(original_rate/(menu_statics.review_count-1), 1)

            # Save data
            menu_statics.review_count -= 1
            menu_statics.average_point = new_rate
            menu_statics.save()
            return Response(result.get_response(), result.get_code())
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Object data not found')
            return Response(result.get_response(), result.get_code())


class PastOrderReview(APIView):

    DEFAULT_HUB_ID = 1
    MENU_TYPE_THRESH_HOLDER = 10
    MENU_TYPE_SET = 0

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data

        try:
            open_id = request_data['open_id']
            product_list = request_data['product_list']
            order_id = request_data['order_id']
            hub_id = request_data['hub_id']
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid(Token or Open id)')
            return Response(result.get_response(), result.get_code())

        language_info = header_parser.parse_language(request.META)
        date_info = product_util.get_date_information(hub_id, product_util.get_sales_time_str())

        product_manager = ProductManager(logger_info, logger_error, language_info, date_info)
        review_manager = ReviewManager(logger_info, logger_error)

        product_list = [product_manager.get_product(product['product_id']) for product in product_list]
        response_list = [review_manager.get_personal_review(language_info[2], open_id, order_id, product)
                         for product in product_list]

        result.set('reviews', response_list)
        result.set('review_items', review_manager.review_items)

        return Response(result.get_response(), result.get_code())
