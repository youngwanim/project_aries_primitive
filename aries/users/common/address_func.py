from aries.common.exceptions.exceptions import AuthInfoError, DataValidationError


def address_req_validation(open_id, access_token):
    if open_id is None or access_token is None:
        raise AuthInfoError


def address_create_data_check(request_data):
    if 'name' not in request_data or 'hub_id' not in request_data:
        raise DataValidationError('Request data invalid', None)

    if 'latitude' not in request_data or 'longitude' not in request_data:
        raise DataValidationError('Request data invalid', None)

    if 'delivery_area' in request_data:
        if request_data['delivery_area']:
            request_data['selected_address'] = True
        else:
            request_data['selected_address'] = False
    else:
        request_data['delivery_area'] = False
        request_data['selected_address'] = False

    if 'has_pending' in request_data:
        if request_data['has_pending']:
            request_data['delivery_area'] = False
            request_data['selected_address'] = False

    # Defence logic for field empty
    if 'format_address' not in request_data:
        request_data['format_address'] = ''
    if 'city_code' not in request_data:
        request_data['city_code'] = ''

    if 'overwrite_user_name' not in request_data:
        request_data['overwrite_user_name'] = False


def get_pickup_hub(cn_header, hub_id):
    hub_address_en = [
        'None',
        'Via Stelle Western Kitchen - Room E101, No. 161, Lane 465 Zhenning Road (Yuyuanli Garden Office)',
        'Coming soon'
    ]

    hub_address_cn = [
        'None',
        'Via Stelle 西式厨房 -长宁区镇宁路465弄161号愚园里E101',
        'Coming soon'
    ]

    if cn_header:
        result = hub_address_cn[hub_id]
    else:
        result = hub_address_en[hub_id]

    return result


def address_select_validation(delivery_area):
    if not delivery_area:
        raise DataValidationError('Request data invalid', None)
