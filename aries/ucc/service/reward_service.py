import json

from aries.ucc.models import Reward, RewardContent, EventReward
from aries.ucc.serializers import RewardSerializer, RewardContentSerializer


class RewardService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def read_reward_list(self, component_list, lang_type=0):
        try:
            reward_list = []

            for component in component_list:
                reward_instance = Reward.objects.get(id=component['reward_id'])
                reward_content = RewardContent.objects.get(reward=reward_instance, language_type=lang_type)

                reward_data = RewardSerializer(reward_instance).data
                reward_content_data = RewardContentSerializer(reward_content).data

                del reward_data['target_id']
                del reward_data['target_point']
                del reward_data['limit_type']
                del reward_data['limit_count']

                del reward_content_data['id']
                del reward_content_data['language_type']
                del reward_content_data['reward']

                for key in reward_content_data.keys():
                    reward_data[key] = reward_content_data.get(key, '')

                reward_data['title'] = json.loads(reward_data['title'])['text']

                reward_list.append(reward_data)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = reward_list

        return self.result

    def read_reward(self, event_reward_id, lang_type=0):
        try:
            event_reward_instance = EventReward.objects.get(id=event_reward_id)
            reward_instance = event_reward_instance.reward
            reward_content_ins = RewardContent.objects.get(reward=reward_instance, language_type=lang_type)

            reward_data = RewardSerializer(reward_instance).data
            reward_content_data = RewardContentSerializer(reward_content_ins).data

            del reward_content_data['id']

            for key in reward_content_data.keys():
                reward_data[key] = reward_content_data[key]
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = reward_data

        return self.result
