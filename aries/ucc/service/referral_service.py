import json

from aries.ucc.common.referral_func import get_shared_id
from aries.ucc.models import ReferralEvent, ReferralInformation
from aries.ucc.serializers import ReferralEventSerializer, ReferralInformationSerializer


class ReferralService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def read_referral_event(self, open_id):
        try:
            referral_count = ReferralEvent.objects.filter(open_id=open_id).count()

            # Referral event object create (QR code is generated in this section)
            if referral_count == 0:
                share_id = get_shared_id(open_id)
                while True:
                    if ReferralEvent.objects.filter(share_id=share_id).count() == 0:
                        break
                    else:
                        share_id = get_shared_id(open_id)

                referral_info_qs = ReferralInformation.objects.filter(referral_type=0).order_by('reward_sequence')
                friend_coupon_list = ReferralInformationSerializer(referral_info_qs, many=True).data

                referral_info_qs = ReferralInformation.objects.filter(referral_type=1).order_by('reward_sequence')
                first_coupon_list = ReferralInformationSerializer(referral_info_qs, many=True).data

                ReferralEvent.objects.create(
                    open_id=open_id, share_id=share_id,
                    invitation_url='https://m.viastelle.com/invitation.html?id=' + share_id,
                    friend_coupon_status=json.dumps(friend_coupon_list),
                    first_coupon_status=json.dumps(first_coupon_list)
                )

            referral_event_ins = ReferralEvent.objects.get(open_id=open_id)
            referral_data = ReferralEventSerializer(referral_event_ins).data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = referral_data

        return self.result

    def read_referral_with_unique_id(self, share_id):
        try:
            referral_info_qs = ReferralEvent.objects.filter(share_id=share_id)

            if referral_info_qs.count() == 0:
                referral_info = None
            else:
                referral_info = ReferralEvent.objects.get(share_id=share_id)
                friend_count = referral_info.friend_membership_count

                if friend_count+1 > 25:
                    referral_info.friend_membership_over = True
                referral_info.friend_membership_count += 1

                coupon_status = json.loads(referral_info.friend_coupon_status)
                for coupon in coupon_status:
                    if coupon['reward_count'] <= friend_count+1 and not coupon['issue_complete']:
                        coupon['issue_available'] = True
                referral_info.friend_coupon_status = json.dumps(coupon_status)
                referral_info.save()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = referral_info

        return self.result

    def read_referral_information(self, referral_type):
        try:
            referral_info_qs = ReferralInformation.objects.filter(referral_type=referral_type)
            referral_info_data = ReferralInformationSerializer(referral_info_qs, many=True).data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = referral_info_data

        return self.result

    def update_referral_reset_friend_info(self, open_id):
        try:
            referral_instance = ReferralEvent.objects.get(open_id=open_id)
            referral_instance.friend_membership_count -= 25

            if referral_instance.friend_membership_count >= 25:
                referral_instance.friend_membership_over = True
            else:
                referral_instance.friend_membership_over = False

            referral_instance.save()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = referral_instance.friend_membership_rest_count

        return self.result

    def update_referral_first_information(self, open_id, reward_count):
        try:
            referral_instance = ReferralEvent.objects.get(open_id=open_id)
            referral_instance.first_purchase_reward_count += reward_count
            referral_instance.first_purchase_rest_count -= reward_count
            referral_instance.save()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = referral_instance.first_purchase_rest_count

        return self.result

    def update_referral_coupon_status(self, open_id, coupon_type, coupon_status):
        try:
            referral_instance = ReferralEvent.objects.get(open_id=open_id)

            if coupon_type == 0:
                referral_instance.friend_coupon_status = json.dumps(coupon_status)
            else:
                referral_instance.first_coupon_status = json.dumps(coupon_status)

            referral_instance.save()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = True

    def update_referral_qr_code(self, open_id, qr_code_image_url):
        try:
            referral_instance = ReferralEvent.objects.get(open_id=open_id)
            referral_instance.has_invitation_image = True
            referral_instance.invitation_image = 'ref_qr/' + qr_code_image_url + '.png'
            referral_instance.save()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = True

        return self.result

    def update_referral_over_flag(self, open_id, over_flag):
        try:
            referral_instance = ReferralEvent.objects.get(open_id=open_id)
            referral_instance.friend_membership_over = over_flag
            referral_instance.save()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = True

        return self.result

    def first_order_up(self, open_id):
        try:
            referral_info = ReferralEvent.objects.get(open_id=open_id)
            referral_info.first_purchase_count += 1
            referral_info.first_purchase_rest_count += 1
            first_coupon_list = json.loads(referral_info.first_coupon_status)
            for coupon in first_coupon_list:
                coupon['issue_available'] = True
            referral_info.first_coupon_status = json.dumps(first_coupon_list)
            referral_info.save()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = referral_info

        return self.result
