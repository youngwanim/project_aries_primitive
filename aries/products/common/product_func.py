import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from aries.common import product_util


def parse_category(product, cn_header):
    product['price_discount_schedule'] = json.loads(product['price_discount_schedule'])
    product['category'] = json.loads(product['category'])
    product['badge'] = product_util.get_badge(cn_header, product['badge_en'], product['badge_cn'])

    del product['badge_en']
    del product['badge_cn']
    del product['has_sales_schedule']
    del product['sales_schedule']
    return product


def parse_menu_data(menu_data):
    menu_data['description'] = json.loads(menu_data['description'])
    menu_data['prep_tips'] = json.loads(menu_data['prep_tips'])
    menu_data['ingredients'] = json.loads(menu_data['ingredients'])
    menu_data['nutrition'] = json.loads(menu_data['nutrition'])
    menu_data['notices'] = json.loads(menu_data['notices'])
    menu_data['subs_contents'] = json.loads(menu_data['subs_contents'])
    menu_data['media_contents'] = json.loads(menu_data['media_contents'])

    menu_list = json.loads(menu_data['image_detail'])
    menu_data['image_detail'] = menu_list[0]
    menu_data['image_detail_list'] = menu_list

    return menu_data


def parse_description_msg(desc_type, cn_header):
    lunch_only = 0
    dinner_only = 1
    subscription = 2
    event_prod = 3

    if desc_type == lunch_only:
        if cn_header:
            result = ''
        else:
            result = ''
    elif desc_type == dinner_only:
        if cn_header:
            result = '此菜品仅限于晚餐时间（4PM-10PM）'
        else:
            result = 'This item is available only for dinner time (4PM-10PM)'
    elif desc_type == subscription:
        if cn_header:
            result = ''
        else:
            result = ''
    elif desc_type == event_prod:
        if cn_header:
            result = ''
        else:
            result = ''
    else:
        result = ''

    return result


def parse_sales_time_limit(sales_time, cn_header):
    dinner = 3

    if sales_time == dinner:
        if cn_header:
            result = 'DINNER ONLY'
        else:
            result = 'DINNER ONLY'
    else:
        result = ''

    return result


def parse_sales_time_limit_status(sales_time):
    dinner = 3
    dinner_only = 7

    if sales_time == dinner:
        result = dinner_only
    else:
        result = 0

    return result


def parse_product_misc(product, cn_header):
    # Add type description
    product['type_name'] = product_util.get_type_name(product['type'], cn_header)
    product['type_index'] = product_util.TYPE_INDEX[product['type']]

    # Add status label
    product['status_label'] = product_util.get_product_state_label(cn_header, product['status'])

    # Check description type and description
    if product['has_description']:
        desc_type = product['description_type']
        product['description'] = parse_description_msg(desc_type, cn_header)


def check_delivery_schedule(delivery_schedule):
    today = datetime.today()
    current_index = today.hour * 2

    if today.hour >= 21:
        return True

    if today.minute > 30:
        current_index += 1

    result = True
    if delivery_schedule < current_index < 43:
        result = False

    return result


def parse_menu_information(menu_manager, product, target_db, cn_header):
    menu_id = product['menu']
    menu_data = menu_manager.get_menu_data(product, target_db, cn_header)

    menu_data['review_statics'] = menu_manager.get_menu_statics(menu_id)

    product['menu'] = menu_data

    # Add type description
    product['type_name'] = product_util.get_type_name(product['type'], cn_header)
    product['type_index'] = product_util.TYPE_INDEX[product['type']]

    product['status_label'] = product_util.get_product_state_label(cn_header, product['status'])

    # Check description type and description
    if product['has_description']:
        desc_type = product['description_type']
        product['description'] = parse_description_msg(desc_type, cn_header)


def parse_restaurant_information(restaurant_manager, menu, target_db):
    restaurant_id = menu['restaurant']
    menu['restaurant'] = restaurant_manager.get_restaurant_data(restaurant_id, target_db)


def add_discount_information(product, discount_info):
    discount_type = discount_info['discount_type']
    discount_rate = discount_info['discount_rate']
    discount_desc = discount_info['discount_desc']
    event_product = discount_info['set_event_product']

    original_price = product['price']
    discount_percent = discount_rate / 100
    exp = Decimal('.00')
    price_decimal = Decimal(original_price * discount_percent)
    price_discount = float(price_decimal.quantize(exp, rounding=ROUND_HALF_UP))

    time_bomb_info = {
        'discount_type': discount_type,
        'discount_rate': discount_rate,
        'discount_desc': discount_desc
    }

    if 'has_stock' in discount_info:
        time_bomb_info['has_stock'] = discount_info['has_stock']
    else:
        time_bomb_info['has_stock'] = False

    if 'stock' in discount_info:
        time_bomb_info['stock'] = discount_info['stock']
    else:
        time_bomb_info['stock'] = 0

    product['price_discount_event'] = True
    product['price_discount'] = original_price - price_discount
    product['event_product'] = event_product
    product['time_bomb_info'] = time_bomb_info
    product['badge'] = []


def get_discount_info_map(discount_list, cn_header):
    discount_map = {}
    for discount in discount_list:
        discount_map[discount['product_id']] = {
            'discount_type': discount['discount_type'],
            'discount_rate': discount['discount_rate'],
            'discount_desc': discount['discount_desc_cn'] if cn_header else discount['discount_desc_en'],
            'set_event_product': discount['set_event_product'],
        }

    return discount_map
