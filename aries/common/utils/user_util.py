import requests

from aries.common import urlmapper, code
from aries.common.exceptions.exceptions import AuthInfoError


def get_user_agreement(agreement):
    if agreement.lower() == 'y':
        return True
    else:
        return False


def get_user_locale(locale):
    if locale.lower() == 'zh':
        return True
    else:
        return False


def check_auth_info(auth_info):
    if auth_info[0] is None or auth_info[1] is None:
        raise AuthInfoError('Authentication Failed')

    payload = {'open_id': auth_info[0], 'access_token': auth_info[1]}
    url = urlmapper.get_url('USER_VALIDATION')

    response = requests.post(url, json=payload)

    if response.status_code != code.ARIES_200_SUCCESS:
        raise AuthInfoError('Authentication Failed')


def check_auth_info_v2(open_id, access_token):
    if open_id is None or access_token is None:
        raise AuthInfoError('Authentication Failed')

    payload = {'open_id': open_id, 'access_token': access_token}
    url = urlmapper.get_url('USER_VALIDATION')

    response = requests.post(url, json=payload)

    if response.status_code != code.ARIES_200_SUCCESS:
        raise AuthInfoError('Authentication Failed')
