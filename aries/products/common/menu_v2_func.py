import json

from aries.common.exceptions.exceptions import DataValidationError
from aries.common.utils import message_util


def request_validation(request_data):
    if 'menu_id_list' not in request_data or 'target_db' not in request_data:
        raise DataValidationError('Hub id or Menu id not found', None)


def get_menu_data(menu_data, cn_header, sales_time):
    microwave = message_util.get_about_the_menu_microwave(cn_header)
    menu_desc = message_util.get_about_desc(cn_header, sales_time)

    menu_data['description'] = json.loads(menu_data['description'])
    menu_data['description'][0] = menu_data['description'][0].format(microwave, menu_desc)
    menu_data['prep_tips'] = json.loads(menu_data['prep_tips'])
    menu_data['ingredients'] = json.loads(menu_data['ingredients'])
    menu_data['nutrition'] = json.loads(menu_data['nutrition'])
    menu_data['notices'] = json.loads(menu_data['notices'])
    menu_data['subs_contents'] = json.loads(menu_data['subs_contents'])
    menu_data['media_contents'] = json.loads(menu_data['media_contents'])

    menu_list = json.loads(menu_data['image_detail'])
    menu_data['image_detail'] = menu_list[0]
    menu_data['image_detail_list'] = menu_list

    return menu_data
