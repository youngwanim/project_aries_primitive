import xmltodict

from aries.common import code
from aries.common.message_utils.WXBizMsgCrypt import WXBizMsgCrypt
from aries.common.models import ResultResponse


class WechatEventManager:

    def __init__(self, logger_info, logger_error, request):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.signature = request.GET.get('signature', None)
        self.timestamp = request.GET.get('timestamp', None)
        self.nonce = request.GET.get('nonce', None)
        self.open_id = request.GET.get('openid', None)
        self.msg_signature = request.GET.get('msg_signature', None)
        self.encrypt_type = request.GET.get('encrypt_type', None)

        self.logger_info.info(
            'signature:%s timestamp:%s nonce:%s open_id:%s msg_signature:%s encrypt_type:%s'
            .format(self.signature, self.timestamp, self.nonce, self.open_id, self.msg_signature, self.encrypt_type)
        )

    def request_validation(self):
        if self.signature is None or self.timestamp is None or self.nonce is None:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            validation_result = (False, result)
        else:
            validation_result = (True, None)
        return validation_result

    def get_decrypt_message(self, token, aes_key, app_id, encrypt_message):
        message_util = WXBizMsgCrypt(token, aes_key, app_id)
        decrypted_msg = message_util.DecryptMsg(encrypt_message, self.msg_signature, self.timestamp, self.nonce)

        if decrypted_msg[0] != 0:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Internal server error')
            decrypt_result = (False, result)
            return decrypt_result

        notification_data = xmltodict.parse(str(decrypted_msg[1], 'utf-8'))
        self.logger_info.info(notification_data)

        decrypt_result = (True, notification_data)
        return decrypt_result
