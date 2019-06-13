import requests

from aries.common import urlmapper


def update_coupon_count(logger_info, logger_error, open_id, access_token, op, count):
    logger_info.info('[EventManager][increase_coupon_count][' + open_id + '][' + access_token + ']')
    url = urlmapper.get_url('USER_NOTIFICATION_UPDATE').format('coupon', str(op), str(count))
    headers = {'open-id': open_id, 'Authorization': 'bearer ' + access_token}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        result = True
    else:
        logger_error.error(response.text)
        result = False

    return result


def update_coupon_count_no_log(open_id, access_token, op, count):
    url = urlmapper.get_url('USER_NOTIFICATION_UPDATE').format('coupon', str(op), str(count))
    headers = {'open-id': open_id, 'Authorization': 'bearer ' + access_token}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        result = True
    else:
        result = False

    return result
