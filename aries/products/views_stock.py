import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.code_msg import get_msg
from aries.common.models import ResultResponse
from aries.products.models import Product, HubStock

logger_info = logging.getLogger('products_info')
logger_error = logging.getLogger('products_error')


class ProductStock(APIView):
    """
    type 0 is sold
    type 1 is refund
    """
    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data

        try:
            trade_type = request_data['trade_type']
            product_list = request_data['product_list']
            validate_str = request_data['validate_str']
            if validate_str != 'GoDbAcKeNdS':
                result = ResultResponse(code.ARIES_401_UNAUTHORIZED, get_msg(code.ARIES_401_UNAUTHORIZED))
                return Response(result.get_response(), result.get_code())
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, get_msg(code.ARIES_401_UNAUTHORIZED))
            return Response(result.get_response(), result.get_code())

        try:
            sales_status = 1

            for product_item in product_list:
                product_id = product_item['product_id']
                quantity = product_item['quantity']

                product = Product.objects.get(id=product_id)
                menu = product.menu
                hub = product.hub

                product_stock = HubStock.objects.get(hub=hub, menu=menu)

                stock_count = product_stock.stock
                sold_count = product_stock.sold

                if trade_type == 0:
                    stock_count -= quantity
                    sold_count += quantity
                else:
                    stock_count += quantity
                    sold_count -= quantity

                if sold_count <= 0:
                    sold_count = 0

                if stock_count <= 0:
                    stock_count = 0

                    products = Product.objects.filter(hub=hub, menu=menu, status__lte=sales_status)

                    for sold_product in products:
                        sold_product_instance = Product.objects.get(id=sold_product.id)
                        sold_product_instance.status = 0
                        sold_product_instance.save()

                if stock_count >= 1:
                    product_status = product.status

                    if product_status == 0:
                        product.status = sales_status
                        product.save()

                product_stock.stock = stock_count
                product_stock.sold = sold_count
                product_stock.save()

            return Response(result.get_response(), result.get_code())
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())
