import requests

from aries.common import code, urlmapper
from aries.common.exceptions.exceptions import BusinessLogicError, AuthInfoError, DataValidationError
from aries.purchases.serializers import PurchaseOrderRequestSerializer


def request_user_validation(open_id, access_token):
    payload = {'open_id': open_id, 'access_token': access_token}
    response = requests.post(urlmapper.get_url('USER_VALIDATION'), json=payload)
    return False if response.status_code != code.ARIES_200_SUCCESS else True


def request_purchase_validation(hub_id, accept_lang, product_list, delivery_schedule, os_type):
    headers = {'accept-language': accept_lang, 'os-type': str(os_type)}
    payload = {'product_list': product_list}
    purchase_url = urlmapper.get_purchase_validation_v2(hub_id, int(delivery_schedule))
    response = requests.post(url=purchase_url, headers=headers, json=payload)

    if response.status_code != code.ARIES_200_SUCCESS:
        raise BusinessLogicError('Internal server error', None, None)

    return response.json()


def request_validation(open_id, access_token, request_data):
    if open_id is None or access_token is None:
        raise AuthInfoError

    if 'hub_id' in request_data:
        if request_data['hub_id'] == 0:
            request_data['hub_id'] = 1

    serializer = PurchaseOrderRequestSerializer(data=request_data)

    if not serializer.is_valid():
        raise DataValidationError('Request data invalid', None)

    if 'product_list' not in request_data \
            or 'coupon_list' not in request_data \
            or 'delivery_date' not in request_data:
        raise DataValidationError('Request data invalid', None)

    if not request_user_validation(open_id, access_token):
        raise AuthInfoError

    request_data['open_id'] = open_id


def purchase_validation(accept_lang, request_data, os_type):
    hub_id = request_data['hub_id']
    product_list_json = request_data['product_list']
    delivery_schedule = request_data['delivery_schedule']

    return request_purchase_validation(hub_id, accept_lang, product_list_json, delivery_schedule, os_type)
