import requests

from aries.common import urlmapper
from aries.common.exceptions.exceptions import DataValidationError


def request_validation(request_data):
    if 'open_id' not in request_data:
        raise DataValidationError('Request data invalid', None)


def get_referral_result(purchase_target, open_id, share_id):
    return {'purchase_target': purchase_target, 'referrer_open_id': open_id, 'referrer_share_id': share_id}


def referral_sign_up_push(message):
    payload = {
        'code': 200, 'message': 'success', 'type': 1,
        'title': message
    }
    url = urlmapper.get_url('HUB_MESSAGE_ANDROID')
    response = requests.post(url, json=payload)
