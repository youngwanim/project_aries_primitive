import json

from aries.common import product_util


def parse_promotion_extra(target_detail):
    detail_json = json.loads(target_detail)
    if product_util.get_sales_time_str() == 'lunch':
        product_id = detail_json['lunch']
    else:
        product_id = detail_json['dinner']
    return product_id
