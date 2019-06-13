from aries.users.models import User, UserReferralInformation, UserNotifyInfo
from aries.users.serializers import UserReferralInfoSerializer


class UserReferralService:
    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def create_user_referral_info(self, user_open_id, user_mdn, referrer_id, referrer_open_id):
        try:
            referrer_user = User.objects.get(open_id=referrer_open_id)
            referrer_mdn = referrer_user.mdn

            UserReferralInformation.objects.create(
                user_open_id=user_open_id,
                user_mdn=user_mdn,
                referrer_open_id=referrer_open_id,
                referrer_share_id=referrer_id,
                referrer_mdn=referrer_mdn
            )

            notify_instance = UserNotifyInfo.objects.get(user=referrer_user)
            notify_instance.has_referral_event = True
            notify_instance.save()
        except Exception as e:
            self.logger_info.info(str(e))
            self.result = False
        else:
            self.result = True

        return self.result

    def read_user_referral_info_check(self, user_mdn):
        try:
            referral_info_count = UserReferralInformation.objects.filter(user_mdn=user_mdn).count()

            if referral_info_count == 0:
                referral_result = True
            else:
                referral_result = False
        except Exception as e:
            self.logger_info.info(str(e))
            self.result = False
        else:
            self.result = referral_result

        return self.result

    def read_user_referral_info(self, user_open_id):
        try:
            referral_info_count = UserReferralInformation.objects.filter(user_open_id=user_open_id).count()

            if referral_info_count == 0:
                referral_info = None
            else:
                referral_info_ins = UserReferralInformation.objects.get(user_open_id=user_open_id)
                referral_info = UserReferralInfoSerializer(referral_info_ins).data
        except Exception as e:
            self.logger_info.info(str(e))
            self.result = None
        else:
            self.result = referral_info

        return self.result
