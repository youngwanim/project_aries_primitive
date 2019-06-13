import json
import random
from collections import namedtuple

import requests

from aries.common import urlmapper
from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.message_utils import message_mapper


def get_lang_type(cn_header):
    lang_type = 0
    if cn_header:
        lang_type = 1
    return lang_type


def parse_json_content(content):
    if 'content' in content:
        content['content'] = json.loads(content['content'])
    if 'how_to_content' in content:
        content['how_to_content'] = json.loads(content['how_to_content'])

    del content['event']
    del content['language_type']

    return content


def set_event_image(event_info, image_path):
    event_info['main_image'] = image_path
    event_info['main_list_image'] = image_path
    event_info['promotion_list_image'] = image_path
    return


def set_content_data(event, event_info, event_available, already_played):
    if not event_available:
        set_event_image(event_info, event['close_image'])
    elif not already_played:
        set_event_image(event_info, event['played_image'])
    else:
        set_event_image(event_info, event['open_image'])

    # Event info
    del event_info['event']

    # Event
    del event['close_image']
    del event['played_image']
    del event['open_image']
    return


def get_time_tuple(start_time, end_time):
    start_time_split = str(start_time).split(':')
    end_time_split = str(end_time).split(':')

    start_hour = int(start_time_split[0])
    start_min = int(start_time_split[1])
    end_hour = int(end_time_split[0])
    end_min = int(end_time_split[1])

    Time = namedtuple('Time', 'start_hour start_min end_hour end_min')
    return Time(start_hour, start_min, end_hour, end_min)


def get_random_number():
    return random.randrange(1, 1000)


def check_play_condition(event, cn_header):
    event_available = event['event_available']
    already_played = event['already_played']

    result = True
    message = ''
    err_code = 0

    if not event_available:
        message = message_mapper.get(5001, cn_header)
        err_code = 5001
        result = False
    elif already_played:
        message = message_mapper.get(5002, cn_header)
        err_code = 5002
        result = False

    if not result:
        raise BusinessLogicError(message, err_code)

    return


def check_history_list(history_list, cn_header):
    if len(history_list) >= 1:
        err_code = 5002
        message = message_mapper.get(err_code, cn_header)
        raise BusinessLogicError(message, err_code)


def get_selected_item(event_list, random_number):
    for event in event_list:
        if event[1][0] <= random_number <= event[1][1]:
            return event


def draw_event_validation(event_list, cn_header):
    if len(event_list) <= 0:
        err_code = 5003
        message = message_mapper.get(err_code, cn_header)
        raise BusinessLogicError(message, err_code)

    prob_sum = 0

    for event in event_list:
        prob_sum += event['probability']

    if prob_sum != 1:
        err_code = 5003
        message = message_mapper.get(err_code, cn_header)
        raise BusinessLogicError(message, err_code)


def delete_reward_data(reward_data):
    del reward_data['target_id']
    del reward_data['target_point']
    del reward_data['limit_type']
    del reward_data['limit_count']
    del reward_data['reward']
    del reward_data['language_type']
    reward_data['title'] = json.loads(reward_data['title'])['text']

    return reward_data


def request_create_coupon(open_id, coupon_id):
    request_body = {'open_id': open_id, 'coupon_id': coupon_id}
    response = requests.post(url=urlmapper.get_url('ROULETTE_COUPON'), json=request_body)

    if response.status_code != 200:
        result = False
    else:
        result = True

    return result
