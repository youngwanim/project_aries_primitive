import requests

from aries.common import urlmapper


def get_time_bomb_info_from_menu(hub_id, accept_lang, os_type):
    url = urlmapper.get_url('TIME_BOMB_INFO').format(str(hub_id))
    headers = {'Accept-Language': accept_lang, 'os-type': str(os_type)}

    result = None

    try:
        response = requests.get(url, headers=headers, timeout=2)
    except Exception as e:
        print(e)
    else:
        if response.status_code == 200:
            result = response.json()

    return result
