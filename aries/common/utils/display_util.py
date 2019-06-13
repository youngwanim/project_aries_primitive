import json
from datetime import datetime
from math import ceil


def week_of_month(dt):
    return int(ceil(dt.day + dt.weekday()/7.0))


def display_check(display_object):
    if display_object['has_week_schedule']:
        today = datetime.today()
        week_no = week_of_month(today)
        week_schedule_list = json.loads(display_object['week_schedule'])
        if week_no not in week_schedule_list:
            return False

    if display_object['has_day_schedule']:
        day_of_week = datetime.today().weekday()
        day_schedule_list = json.loads(display_object['day_schedule'])
        if day_of_week not in day_schedule_list:
            return False

    if display_object['has_time_schedule']:
        today = datetime.today()
        delivery_index = today.hour*2

        if 22 <= delivery_index <= 42:
            time_schedule_list = json.loads(display_object['time_schedule'])

            time_index_result = False

            for time_schedule in time_schedule_list:
                start_index = int(time_schedule['start_index'])
                end_index = int(time_schedule['end_index'])

                if start_index <= delivery_index <= end_index:
                    time_index_result = True
                    break

            if not time_index_result:
                return False

    return True
