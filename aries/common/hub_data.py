HUB_001_ADDRESS_EN = 'Room E101, No. 161, Lane 465 Zhenning Road (Yuyuanli Garden Office)'
HUB_001_ADDRESS_CN = '长宁区镇宁路465弄161号愚园里E101'

HUB_001_NAME_EN = 'Via Stelle Western Kitchen'
HUB_001_NAME_CN = 'Via Stelle 西式厨房'

address_map_en = dict()
address_map_cn = dict()

address_name_map_en = dict()
address_name_map_cn = dict()

address_map_en[1] = HUB_001_ADDRESS_EN
address_map_cn[1] = HUB_001_ADDRESS_CN

address_name_map_en[1] = HUB_001_NAME_EN
address_name_map_cn[1] = HUB_001_NAME_CN


def get_hub_address(cn_header, hub_id):
    if cn_header:
        address = address_map_cn.get(hub_id, HUB_001_ADDRESS_CN)
    else:
        address = address_map_en.get(hub_id, HUB_001_ADDRESS_EN)
    return address


def get_hub_name(cn_header, hub_id):
    if cn_header:
        address = address_name_map_cn.get(hub_id, HUB_001_NAME_CN)
    else:
        address = address_name_map_en.get(hub_id, HUB_001_NAME_EN)
    return address


DELIVERY_TYPE_FIRST = '[DELIVERY] ViaStelle'
DELIVERY_TYPE_SECOND = '[DELIVERY] Regular'
# DELIVERY_TYPE_THIRD = '[On site pickup]'
DELIVERY_TYPE_THIRD = ''
DELIVERY_SERVICE_FIRST = 'ViaStelle Premium'
DELIVERY_SERVICE_SECOND = 'Regular'
DELIVERY_SERVICE_THIRD = 'On site pickup'

DELIVERY_TYPE_FIRST_CN = '[配送] ViaStelle高級'
DELIVERY_TYPE_SECOND_CN = '[配送] 普通'
# DELIVERY_TYPE_THIRD_CN = '[直接签收]'
DELIVERY_TYPE_THIRD_CN = ''
DELIVERY_SERVICE_FIRST_CN = 'ViaStelle普通'
DELIVERY_SERVICE_SECOND_CN = '普通'
DELIVERY_SERVICE_THIRD_CN = '直接签收'


def get_delivery_str(cn_header, delivery_type):
    if delivery_type == 0:
        if cn_header:
            delivery_str = DELIVERY_TYPE_FIRST_CN
        else:
            delivery_str = DELIVERY_TYPE_FIRST
    elif delivery_type == 1:
        if cn_header:
            delivery_str = DELIVERY_TYPE_SECOND_CN
        else:
            delivery_str = DELIVERY_TYPE_SECOND
    else:
        if cn_header:
            delivery_str = DELIVERY_TYPE_THIRD_CN
        else:
            delivery_str = DELIVERY_TYPE_THIRD
    return delivery_str


def get_delivery_service_str(cn_header, delivery_type):
    if delivery_type == 0:
        if cn_header:
            delivery_str = DELIVERY_SERVICE_FIRST_CN
        else:
            delivery_str = DELIVERY_SERVICE_FIRST
    elif delivery_type == 1:
        if cn_header:
            delivery_str = DELIVERY_SERVICE_SECOND_CN
        else:
            delivery_str = DELIVERY_SERVICE_SECOND
    else:
        if cn_header:
            delivery_str = DELIVERY_SERVICE_THIRD_CN
        else:
            delivery_str = DELIVERY_SERVICE_THIRD
    return delivery_str


delivery_cost = [10, 8, 0]


def get_shipping_cost(shipping_type):
    if shipping_type > 2:
        shipping_type = 0
    return delivery_cost[shipping_type]
