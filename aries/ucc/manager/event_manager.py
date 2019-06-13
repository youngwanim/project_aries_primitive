import datetime
import random
from collections import namedtuple

import requests

import aries.ucc.common.ucc_event_func as event_util
from aries.common import urlmapper
from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.message_utils import message_mapper

from aries.ucc.service.event_service import EventService
from aries.ucc.service.reward_service import RewardService


class EventManager:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.event_service = EventService(self.logger_info, self.logger_error)
        self.reward_service = RewardService(self.logger_info, self.logger_error)

    def get_event_status(self, auth_info, event_id=0, cn_header=False):
        self.logger_info.info(
            '[EventManager][get_event_status][PARAMS:' + str(event_id) + ',' + str(cn_header) + ']'
        )

        open_id = auth_info[0]
        lang_type = event_util.get_lang_type(cn_header)

        event_object = self.event_service.read_event_service(event_id, lang_type)
        event_object['event'] = event_util.parse_json_content(event_object['event'])

        reward_list = event_object['event_reward']
        event_object['event_reward'] = self.reward_service.read_reward_list(reward_list, lang_type)

        event = event_object['event']

        # Game playable check
        event_available = True
        play_available = True
        already_played = False

        # Time parsing
        start_date = datetime.datetime.strptime(event['start_date'], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(event['end_date'], '%Y-%m-%d')

        # Get named tuple from event time
        event_time = event_util.get_time_tuple(event['start_time'], event['end_time'])

        # Event period validation
        today = datetime.datetime.today()
        today_date = datetime.datetime(today.year, today.month, today.day, 0, 0)

        if not (start_date <= today_date <= end_date):
            event_available = False
            play_available = False

        # Time limit check
        if event['has_game_time'] and event_available:
            start_time = datetime.time(event_time.start_hour, event_time.start_min)
            end_time = datetime.time(event_time.end_hour, event_time.end_min)
            current_time = datetime.time(today.hour, today.minute)

            if not (start_time <= current_time <= end_time):
                play_available = False

        # Check event history
        if open_id is not None:
            history_list = self.event_service.read_event_history(event['id'], open_id, today)
            if len(history_list) >= 1:
                play_available = False
                already_played = True

        # Event information image change
        event['event_available'] = event_available
        event['play_available'] = play_available
        event['already_played'] = already_played

        # Data parsing
        event_info = event_object['event_info']
        event_util.set_content_data(event, event_info, event_available, already_played)

        return event_object

    def draw_event(self, event_id, cn_header=False):
        event_reward_list = self.event_service.read_event_reward(event_id)
        event_util.draw_event_validation(event_reward_list, cn_header)

        random.shuffle(event_reward_list)

        event_list = []
        start_index = 1
        end_index = 0

        for event_reward in event_reward_list:
            end_index = end_index + event_reward['probability']*1000
            event_info = (event_reward['id'], (start_index, end_index))
            event_list.append(event_info)
            start_index = end_index+1

        for event in event_list:
            print(event)

        random_number = event_util.get_random_number()
        selected_reward = event_util.get_selected_item(event_list, random_number)
        reward_id = selected_reward[0]

        result = (reward_id, random_number)
        return result

    def create_event_history(self, event_id, open_id, reward_id, random_number, cn_header=False):
        today = datetime.datetime.today()

        history_list = self.event_service.read_event_history(event_id, open_id, today)
        event_util.check_history_list(history_list, cn_header)

        create_result = self.event_service.create_event_history(event_id, open_id, reward_id, random_number)

        if not create_result:
            err_code = 5004
            message = message_mapper.get(err_code, cn_header)
            raise BusinessLogicError(message, err_code)

        reward_data = self.reward_service.read_reward(reward_id, cn_header)

        name = reward_data['name']
        reward_type = reward_data['type']
        target_id = reward_data['target_id']
        target_point = reward_data['target_point']
        limit_type = reward_data['limit_type']
        limit_count = reward_data['limit_count']

        Reward = namedtuple('Reward', 'name type target_id target_point limit_type limit_count')
        reward_tuple = Reward(name, reward_type, target_id, target_point, limit_type, limit_count)

        result = (True, event_util.delete_reward_data(reward_data), reward_tuple)

        return result

    def create_coupon(self, open_id, coupon_id, cn_header=False):
        self.logger_info.info('[EventManager][create_coupon][' + open_id + ',' + str(coupon_id))

        result = event_util.request_create_coupon(open_id, coupon_id)

        if not result:
            message = message_mapper.get(3013, cn_header)
            raise BusinessLogicError(message, 3013)

        return True

    def increase_coupon_count(self, open_id, access_token):
        self.logger_info.info('[EventManager][increase_coupon_count][' + open_id + '][' + access_token + ']')
        url = urlmapper.get_url('USER_NOTIFICATION_UPDATE').format('coupon', '0', '1')
        headers = {'open-id': open_id, 'Authorization': 'bearer ' + access_token}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return False

        return True

    def check_event_history_count(self, open_id, access_token):
        self.logger_info.info('[EventManager][event_history_count][' + open_id + '][' + access_token + ']')

        today = datetime.datetime.today()
        event_count = self.event_service.read_event_count_with_date(today)

        if event_count == 0:
            return False

        history_count = self.event_service.read_event_history_with_latest(open_id, today)

        if history_count != 0:
            return False

        return True
