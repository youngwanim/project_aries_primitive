import json

from aries.common import code
from aries.common import payment_util
from aries.common.code_msg import get_msg
from aries.common.exceptions.exceptions import BusinessLogicError

from aries.purchases.factory.coupon_factory import CouponInstance
from aries.purchases.service.coupon_service import CouponService


class CouponManagerV2:

    product_list = []
    coupon_list = []
    coupon_detail = []

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.discount_price = 0
        self.product_list = []
        self.coupon_list = []
        self.coupon_detail = []

    def coupon_validate(self, open_id, product_list, coupon_list):
        self.logger_info.info('[coupon_manager_v2][CouponManagerV2][coupon_validate][' + open_id + ']')

        self.product_list = product_list
        self.coupon_list = coupon_list

        coupon_service = CouponService(self.logger_info, self.logger_error)

        for coupon in coupon_list:
            # Get coupon information
            coupon_id = coupon['coupon_id']
            cs_coupon_ins = coupon_service.read_customer_coupon_ins_with_id(coupon_id)
            coupon_instance = cs_coupon_ins.coupon

            coupon_data = coupon_service.read_coupon_data(coupon_instance)
            coupon_data['target_product_ids'] = json.loads(coupon_data['target_product_ids'])
            target_id = coupon['target_id']

            # Coupon validate
            if cs_coupon_ins.open_id != open_id or cs_coupon_ins.status != 0:
                self.logger_info.info(code.ERROR_3004_COUPON_OWNER_NOT_FOUND)
                error_code = code.ERROR_3004_COUPON_OWNER_NOT_FOUND
                raise BusinessLogicError(get_msg(error_code), error_code, None)

            coupon_validator = CouponInstance.factory(coupon_data['coupon_type'], coupon_data, target_id, product_list)
            if not coupon_validator.check_coupon_rule():
                error_code = code.ERROR_3005_COUPON_APPLY_ERROR
                raise BusinessLogicError(get_msg(error_code), error_code, None)

            discount_amount = coupon_validator.get_discount_price()
            self.discount_price += discount_amount

            coupon_str = payment_util.get_coupon_title_str(
                coupon_instance.name, coupon_instance.is_primary_coupon, target_id, product_list
            )

            coupon_json = {'coupon_title': coupon_str, 'discount_amount': discount_amount,
                           'coupon_type': coupon_instance.coupon_type, 'target_type': coupon_instance.target_type,
                           'target_id': target_id}
            self.coupon_detail.append(coupon_json)

    def get_coupon_detail(self):
        return self.coupon_detail

    def get_discount_price(self):
        return self.discount_price
