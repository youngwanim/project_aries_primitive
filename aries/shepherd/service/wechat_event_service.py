from aries.common import code
from aries.common.models import ResultResponse
from aries.shepherd.models import WechatEventMessage


class WechatEventService:

    def __init__(self):
        self.service_result = (True, None)

    def create_wechat_event_message(self, wechat_message):

        try:
            WechatEventMessage.objects.create(**wechat_message)
        except Exception as e:
            print(e)
            self.service_result = (False, ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Internal server error'))

        return self.service_result
