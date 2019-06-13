import requests

from aries.common import urlmapper, code
from aries.common.exceptions.exceptions import DataValidationError


def get_sp_inst_template(cn_header):
    inst_template_en = [
        'Container recycle pickup',
        'Please leave the food at the door',
        'Please leave the food at the reception',
    ]

    inst_template_cn = [
        '请回收餐盒',
        '请放在门口',
        '请放在前台',
    ]

    if cn_header:
        result = inst_template_cn
    else:
        result = inst_template_en

    return result


def get_check_sp_instruction(sp_inst):
    result = False

    if sp_inst == 'Please leave the food at the door':
        result = True
    elif sp_inst == 'Please leave the food at the reception':
        result = True
    elif sp_inst == 'Container recycle pickup':
        result = True
    elif sp_inst == '请放在门口':
        result = True
    elif sp_inst == '请放在前台':
        result = True
    elif sp_inst == '请回收餐盒':
        result = True
    elif len(sp_inst) <= 0:
        result = True

    return result


def get_delivery_time(default_hub_id, accept_lang):
    url = urlmapper.get_time_table_url_v2(default_hub_id)
    headers = {'Content-Type': 'application/json', 'Accept-Language': accept_lang}
    response = requests.get(url, headers=headers)

    if response.status_code == code.ARIES_200_SUCCESS:
        response_json = response.json()
        working_day = response_json['working_day']
        timetable = response_json['timetable']
        order_available = response_json['order_available']
        minimum_order_price = response_json['minimum_order_price']
        order_unavailable_message = response_json['order_unavailable_message']
    else:
        working_day = ''
        timetable = []
        order_available = False
        minimum_order_price = 0
        order_unavailable_message = ''

    delivery_time_map = {
        'working_day': working_day,
        'timetable': timetable,
        'order_available': order_available,
        'minimum_order_price': minimum_order_price,
        'order_unavailable_message': order_unavailable_message
    }

    return delivery_time_map


def get_purchases_data(open_id, access_token, accept_lang):
    headers = {'open-id': str(open_id), 'Content-Type': 'application/json', 'Accept-Language': accept_lang,
               'Authorization': 'bearer ' + access_token}
    response = requests.get(urlmapper.get_url('COUPON_LIST'), headers=headers)

    if response.status_code == code.ARIES_200_SUCCESS:
        response_json = response.json()
        coupon_json = response_json['coupons']
        primary_json = response_json['primary_coupons']
        additional_json = response_json['additional_coupons']
    else:
        coupon_json = []
        primary_json = []
        additional_json = []

    purchase_map = {
        'coupons': coupon_json,
        'primary_coupons': primary_json,
        'additional_coupons': additional_json
    }

    return purchase_map


def get_recommend_product(default_hub_id, accept_lang):
    headers = {'Accept-Language': accept_lang}
    recommend_url = urlmapper.get_recommend_url_v2(default_hub_id)
    response = requests.get(recommend_url, headers=headers)

    if response.status_code == code.ARIES_200_SUCCESS:
        response_json = response.json()
        result = response_json['products']
    else:
        result = []

    return result


def cart_inst_validation(request_data):
    if 'special_instruction' not in request_data:
        raise DataValidationError('Request data invalid', None)


def get_user_inst_list(cn_header, inst_list):
    if cn_header:
        prefix_str = '(个人) '
    else:
        prefix_str = '(PERSONAL) '

    updated_list = [prefix_str + item for item in inst_list]

    return updated_list


def cut_user_inst_template(special_instruction):
    prefix_str_en = '(PERSONAL) '
    prefix_str_cn = '(个人) '

    if special_instruction.startswith(prefix_str_en):
        special_instruction.replace(prefix_str_en, '')
    elif special_instruction.startswith(prefix_str_cn):
        special_instruction.replace(prefix_str_cn, '')

    return special_instruction
