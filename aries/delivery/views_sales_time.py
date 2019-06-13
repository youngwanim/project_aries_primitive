import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code, product_util
from aries.common.models import ResultResponse

logger_info = logging.getLogger('purchases_info')
logger_error = logging.getLogger('purchases_error')


class ProductSalesTime(APIView):
    """
    Product sales time API class
    """
    result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

    def get(self, request):
        logger_info.info('[views_sales_time][ProductSalesTime][GET][{}]'.format(request.META.get('REMOTE_ADDR', '')))

        sales_time = product_util.get_sales_time_str()
        self.result.set('sales_time', sales_time)

        return Response(self.result.get_response(), self.result.get_code())
