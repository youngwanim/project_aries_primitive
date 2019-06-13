import json

from aries.common.utils.push_util_v2 import PushInstance
from aries.ucc.service.referral_service import ReferralService
from aries.users.common.shopping_bag_func import get_check_sp_instruction, cut_user_inst_template
from aries.users.serializers import UserInfoSerializer, UserAccountSerializer
from aries.users.service.user_receipt_service import UserReceiptService
from aries.users.service.user_service import UserService


class UserManagerV2:

    SIGN_UP_MSG_EN = 'You have got good friends who got you {} coupon just now!'
    SIGN_UP_MSG_CN = '你的好友刚刚为你赢得{}张优惠礼券！'

    REF_TARGET = 101

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.user_service = UserService(self.logger_info, self.logger_error)
        self.receipt_service = UserReceiptService(self.logger_info, self.logger_error)

    def send_sign_up_push(self, user_open_id, cn_header):
        self.logger_info.info('[UserManagerV2][send_sign_up_push][' + str(user_open_id) + ']')
        try:
            user_service = UserService(self.logger_info, self.logger_error)
            referral_service = ReferralService(self.logger_info, self.logger_error)

            user_instance = user_service.get_user_instance(user_open_id)
            user_info_ins = user_service.get_user_info_with_ins(user_instance)
            referral_data = referral_service.read_referral_event(user_open_id)

            push_agreement = user_instance.push_agreement
            os_type = user_info_ins.os_type
            self.logger_info.info('[UserManagerV2][send_sign_up_push][Push data read complete]')

            if (os_type == 0 or os_type == 1) and 'friend_membership_count' in referral_data:
                self.logger_info.info('[UserManagerV2][send_sign_up_push][' + str(os_type) + ']')

                friend_count = referral_data['friend_membership_count']
                friend_check = True if friend_count == 1 or (friend_count % 5) == 0 else False

                if str(push_agreement).lower() == 'y' and friend_check:
                    self.logger_info.info('[UserManagerV2][send_sign_up_push][Push send]')
                    title = ''
                    if cn_header:
                        message = self.SIGN_UP_MSG_CN.format(str(friend_count))
                    else:
                        message = self.SIGN_UP_MSG_EN.format(str(friend_count))
                    push_sender = PushInstance.factory(os_type, user_open_id, title, message, self.REF_TARGET, '')
                    push_sender.send_push_notification()
        except Exception as e:
            self.logger_info.info(str(e))

    def get_user_data(self, user_open_id):
        self.logger_info.info('[UserManagerV2][get_default_hub_id][' + user_open_id + ']')

        user_service = UserService(self.logger_info, self.logger_error)
        user_instance = user_service.get_user_instance(user_open_id)
        user_data = UserAccountSerializer(user_instance).data

        return user_data

    def get_user_info(self, user_open_id):
        self.logger_info.info('[UserManagerV2][get_user_info][' + user_open_id + ']')

        user_service = UserService(self.logger_info, self.logger_error)
        user_instance = user_service.get_user_instance(user_open_id)
        user_info = user_service.get_user_info_with_ins(user_instance)

        return UserInfoSerializer(user_info).data

    def get_user_cart_info_data(self, user_open_id):
        self.logger_info.info('[UserManagerV2][get_user_cart_info][' + user_open_id + ']')

        user_service = UserService(self.logger_info, self.logger_error)
        user_instance = user_service.get_user_instance(user_open_id)
        cart_info = user_service.get_user_cart_info(user_instance)

        return cart_info

    def update_cart_info(self, cart_info, include_cutlery, special_instruction):
        self.logger_info.info('[UserManagerV2][update_cart_info]')

        user_service = UserService(self.logger_info, self.logger_error)

        if get_check_sp_instruction(special_instruction):
            special_instruction = None
        else:
            special_instruction = cut_user_inst_template(special_instruction)

        result = user_service.set_user_cart_info(cart_info, include_cutlery, special_instruction)

        return result
