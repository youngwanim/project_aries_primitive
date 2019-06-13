import datetime
import json
import time
from collections import namedtuple

from dateutil.relativedelta import relativedelta

HUB_SET = (1, 2)
DEFAULT_HUB_ID = 1

STATE_LABEL_0_EN = 'SOLD OUT'
STATE_LABEL_0_CN = '已售完'
STATE_LABEL_1_EN = 'ADD TO BAG'
STATE_LABEL_1_CN = '加入购物袋'
# STATE_LABEL_1_EN = 'ORDER FOR '
# STATE_LABEL_1_CN = '订购'
STATE_LABEL_2_EN = 'AFTER 3PM'
STATE_LABEL_2_CN = '3点以后'
STATE_LABEL_3_EN = 'LUNCH UNTIL 3PM'
STATE_LABEL_3_CN = '午餐到3点钟'
STATE_LABEL_4_EN = 'COMING SOON'
STATE_LABEL_4_CN = '敬请期待'
STATE_LABEL_5_EN = 'TEMP'

ALL_TIME_INDEX = (22, 42)
MORNING_TIME_INDEX = (22, 42)
LUNCH_TIME_INDEX = (22, 42)
DINNER_TIME_INDEX = (30, 42)

TIME_TYPE_LIST = [ALL_TIME_INDEX, MORNING_TIME_INDEX, LUNCH_TIME_INDEX, DINNER_TIME_INDEX]
TIME_TYPE_MAP = {'all_day': 0, 'morning': 1, 'lunch': 2, 'dinner': 3}
TIME_TYPE_STRING = ['ALL DAY ', 'MORNING ', 'LUNCH', 'DINNER']
TIME_TYPE_STRING_CN = ['終日 ', '朝餐 ', '午餐下单', '晚餐下单']

SALES_TIME_QUERY = ['sales_time=all_day', 'sales_time=morning', 'sales_time=lunch', 'sales_time=dinner']

TYPE_NAME = ['Set menu', 'Main', 'Side', 'Dessert', 'FRUIT DRINKS',
             'Wine', 'Salad', 'Chop Salad', 'Subscription', '', 'Event']
TYPE_NAME_CN = ['套餐', '主菜', '配菜', '甜品', '新鲜果饮', '葡萄酒', '沙拉', '鲜切沙拉', '沙拉计划', '', '沙拉']

TYPE_INDEX = [10, 2, 10, 3, 4,
              5, 10, 0, 1, 10, 10]


def get_type_name(index, cn_header):
    if cn_header:
        return TYPE_NAME_CN[index]
    else:
        return TYPE_NAME[index]


def get_product_state_label(is_cn_header, status):
    if status == 0:
        current_date = datetime.datetime.today()
        start_date = datetime.datetime(2019, 1, 30, 16, 0)
        end_date = datetime.datetime(2019, 1, 30, 16, 30)

        if start_date < current_date < end_date:
            if is_cn_header:
                return '2月11日起可下单'
            else:
                return 'Back on 2/11'
        else:
            if is_cn_header:
                return STATE_LABEL_0_CN
            else:
                return STATE_LABEL_0_EN
    elif status == 1:
        if is_cn_header:
            return STATE_LABEL_1_CN
        else:
            return STATE_LABEL_1_EN
    elif status == 2:
        if is_cn_header:
            return STATE_LABEL_2_CN
        else:
            return STATE_LABEL_2_EN
    elif status == 3:
        if is_cn_header:
            return STATE_LABEL_3_CN
        else:
            return STATE_LABEL_3_EN
    else:
        if is_cn_header:
            return STATE_LABEL_4_CN
        else:
            return STATE_LABEL_4_EN


def get_lunch_time():
    today = time.localtime()

    if today[3] >= 21:
        return True

    if today[3] < 15:
        return True
    else:
        return False


def get_sales_time():
    lunch = 2
    dinner = 3

    today = time.localtime()

    if today[3] >= 21:
        return lunch

    if today[3] < 15:
        return lunch
    else:
        return dinner


def get_sales_time_str():
    lunch = 'lunch'
    dinner = 'dinner'

    today = time.localtime()

    if today[3] >= 21:
        return lunch

    if today[3] < 15:
        return lunch
    else:
        return dinner


def get_available_time(current_time):
    today = time.localtime()

    if current_time == 2:
        if today[3] >= 21:
            return True

        if today[3] < 15:
            return True
        else:
            return False
    else:
        return True


def get_sales_time_to_str(current_time):
    if current_time == 2:
        return 'lunch'
    elif current_time == 3:
        return 'dinner'
    else:
        return 'dinner'


def get_sales_str_to_time(current_time):
    if current_time == 'lunch':
        return 2
    elif current_time == 'dinner':
        return 3
    else:
        return 3


def get_phase_next_day():
    today = time.localtime()

    if today[3] >= 21:
        return True
    else:
        return False


def get_selling_time_delivery_schedule(time_type, delivery_schedule):
    time_tuple = TIME_TYPE_LIST[time_type]

    if time_tuple[0] <= delivery_schedule <= time_tuple[1]:
        return True
    else:
        return False


def get_coupon_date(period_type, period_day, start_date, end_date):
    today = datetime.date.today()
    result = (today, end_date)

    if period_type == 1:
        next_date = today + datetime.timedelta(days=period_day)
        result = (today, next_date)
    elif period_type == 2:
        result = (start_date, end_date)
    return result


def get_date_information(hub_id, time_type):
    if int(hub_id) not in HUB_SET:
        hub_id = DEFAULT_HUB_ID

    if len(time_type) > 1:
        time_type = TIME_TYPE_MAP[time_type]
    else:
        time_type = int(time_type)

    current_date = datetime.date.today()
    phase_next_day = get_phase_next_day()

    if phase_next_day:
        current_date += datetime.timedelta(days=1)

    launch_time = get_lunch_time()

    result = (int(hub_id), time_type, phase_next_day, current_date, launch_time)
    return result


def get_date_information_v2(hub_id, time_type):
    if int(hub_id) not in HUB_SET:
        hub_id = DEFAULT_HUB_ID

    if len(time_type) > 1:
        time_type = TIME_TYPE_MAP[time_type]
    else:
        time_type = int(time_type)

    current_date = datetime.date.today()
    phase_next_day = get_phase_next_day()

    if phase_next_day:
        current_date += datetime.timedelta(days=1)

    lunch_time = get_lunch_time()

    DateInfo = namedtuple("DateInfo", 'hub_id time_type phase_next_day current_date lunch_time')
    return DateInfo(hub_id=int(hub_id), time_type=time_type, phase_next_day=phase_next_day,
                    current_date=current_date, lunch_time=lunch_time)


def get_date_information_v3(hub_id):
    if int(hub_id) not in HUB_SET:
        hub_id = DEFAULT_HUB_ID

    time_type = get_sales_time()

    current_date = datetime.date.today()
    phase_next_day = get_phase_next_day()

    if phase_next_day:
        current_date += datetime.timedelta(days=1)

    DateInfo = namedtuple("DateInfo", 'hub_id time_type phase_next_day current_date')
    return DateInfo(hub_id=int(hub_id), time_type=time_type, phase_next_day=phase_next_day, current_date=current_date)


def get_timetable_query(sales_time):
    return SALES_TIME_QUERY[sales_time]


def get_badge(cn_header, badge_en, badge_cn):
    if cn_header:
        return json.loads(badge_cn)
    else:
        return json.loads(badge_en)


def get_delivery_schedule_str(delivery_schedule):
    standard_time = datetime.datetime(1, 1, 1, 0, 0)
    target_time = standard_time + datetime.timedelta(minutes=(30*delivery_schedule))
    end_time = target_time + datetime.timedelta(minutes=60)
    return str(target_time)[-8:-3] + '~' + str(end_time)[-8:-3]


def get_month_schedule(year, month):
    start_date = datetime.datetime(int(year), int(month), 1, 0, 0)
    start_date_str = str(start_date)[:10]
    end_date = start_date + relativedelta(months=1) - relativedelta(days=1)
    end_date_str = str(end_date)[:10]
    result = (start_date_str, end_date_str)
    return result
