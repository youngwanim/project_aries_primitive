import requests

from aries.common import urlmapper


def request_member_promotion(open_id, promotion_type, accept_lang='zh'):
    url = urlmapper.get_url('SIGNUP_PROMOTION')

    headers = {'Content-Type': 'application/json', 'Accept-Language': accept_lang}
    body = {'open_id': open_id, 'promotion_type': promotion_type}

    response = requests.post(url, headers=headers, json=body)

    result = {'has_member_promotion': False, 'member_promotion': {}}

    if response.status_code == 200:
        res_json = response.json()
        result['has_member_promotion'] = res_json['has_member_promotion']
        result['member_promotion'] = res_json['member_promotion']

    return result


def request_share_id_validation(share_id):
    url = urlmapper.get_url('SHARE_ID_VALIDATION')
    body = {'share_id': share_id}

    response = requests.post(url, json=body)

    open_id = None

    if response.status_code == 200:
        res_json = response.json()
        open_id = res_json['open_id']

    return open_id
