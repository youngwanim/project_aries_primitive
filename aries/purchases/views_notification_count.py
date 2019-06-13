import logging

from datetime import date

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.models import ResultResponse
from aries.purchases.models import CustomerCoupon, Order


logger_info = logging.getLogger('purchases_info')
logger_error = logging.getLogger('purchases_error')


class NotificationCount(APIView):

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        # Request data parsing
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            logger_info.info(open_id + ':' + access_token)
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid(Token or Open id)')
            return Response(result.get_response(), result.get_code())

        # Get usable coupon count and upcoming order count
        try:
            today = date.today()

            coupon_count = CustomerCoupon.objects.filter(
                open_id=open_id,
                status=0,
                end_date__gte=today
            ).count()

            upcoming_order_count = Order.objects.filter(
                open_id=open_id,
                order_status__lt=3
            ).count()

            result.set('coupon_count', coupon_count)
            result.set('upcoming_order_count', upcoming_order_count)
            return Response(result.get_response(), result.get_code())
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
            return Response(result.get_response(), result.get_code())
