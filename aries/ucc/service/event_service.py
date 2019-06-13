from aries.ucc.models import Event, EventInformation, EventReward, EventContent, EventHistory
from aries.ucc.serializers import EventSerializer, EventInfoSerializer, EventContentSerializer, EventHistorySerializer, \
    EventRewardSerializer


class EventService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def read_event_service(self, event_id=None, lang_type=0):
        try:
            if event_id is not None:
                event_instance = Event.objects.get(id=event_id)
            else:
                event_instance = Event.objects.latest('id')

            event_info_instance = EventInformation.objects.get(event=event_instance, language_type=lang_type)
            event_content_instance = EventContent.objects.get(event=event_instance, language_type=lang_type)
            event_reward = EventReward.objects.filter(event=event_instance)

            event_data = EventSerializer(event_instance).data
            event_content_data = EventContentSerializer(event_content_instance).data
            event_info_data = EventInfoSerializer(event_info_instance).data

            # Delete some information
            del event_data['limit_type']
            del event_data['limit_count']

            del event_content_data['id']
            del event_info_data['language_type']

            for key in event_content_data.keys():
                event_data[key] = event_content_data[key]

            event_reward_list = [
                {'reward_id': event_reward.reward.id, 'probability': event_reward.probability}
                for event_reward in event_reward
            ]

        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = {
                'event': event_data,
                'event_info': event_info_data,
                'event_reward': event_reward_list
            }

        return self.result

    def read_event_history(self, event_id, open_id, today):
        try:
            today_date = today.date()
            query_str = {'event_id': event_id, 'issue_date': today_date}

            if open_id is not None:
                query_str['open_id'] = open_id

            event_histories = EventHistory.objects.filter(**query_str)
            event_history_list = []
            print(event_histories)
            for event_history in event_histories:
                history_instance = EventHistory.objects.get(open_id=open_id, id=event_history.id)
                event_history_list.append(EventHistorySerializer(history_instance).data)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = event_history_list
        return self.result

    def read_event_reward(self, event_id):
        try:
            event_rewards = EventReward.objects.filter(event=event_id)

            event_reward_list = []

            for event_reward in event_rewards:
                event_reward_instance = EventReward.objects.get(id=event_reward.id)
                event_reward_list.append(EventRewardSerializer(event_reward_instance).data)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = event_reward_list
        return self.result

    def create_event_history(self, event_id, open_id, reward_id, random_number):
        try:
            EventHistory.objects.create(
                event_id=event_id,
                open_id=open_id,
                reward_id=reward_id,
                random_number=random_number
            )
        except Exception as e:
            self.logger_error.error('[create_event_history][' + str(e) + ']')
            self.result = False
        else:
            self.result = True

        return self.result

    def read_event_count_with_date(self, today):
        try:
            date = today.date()
            event_instance = Event.objects.latest('id')
            event_count = Event.objects.filter(id=event_instance.id, start_date__lte=date, end_date__gte=date).count()
            print(event_count)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = event_count
        return self.result

    def read_event_history_with_latest(self, open_id, today):
        try:
            event_instance = Event.objects.latest('id')

            date = today.date()
            query_str = {'event_id': event_instance.id, 'issue_date': date}

            if open_id is not None:
                query_str['open_id'] = open_id

            event_history_count = EventHistory.objects.filter(**query_str).count()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = event_history_count
        return self.result
