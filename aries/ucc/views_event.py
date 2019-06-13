import logging

import aries.ucc.common.ucc_event_func as event_util

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import AuthInfoError, BusinessLogicError
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.common.utils import user_util

from aries.ucc.manager.event_manager import EventManager
from aries.ucc.models import EventHistory


class EventInformation(APIView):
    logger_info = logging.getLogger('ucc_info')
    logger_error = logging.getLogger('ucc_error')

    def get(self, request):
        auth_info = header_parser.parse_authentication(request)
        language_info = header_parser.parse_language(request.META)

        event_manager = EventManager(self.logger_info, self.logger_error)

        try:
            event = event_manager.get_event_status(auth_info, None, language_info[0])
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('event', event['event'])
            result.set('event_reward', event['event_reward'])
            result.set('event_info', event['event_info'])

        return Response(result.get_response(), result.get_code())


class EventDrawing(APIView):
    logger_info = logging.getLogger('ucc_info')
    logger_error = logging.getLogger('ucc_error')

    def get(self, request):
        auth_info = header_parser.parse_authentication(request)
        language_info = header_parser.parse_language(request.META)

        event_manager = EventManager(self.logger_info, self.logger_error)

        try:
            # Get event manager
            event_object = event_manager.get_event_status(auth_info, None, language_info[0])
            event = event_object['event']

            if event['need_auth']:
                user_util.check_auth_info(auth_info)

            # Check game play condition
            event_util.check_play_condition(event, language_info[0])

            # Play the game
            reward_result = event_manager.draw_event(event['id'], language_info[0])
            reward_id = reward_result[0]
            random_number = reward_result[1]

            # Make the history
            create_result = event_manager.create_event_history(
                event['id'], auth_info[0], reward_id, random_number, language_info[0]
            )

            # Reward interface to purchase server
            reward_tuple = create_result[2]
            event_manager.create_coupon(auth_info[0], reward_tuple.target_id, language_info[0])

            # Coupon count increase
            event_manager.increase_coupon_count(auth_info[0], auth_info[1])
        except AuthInfoError as e:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, str(e))
        except BusinessLogicError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message)
            result.set_error(err_code)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('event_reward', create_result[1])

        return Response(result.get_response(), result.get_code())


class EventDelete(APIView):
    logger_info = logging.getLogger('ucc_info')
    logger_error = logging.getLogger('ucc_error')

    def get(self, request):
        try:
            auth_info = header_parser.parse_authentication(request)
            open_id = auth_info[0]

            EventHistory.objects.filter(open_id=open_id).delete()
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())


class EventValidation(APIView):
    logger_info = logging.getLogger('ucc_info')
    logger_error = logging.getLogger('ucc_error')

    def get(self, request):
        try:
            auth_info = header_parser.parse_authentication(request)

            event_manager = EventManager(self.logger_info, self.logger_error)
            event_result = event_manager.check_event_history_count(auth_info[0], auth_info[1])

            if event_result:
                event_result = True
            else:
                event_result = False
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('event_result', event_result)

        return Response(result.get_response(), result.get_code())
