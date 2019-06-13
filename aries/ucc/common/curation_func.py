import requests

from aries.common import urlmapper
from aries.common.exceptions.exceptions import DataValidationError


def article_post_validation(request_data):
    if 'article' not in request_data:
        raise DataValidationError('Required parameter is not found', None)

    if 'content_en' not in request_data['article'] or 'content_cn' not in request_data['article']:
        raise DataValidationError('Required parameter is not found', None)


def create_article_validation(article, content_en, content_cn):
    if 'layout_type' not in article or 'action_type' not in article:
        raise DataValidationError('Request data invalid', None)

    if 'language_type' not in content_en or 'language_type' not in content_cn:
        raise DataValidationError('Request data invalid', None)


def page_post_validation(request_data):
    if 'curation_page' not in request_data:
        raise DataValidationError('Required parameter is not found', None)

    if 'content_en' not in request_data['curation_page'] or 'content_cn' not in request_data['curation_page']:
        raise DataValidationError('Required parameter is not found', None)


def page_list_update_post_validation(request_data):
    if 'curation_pages' not in request_data:
        raise DataValidationError('Required parameter is not found', None)

    page_list = request_data['curation_pages']

    for page in page_list:
        if 'status' not in page or 'id' not in page or 'list_index' not in page:
            raise DataValidationError('Required parameter is not found', None)


def get_article_validation(article_id):
    if article_id == 0:
        raise DataValidationError('Request data invalid', None)


def get_product_info_from_menu(hub_id, menu_id_list, cn_header, os_type):
    target_db = 'aries_cn' if cn_header else 'default'

    url = urlmapper.get_url('PRODUCT_WITH_MENU').format(str(hub_id))
    headers = {'os-type': str(os_type)}
    body = {'target_db': target_db, 'menu_id_list': menu_id_list}

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        result = response.json()
    else:
        result = None

    return result


def get_product_info_for_curation(product):
    if product is not None:
        result = {
            'id': product['id'],
            'type': product['type'],
            'icon_type': product['menu']['icon_type'],
            'status': product['status'],
            'status_label': product['status_label'],
            'price': product['price'],
            'price_discount_event': product['price_discount_event'],
            'price_discount': product['price_discount'],
        }

        if 'time_bomb_info' in product:
            result['badge'] = []
            result['time_bomb_info'] = product['time_bomb_info']
        else:
            result['badge'] = product['badge']
    else:
        result = {
            'id': 0,
            'type': 0,
            'icon_type': 0,
            'status': 0,
            'status_label': '',
            'price': 0,
            'price_discount_event': False,
            'price_discount': 0,
            'badge': []
        }
    return result


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


def get_banner_section(curation_list):
    banner_layout = 1
    result = None

    for curation in curation_list:
        if curation['layout_type'] == banner_layout:
            result = curation
            break

    return result


def get_curation_article(article_id, layout_type, detail, action_type=1, action_target='', action_extra=''):
    curation_section = {
        'id': article_id,
        'text_data': [],
        'award_data': [],
        'tag_data': [],
        'sub_title': '',
        'content_type': 0,
        'published_date': '',
        'has_menu_data': False,
        'menu_id': 0,
        'layout_type': layout_type,
        'title': '',
        'content': '',
        'has_dp_status': False,
        'dp_status': 0,
        'has_dp_schedule': False,
        'dp_schedule_id': 0,
        'action_type': action_type,
        'action_target': str(action_target),
        'action_extra': str(action_extra),
        'media_data': [
            {
                'detail': detail,
                'type': 0,
                'extra': ''
            }
        ],
    }
    return curation_section
