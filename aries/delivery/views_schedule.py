import datetime
import json

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.code_msg import get_msg
from aries.common.models import ResultResponse
from aries.common.http_utils import header_parser

from .models import DeliverySchedule, ShippingAvailability, ShippingMethod
from .serializers import ShippingMethodListSerializer


# response of this function is like the followings:
#  # {"working_day": "2017-03-04", 
#  time_slots : [ 
#   {"index": 2, "starttime": "07:00 PM", "endtime":"08:00 PM"},
#   {"index": 3, "interval": "20:00-21:00"},
#   {"index": 4, "interval": "21:00-22:00"},  
#


class DeliveryTargetSchedule(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeliveryTargetSchedule, self).dispatch(request, *args, **kwargs)

    def get(self, request, hub_id):
        # Query the DeliverySchedule DB 
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        language_info = header_parser.parse_language(request.META)
        target_db = language_info[1]

        sales_time = 'ALL_DAY'
        if request.query_params.get('sales_time'):
            sales_time = request.query_params.get('sales_time').upper()

        today = datetime.datetime.today()
        next_working_day = today + datetime.timedelta(days=30)
        try:
            dlv_schedules = DeliverySchedule.objects.filter(working_day__range=[today, next_working_day])

            if dlv_schedules.count() <= 0:
                result.set('timetable', json.loads('[]'))
            else:
                target_schedule = dlv_schedules[0]
                delivery_day = today

                if delivery_day.time() > dlv_schedules[0].delivery_end:
                    if dlv_schedules.count() > 1:
                        target_schedule = dlv_schedules[1]
                        next_day = target_schedule.working_day
                    else:
                        target_schedule = dlv_schedules[0]
                        next_day = today + datetime.timedelta(days=1)
                else:
                    next_day = today

                if sales_time == 'LUNCH':
                    time_table = target_schedule.delivery_time_table_lunch
                elif sales_time == 'DINNER':
                    time_table = target_schedule.delivery_time_table_dinner
                else:
                    time_table = target_schedule.delivery_time_table

                time_slots = json.loads(time_table)
                result.set('working_day', next_day.strftime('%Y.%m.%d'))
                available_time = 0
                matched_index = []

                for target_slot in time_slots:
                    time = datetime.datetime.strptime(
                        next_day.strftime("%Y.%m.%d") + ' ' + target_slot["starttime"], "%Y.%m.%d %I:%M %p"
                    )

                    if today > time:
                        available_time += 1
                    else:
                        matched_index.append(target_slot['index'])

                try:
                    shipping_avail = ShippingAvailability.objects.get(hub_id=hub_id, ds_id=target_schedule)
                except ShippingAvailability.DoesNotExist:
                    shipping_avail = ShippingAvailability(hub_id=hub_id, ds_id=target_schedule)
                    shipping_avail.save()

                time_slots_avail = json.loads(shipping_avail.shipping_availability_table)
                result_list = [target_time for slot in matched_index for target_time in time_slots_avail
                               if slot == target_time['index']]

                if sales_time == 'LUNCH':
                    result_table = result_list
                elif sales_time == 'DINNER':
                    result_table = result_list
                else:
                    result_table = time_slots_avail[available_time:]

                result.set('timetable', result_table)
        except DeliverySchedule.DoesNotExist:
            today = datetime.datetime.today()
            today = today + datetime.timedelta(1)
            result.set('timetable', json.loads('[]'))
            result.set('working_day', today.strftime("%Y.%m.%d"))
            result.set('shipping_detail', json.loads('[]'))
            return Response(result.get_response(), result.get_code())

        try:
            shipping_methods = ShippingMethod.objects.using(target_db).filter(hub_id=hub_id)
            shipping_method_list = ShippingMethodListSerializer(shipping_methods, many=True).data
            result.set('shipping_detail', shipping_method_list)
        except ShippingMethod.DoesNotExist:
            print("ShippingMethod is not defined for hub id: {0}".format(hub_id))
            result.set('shipping_detail', json.loads('[]'))
        except Exception as e:
            print(e)
            result.set('shipping_detail', json.loads('[]'))

        return Response(result.get_response(), result.get_code())


class DeliveryTargetScheduleDetail(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeliveryTargetScheduleDetail, self).dispatch(request, *args, **kwargs)

    def get(self, request, hub_id, date, table_id, shipping_type):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        target_db = 'default'
        if request.META.get('HTTP_ACCEPT_LANGUAGE'):
            accept_lang = request.META['HTTP_ACCEPT_LANGUAGE']
            if 'zh' in accept_lang:
                target_db = 'aries_cn'

        try:
            shipping_methods = ShippingMethod.objects.using(target_db).filter(hub_id=hub_id)
            shipping_method_list = ShippingMethodListSerializer(shipping_methods, many=True).data
            result.set('shipping_detail', shipping_method_list)
        except ShippingMethod.DoesNotExist:
            print("ShippingMethod is not defined for hub id: {0}".format(hub_id))
            error_code = code.ERROR_3012_NOT_SUPPORT_DELIVERY_METHOD
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, get_msg(error_code))
            result.set_error(code.ERROR_3012_NOT_SUPPORT_DELIVERY_METHOD)
            return Response(result.get_response(), result.get_code())
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
            result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)
            return Response(result.get_response(), result.get_code())

        # Default value
        dlv_schedules = ''

        try:
            # print(str(date))
            today = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            next_working_day = today + datetime.timedelta(days=30)

            dlv_schedules = DeliverySchedule.objects.filter(working_day__range=[today, next_working_day])
            shipping_avail = ShippingAvailability.objects.get(ds_id=dlv_schedules[0], hub_id=hub_id)
            time_slots_avail = json.loads(shipping_avail.shipping_availability_table)

            for target_slot in time_slots_avail:
                if str(target_slot['index']) == table_id:
                    for target_slot_avail in target_slot['shipping']:
                        if str(target_slot_avail['shipping_type']) == shipping_type:
                            result.set('availability', target_slot_avail['available'])
                            result.set('delivery_start_time', target_slot['starttime'])
                            result.set('delivery_end_time', target_slot['endtime'])
                            return Response(result.get_response(), result.get_code())

            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Invalid timetable index or shipping type')
            result.set_error(code.ERROR_3007_DELIVERY_SCHEDULE_INVALID)

        except DeliverySchedule.DoesNotExist:
            print("No delivery schedule is found for date at {0},hub {1}".format(str(date), str(hub_id)))
            error_code = code.ERROR_3011_NO_AVAILABLE_DELIVERY_SCHEDULE
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, get_msg(error_code))
            result.set_error(error_code)
            return Response(result.get_response(), result.get_code())
        except ShippingAvailability.DoesNotExist:
            print("No shipping schedule is found for ds_id-{0},hub {1}".format(str(dlv_schedules.id), str(hub_id)))
            error_code = code.ERROR_3011_NO_AVAILABLE_DELIVERY_SCHEDULE
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, get_msg(error_code))
            result.set_error(error_code)
            return Response(result.get_response(), result.get_code())
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
            result.set_error(code.ERROR_9000_INTERNAL_API_CALL_FAILED)

        return Response(result.get_response(), result.get_code())
