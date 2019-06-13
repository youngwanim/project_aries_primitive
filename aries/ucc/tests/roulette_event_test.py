import json
import logging
import aries.ucc.common.ucc_event_func as event_util

from django.test import TestCase

from aries.common.exceptions.exceptions import BusinessLogicError


class TestRouletteEvent(TestCase):

    def setUp(self):
        self.logger_info = logging.getLogger('purchases_info')
        self.logger_error = logging.getLogger('purchases_error')

    # TEST01 : ucc_event_func
    def test_ucc_event_func(self):
        self.assertEqual(0, event_util.get_lang_type(False))
        self.assertEqual(1, event_util.get_lang_type(True))

        test_data = {'content': '{"t": "H"}', 'how_to_content': '["One", "Two]', 'event': '111', 'language_type': 0}
        after_test_data = event_util.parse_json_content(test_data)
        self.assertIsNone(after_test_data['event'])
        self.assertIsNone(after_test_data['language_type'])
        self.assertIsNotNone(after_test_data['content'])
        self.assertIsNotNone(after_test_data['how_to_content'])

        event_info = {
            'main_image': 'before',
            'main_list_image': 'before',
            'promotion_list_image': 'before'
        }
        event_info = event_util.set_event_image(event_info, 'after')
        self.assertEqual('before', event_info['main_image'])
        self.assertEqual('before', event_info['main_list_image'])
        self.assertEqual('before', event_info['promotion_list_image'])

        event_info = {
            'close_image': '',
            'played_image': '',
            'open_image': ''
        }
        event = {'event': ''}

        event_util.set_content_data(event, event_info, True, True)
        self.assertIsNone(event_info['close_image'])
        self.assertIsNone(event_info['played_image'])
        self.assertIsNone(event_info['open_image'])
        self.assertIsNone(event['event'])

        start_time = '12:24'
        end_time = '18:37'

        time_tuple = event_util.get_time_tuple(start_time, end_time)
        self.assertEqual(12, time_tuple.start_hour)
        self.assertEqual(24, time_tuple.start_min)
        self.assertEqual(18, time_tuple.end_hour)
        self.assertEqual(37, time_tuple.end_min)

        reward_dummy = {
            'target_id': 1,
            'target_point': 10,
            'limit_type': 1,
            'limit_count': 9,
            'reward': 'reward',
            'language_type': 0,
            'title': '{"text":"my_text"}'
        }
        reward_dummy = event_util.delete_reward_data(reward_dummy)
        self.assertIsNone(reward_dummy['target_id'])
        self.assertIsNone(reward_dummy['target_point'])
        self.assertIsNone(reward_dummy['limit_type'])
        self.assertIsNone(reward_dummy['limit_count'])
        self.assertIsNone(reward_dummy['reward'])
        self.assertIsNone(reward_dummy['language_type'])
        self.assertEqual(reward_dummy['title'], 'my_text')

        event = {'event_available': False, 'already_played': False}
        self.assertRaises(BusinessLogicError, event_util.check_play_condition(event, False))
        event = {'event_available': True, 'already_played': False}
        self.assertRaisesMessage(BusinessLogicError, 'Event period finished',
                                 event_util.check_play_condition(event, False))

        history_list = ['test']
        self.assertRaises(BusinessLogicError, event_util.check_history_list(history_list), False)
        event_list = [('Hello', (1, 100)), ('Hello 2', (101, 500))]
        event = event_util.get_selected_item(event_list, 444)
        self.assertEqual(event[0], 'Hello 2')
        self.assertEqual(event[1][0], 101)

        event_list = []
        self.assertRaises(BusinessLogicError, event_util.draw_event_validation(event_list, False))
        event_list = [{'probability': 0.3}, {'probability': 0.5}, {'probability': 0.1}]
        self.assertRaises(BusinessLogicError, event_util.draw_event_validation(event_list, ))


