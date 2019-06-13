import requests

import aries.ucc.common.referral_func as ref_util
from aries.common import urlmapper

from aries.common.exceptions.exceptions import BusinessLogicError, DataValidationError
from aries.common.message_utils import message_mapper
from aries.ucc.common.referral_func import get_coupon_information, issue_coupon
from aries.ucc.service.referral_service import ReferralService

from aries.users.service.user_service import UserService


class ReferralManager:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        # Check user service when decouple user and ucc domain
        self.referral_service = ReferralService(logger_info, logger_error)
        self.user_service = UserService(logger_info, logger_error)

    def get_referral_status(self, open_id, access_token, accept_lang):
        # Get referral event data
        referral_event_data = self.referral_service.read_referral_event(open_id)
        friend_coupon_status = referral_event_data['friend_coupon_status']
        first_coupon_status = referral_event_data['first_coupon_status']

        # Check qr code exists
        if not referral_event_data['has_invitation_image']:
            unique_id = referral_event_data['share_id']
            qr_result = ref_util.generate_qr_code(unique_id, open_id, access_token)

            if qr_result:
                self.referral_service.update_referral_qr_code(open_id, unique_id)

            referral_event_data = self.referral_service.read_referral_event(open_id)
            friend_coupon_status = referral_event_data['friend_coupon_status']
            first_coupon_status = referral_event_data['first_coupon_status']

        # Friend membership count
        if referral_event_data['friend_membership_count'] > 25:
            referral_event_data['friend_membership_count'] = 25
            referral_event_data['friend_membership_over'] = True

        # Thumbnail data change with language and add share description to referral event
        ref_util.get_image_with_language(referral_event_data, accept_lang)
        ref_util.get_share_information(referral_event_data, accept_lang)

        # Get coupon description
        referral_event_data['description'] = ref_util.get_coupon_description(30, accept_lang)

        # Get coupon id and description
        coupon_ids = []
        for coupon in friend_coupon_status:
            coupon['description'] = ref_util.get_coupon_description(30, accept_lang)
            coupon_ids.append(coupon['id'])

        for coupon in first_coupon_status:
            coupon['description'] = ref_util.get_coupon_description(30, accept_lang)
            coupon_ids.append(coupon['id'])

        coupon_info = get_coupon_information(coupon_ids, accept_lang)

        for coupon in coupon_info:
            coupon_id = coupon['id']
            cash_discount = int(coupon['cash_discount'])
            for friend_coupon in friend_coupon_status:
                if friend_coupon['id'] == coupon_id:
                    friend_coupon['name'] = ref_util.friend_coupon_naming(str(cash_discount), accept_lang)

            for first_coupon in first_coupon_status:
                if first_coupon['id'] == coupon_id:
                    first_coupon['name'] = ref_util.pur_coupon_naming(str(cash_discount), accept_lang)

        # First purchase coupon calculate
        first_purchase_rest_count = referral_event_data['first_purchase_rest_count']
        result_purchase_coupon_list = []

        if first_purchase_rest_count > 0:
            first_coupon = first_coupon_status[0]
            for index in range(first_purchase_rest_count):
                result_purchase_coupon_list.append(first_coupon)
            referral_event_data['first_coupon_available'] = True

        referral_event_data['first_coupon_status'] = result_purchase_coupon_list
        return referral_event_data

    def get_referral_information(self, accept_lang):
        friend_type = 0
        first_type = 1

        friend_coupon_status = self.referral_service.read_referral_information(friend_type)
        first_coupon_status = self.referral_service.read_referral_information(first_type)

        coupon_ids = []
        for coupon in friend_coupon_status:
            coupon_ids.append(coupon['id'])

        for coupon in first_coupon_status:
            coupon_ids.append(coupon['id'])

        coupon_info = get_coupon_information(coupon_ids, accept_lang)

        for coupon in coupon_info:
            coupon_id = coupon['id']
            cash_discount = int(coupon['cash_discount'])

            for friend_coupon in friend_coupon_status:
                if friend_coupon['id'] == coupon_id:
                    friend_coupon['name'] = ref_util.friend_coupon_naming(str(cash_discount), accept_lang)

            for first_coupon in first_coupon_status:
                if first_coupon['id'] == coupon_id:
                    first_coupon['name'] = ref_util.pur_coupon_naming(str(cash_discount), accept_lang)

        referral_info_data = {
            'friend_coupon_status': friend_coupon_status,
            'first_coupon_status': first_coupon_status
        }

        return referral_info_data

    def issue_referral_coupon(self, open_id, cn_header, coupon_type, coupon_list):
        referral_event = self.referral_service.read_referral_event(open_id)

        if coupon_type == 0:
            target_coupon_list = referral_event['friend_coupon_status']
            user_reward_count = referral_event['friend_membership_count']
        else:
            target_coupon_list = referral_event['first_coupon_status']
            user_reward_count = referral_event['first_purchase_rest_count']

        # Find target coupons
        issue_coupon_list = []
        coupon_reward_count = 0

        for req_coupon in coupon_list:
            for tag_coupon in target_coupon_list:
                if tag_coupon['id'] == req_coupon['id']:
                    # Coupon reward condition check
                    coupon_reward_count = tag_coupon['reward_count']
                    coupon_issue_complete = tag_coupon['issue_complete']

                    if coupon_issue_complete:
                        raise BusinessLogicError(message_mapper.get(3202, cn_header), 3202, None)

                    if user_reward_count < coupon_reward_count:
                        raise BusinessLogicError(message_mapper.get(3201, cn_header), 3201, None)

                    issue_coupon_list.append(tag_coupon)

        # Coupon reward point update
        if coupon_type == 1:
            all_reward_count = len(coupon_list)*coupon_reward_count
            self.referral_service.update_referral_first_information(open_id, all_reward_count)

        # Coupon issue and User coupon_count update
        coupon_code = 'referral_20180725'
        sender_id = 'Admin'
        issue_coupon(open_id, cn_header, issue_coupon_list, coupon_code, sender_id)

        # Get new referral information
        referral_event = self.referral_service.read_referral_event(open_id)
        if coupon_type == 0:
            target_coupon_list = referral_event['friend_coupon_status']
            user_reward_count = referral_event['friend_membership_count']
        else:
            target_coupon_list = referral_event['first_coupon_status']
            user_reward_count = referral_event['first_purchase_rest_count']

        # Rest coupon status check
        has_reset = False

        if coupon_type == 0:
            for coupon in issue_coupon_list:
                for user_coupon in target_coupon_list:
                    if coupon['id'] == user_coupon['id']:
                        user_coupon['issue_available'] = False
                        user_coupon['issue_complete'] = True
        else:
            if user_reward_count <= 0:
                for coupon in target_coupon_list:
                    coupon['issue_available'] = False
                    coupon['issue_complete'] = False
            else:
                for coupon in target_coupon_list:
                    coupon['issue_available'] = True
                    coupon['issue_complete'] = False

        self.referral_service.update_referral_coupon_status(open_id, coupon_type, target_coupon_list)

        # Get new referral information
        referral_event = self.referral_service.read_referral_event(open_id)
        if coupon_type == 0:
            target_coupon_list = referral_event['friend_coupon_status']
        else:
            target_coupon_list = referral_event['first_coupon_status']

        # Get coupon id and description, name
        accept_lang = 'zh' if cn_header else 'en'

        coupon_ids = []
        for coupon in target_coupon_list:
            coupon['description'] = ref_util.get_coupon_description(30, accept_lang)
            coupon_ids.append(coupon['id'])

        coupon_info = get_coupon_information(coupon_ids, accept_lang)

        for coupon in coupon_info:
            coupon_id = coupon['id']

            for target_coupon in target_coupon_list:
                if target_coupon['id'] == coupon_id:
                    cash_discount = int(coupon['cash_discount'])
                    if coupon_type == 0:
                        target_coupon['name'] = ref_util.friend_coupon_naming(str(cash_discount), accept_lang)
                    else:
                        target_coupon['name'] = ref_util.pur_coupon_naming(str(cash_discount), accept_lang)

        # Result mapping from coupon_list
        if coupon_type == 0:
            friend_membership_count = referral_event['friend_membership_count']

            # Friend membership count
            if friend_membership_count > 25:
                friend_membership_count = 25
                referral_over = True
            else:
                referral_over = False
                if referral_event['friend_membership_over']:
                    self.referral_service.update_referral_over_flag(open_id, False)

            result = {
                'coupon_status': target_coupon_list, 'has_reset': has_reset,
                'friend_membership_count': friend_membership_count, 'friend_membership_over': referral_over
            }
        else:
            rest_point = referral_event['first_purchase_rest_count']
            result_coupon_list = []

            if len(target_coupon_list) >= 1:
                coupon = target_coupon_list[0]
                for index in range(rest_point):
                    result_coupon_list.append(coupon)

            result = {
                'coupon_status': result_coupon_list, 'has_reset': has_reset
            }

        return result

    def check_coupon_reset(self, open_id):
        referral_event = self.referral_service.read_referral_event(open_id)
        friend_coupon_list = referral_event['friend_coupon_status']
        user_membership_count = referral_event['friend_membership_count']

        all_clear = True
        for coupon in friend_coupon_list:
            if not coupon['issue_complete']:
                all_clear = False

        if all_clear:
            self.referral_service.update_referral_reset_friend_info(open_id)
            user_membership_count -= 25

            for coupon in friend_coupon_list:
                if coupon['reward_count'] <= user_membership_count:
                    coupon['issue_available'] = True
                else:
                    coupon['issue_available'] = False
                coupon['issue_complete'] = False

            self.referral_service.update_referral_coupon_status(open_id, 0, friend_coupon_list)

        return all_clear

    def get_open_id_from_unique_id(self, share_id):
        referral_event = self.referral_service.read_referral_with_unique_id(share_id)

        if referral_event is None:
            raise DataValidationError('Do not find unique id', None)

        referral_result = {'open_id': referral_event.open_id, 'share_id': referral_event.share_id}

        return referral_result

    def do_first_purchase_up(self, open_id):
        referral = self.referral_service.first_order_up(open_id)
        rest_count = str(referral.first_purchase_rest_count)

        user_ins = self.user_service.get_user_instance(open_id)
        user_locale = user_ins.locale

        if user_locale == 'en' or user_locale == 'En':
            push_message = 'Good friends you have! You’ve got {} coupon you can use right now~'.format(rest_count)
        else:
            push_message = '好友送福利！你获得{}张优惠礼券，快去使用吧~'.format(rest_count)

        payload = {
            'code': 200, 'message': 'success', 'order': '', 'type': 0,
            'order_id': '', 'title': push_message
        }
        url = urlmapper.get_url('HUB_MESSAGE_ANDROID')
        response = requests.post(url, json=payload)
        self.logger_info.info(response.content)
