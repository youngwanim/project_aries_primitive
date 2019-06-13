import requests

from aries.common import urlmapper
from aries.common.utils import promotion_util
from aries.purchases.service.promotion_service import PromotionService


class PromotionManager:

    def __init__(self, logger_info, logger_error, target_db):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.target_db = target_db

    def update_notification_count(self, auth_info):
        open_id = auth_info[0]
        access_token = auth_info[1]

        if open_id is None or access_token is None:
            self.logger_info.info('[update_notification] non-member-request')
        else:
            self.logger_info.info('[update_notification] ' + open_id)
            headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}
            payload = {'has_promotion': False}
            requests.put(urlmapper.get_url('USER_NOTIFICATION'), headers=headers, json=payload)

        return True

    def get_promotion(self, promotion_id):
        promotion_service = PromotionService(self.logger_info, self.logger_error, self.target_db)
        promotion_data = promotion_service.read_promotion_with_id(promotion_id)

        if promotion_data['target_type'] == 4:
            product_id = promotion_util.parse_promotion_extra(promotion_data['target_detail'])
            promotion_data['target_detail'] = product_id

        return promotion_data

    def get_promotion_list(self, page, limit, hub_id, os_type):
        ongoing_list = []
        expired_list = []

        promotion_service = PromotionService(self.logger_info, self.logger_error, self.target_db)
        promotion_list_result = promotion_service.read_promotion_list(page, limit, hub_id)
        target_promotion_list_result = promotion_service.read_promotion_list_with_os(hub_id, os_type)

        promotion_data = target_promotion_list_result[0] + promotion_list_result[0]
        promotion_count = target_promotion_list_result[1] + promotion_list_result[1]

        for promotion in promotion_data:
            if promotion['target_type'] == 4:
                product_id = promotion_util.parse_promotion_extra(promotion['target_detail'])
                promotion['target_detail'] = product_id

            if promotion['status'] == 0:
                expired_list.append(promotion)
            else:
                ongoing_list.append(promotion)

        result = (promotion_count, ongoing_list + expired_list)
        return result

    def get_promotion_list_with_latest(self, promotion_type, lang_type):
        promotion_service = PromotionService(self.logger_info, self.logger_error, lang_type)
        coupon_promotion = promotion_service.read_coupon_promotion_with_latest(promotion_type, lang_type)

        return coupon_promotion
