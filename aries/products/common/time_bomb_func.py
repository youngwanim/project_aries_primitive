import datetime

from aries.common.exceptions.exceptions import DataValidationError


def get_time_bomb_platform_query(os_type):
    os_type_list = [{'target_android': True}, {'target_ios': True}, {'target_mobile_web': True}]
    return os_type_list[os_type]


def check_status(start_time, end_time):
    current_time = datetime.datetime.today().time()
    return start_time < current_time < end_time


def create_time_bomb_validation(request_data):
    if 'time_bomb' not in request_data:
        raise DataValidationError('Request data invalid', None)
    if 'time_bomb_content_en' not in request_data['time_bomb']:
        raise DataValidationError('Request data invalid', None)
    if 'time_bomb_content_cn' not in request_data['time_bomb']:
        raise DataValidationError('Request data invalid', None)


def time_bomb_activation_validation(request_data):
    if 'activate' not in request_data:
        raise DataValidationError('Request data invalid', None)


def time_bomb_expired_template_en():
    date_str = str(datetime.datetime.today().date())

    time_bomb_template = {
        'code': 200,
        'message': 'success',
        'id': 1,
        'hub': 1,
        'status': 3,
        'start_date': date_str,
        'end_date': date_str,
        'start_time': 1548032400,
        'end_time': 1548032400,
        'current_time': 1548032400,
        'start_main_image': 'timebomb/timebomb_detail_eng-min.jpg',
        'end_main_image': 'timebomb/timebomb_end_eng-min.jpg',
        'start_banner_image': 'timebomb/timebomb_banner_eng-min.jpg',
        'end_banner_image': 'timebomb/timebomb_banner_eng_2-min.jpg',
        'popup_image': 'timebomb/timebomb_detail_eng-min.jpg',
        'main_content': 'Expired time bomb event.',
        'discount_message': '%',
        'expired_message': 'Time Bomb exploded! At the moment,'
                           'all the dishes are sold out for Time Bomb event for today.'
                           'Please wait until the next Time Bomb comes along.',
        'sold_out_message': 'Time Bomb exploded! At the moment,'
                           'all the dishes are sold out for Time Bomb event for today.'
                           'Please wait until the next Time Bomb comes along.',
        'guide_content': [],
        'products': [],
    }

    return time_bomb_template


def time_bomb_expired_template_cn():
    date_str = str(datetime.datetime.today().date())

    time_bomb_template = {
        'code': 200,
        'message': 'success',
        'id': 1,
        'hub': 1,
        'status': 3,
        'start_date': date_str,
        'end_date': date_str,
        'start_time': 1548032400,
        'end_time': 1548032400,
        'current_time': 1548032400,
        'start_main_image': 'timebomb/timebomb_detail_chn-min.jpg',
        'end_main_image': 'timebomb/timebomb_end_chn-min.jpg',
        'start_banner_image': 'timebomb/timebomb_banner_chn-min.jpg',
        'end_banner_image': 'timebomb/timebomb_banner_chn_2-min.jpg',
        'popup_image': 'timebomb/timebomb_detail_chn-min.jpg',
        'main_content': 'Expired time bomb event.',
        'discount_message': '%',
        'expired_message': 'Time Bomb exploded! At the moment,'
                           'all the dishes are sold out for Time Bomb event for today.'
                           'Please wait until the next Time Bomb comes along.',
        'sold_out_message': 'Time Bomb exploded! At the moment,'
                           'all the dishes are sold out for Time Bomb event for today.'
                           'Please wait until the next Time Bomb comes along.',
        'guide_content': [],
        'products': [],
    }

    return time_bomb_template
