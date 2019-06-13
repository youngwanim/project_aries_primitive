import datetime
import json

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse

from .models import DeliverySchedule


class DeliveryTimeTable(APIView):
    SUCCESS_MSG = 'success'

    def get(self, request, hub_id):
        lang_info = parse_language_v2(request.META)
        today = datetime.datetime.today()

        try:
            # Latest schedule
            target_schedule = DeliverySchedule.objects.filter(hub_id=int(hub_id)).latest('-id')
            delivery_day = today

            # After 9:00 pm, next day setting
            if delivery_day.time() > target_schedule.delivery_end:
                next_day = today + datetime.timedelta(days=1)
            else:
                next_day = today

            time_slots = json.loads(target_schedule.delivery_time_table)

            available_time = 0
            matched_table = []

            for target_slot in time_slots:
                time = datetime.datetime.strptime(
                    next_day.strftime("%Y.%m.%d") + ' ' + target_slot["starttime"], "%Y.%m.%d %I:%M %p"
                )

                if today > time:
                    available_time += 1
                else:
                    table = {
                        'index': target_slot['index'], 'starttime': target_slot['starttime'],
                        'endtime': target_slot['endtime'], 'delivery_price': target_schedule.delivery_price
                    }
                    matched_table.append(table)

            minimum_order_price = target_schedule.minimum_order_price
            order_available = target_schedule.order_available

            if lang_info.cn_header:
                unavailable_msg = target_schedule.unavailable_msg_chn
            else:
                unavailable_msg = target_schedule.unavailable_msg_eng

            if not order_available:
                order_unavailable_msg = unavailable_msg
            else:
                order_unavailable_msg = ''

        except Exception as e:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS_MSG)
            result.set('working_day', next_day.strftime('%Y.%m.%d'))
            result.set('timetable', matched_table)
            result.set('order_available', order_available)
            result.set('minimum_order_price', minimum_order_price)
            result.set('order_unavailable_message', order_unavailable_msg)

        return Response(result.get_response(), result.get_code())
