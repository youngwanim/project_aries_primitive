import requests

from aries.common import code
from aries.common import product_util
from aries.common import urlmapper
from aries.common.exceptions.exceptions import AuthInfoError


def get_time_table(hub_id, sales_time):
    query = product_util.get_timetable_query(sales_time)
    url = urlmapper.get_url('TIMETABLE_LIST') + '/' + str(hub_id) + '?' + query
    response = requests.get(url)

    if response.status_code == code.ARIES_200_SUCCESS:
        response_json = response.json()
        result = response_json['timetable']
    else:
        result = []
    return result


def read_upcoming_order(open_id, access_token):
    headers = {
        'open-id': open_id,
        'authorization': 'bearer ' + access_token
    }
    payload = {
        'has_upcoming_order': False
    }
    requests.put(urlmapper.get_url('USER_NOTIFICATION'), headers=headers, json=payload)


def get_review_item(headers, payload):
    response = requests.get(urlmapper.get_url('REVIEW_DATA'), headers=headers, params=payload)
    response_json = response.json()
    return response_json


def get_user_info(open_id, access_token, address_id):
    url = urlmapper.get_url('ADMIN_USER_INFO')
    headers = {'Authorization': 'bearer ' + access_token}
    payload = {'open_id': open_id, 'access_token': access_token, 'address_id': address_id}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == code.ARIES_200_SUCCESS:
        response_json = response.json()
        result = {
            'user': response_json['user'],
            'user_info': response_json['user_info'],
            'user_address': response_json['user_address']
        }
    else:
        result = {'user': '', 'user_info': '', 'user_address': ''}

    return result


def get_admin_token_validate(access_token):
    url = urlmapper.get_url('ADMIN_VALIDATE')
    payload = {'access_token': access_token}
    response = requests.post(url, json=payload)

    if response.status_code != code.ARIES_200_SUCCESS:
        result = False
    else:
        result = True

    return result


def get_admin_token_validate_v2(access_token):
    url = urlmapper.get_url('ADMIN_VALIDATE')
    payload = {'access_token': access_token}
    response = requests.post(url, json=payload)

    if response.status_code != code.ARIES_200_SUCCESS:
        raise AuthInfoError('Authentication error')


def get_recommend_products(accept_lang, hub_id, os_type):
    product_list = []

    headers = {'Accept-Language': accept_lang, 'os-type': str(os_type)}
    recommend_url = urlmapper.get_recommend_url_v2(hub_id)
    response = requests.get(recommend_url, headers=headers)

    if response.status_code == code.ARIES_200_SUCCESS:
        response_json = response.json()
        product_list = response_json['products']

    return product_list


def get_user_information(open_id, access_token):
    payload = {'open_id': open_id, 'access_token': access_token}
    url = urlmapper.get_url('USER_VALIDATION')

    response = requests.post(url, json=payload)

    if response.status_code == code.ARIES_200_SUCCESS:
        response_json = response.json()
        result = (True, response_json)
    else:
        result = (False, None)

    return result
