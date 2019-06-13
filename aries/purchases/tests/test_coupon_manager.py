import datetime
import logging

from django.test import TestCase

from aries.purchases.manager.coupon_manager_v3 import CouponManagerV3
from aries.purchases.models import Coupon, CustomerCoupon
from aries.purchases.service.coupon_service import CouponService

coupon1 = {
    'status': 0,
    'description': '["Days to be processed"]',
    'image': '10-dollar-coupon.png',
    'delivery_detail': 0,
    'target_detail': '',
    'is_time_coupon': False,
    'start_time': None,
    'is_primary_coupon': True,
    'cash_discount': 47.0,
    'target_type': 200,
    'end_time': None,
    'coupon_type': 0,
    'target_max': 0,
    'target_product_ids': '[138,139]',
    'cash_maximum': 0.0,
    'target_min': 0,
    'cash_minimum': 102.0,
    'name': 'SPRING COUPON ONE',
    'cash_type': 0
}

coupon2 = {
    'status': 0,
    'description': '["Days to be processed"]',
    'image': '10-dollar-coupon.png',
    'delivery_detail': 0,
    'target_detail': '',
    'is_time_coupon': False,
    'start_time': None,
    'is_primary_coupon': True,
    'cash_discount': 47.0,
    'target_type': 200,
    'end_time': None,
    'coupon_type': 0,
    'target_max': 0,
    'target_product_ids': '[138,139]',
    'cash_maximum': 0.0,
    'target_min': 0,
    'cash_minimum': 102.0,
    'name': 'SPRING COUPON TWO',
    'cash_type': 0
}


class TestCouponManager(TestCase):
    def setUp(self):
        self.language_info = (False, 'default', 'en')
        self.auth_info = (None, None)
        self.logger_info = logging.getLogger('purchases_info')
        self.logger_error = logging.getLogger('purchases_error')
        self.coupon_manager = CouponManagerV3(self.logger_info, self.logger_error)

    def test_coupon_service(self):
        coupon_one = Coupon.objects.create(**coupon1)
        coupon_two = Coupon.objects.create(**coupon2)

        self.assertNotEqual(coupon_one, None)
        self.assertNotEqual(coupon_two, None)

        customer_coupon_count = CustomerCoupon.objects.all().count()
        self.assertEqual(customer_coupon_count, 0)

        # open_id, coupon_id, coupon_code, start_date, end_date, sender_id
        today = datetime.datetime.today()

        coupon_service = CouponService(self.logger_info, self.logger_error)
        coupon_service.create_customer_coupon(
            'AAA', coupon_one.id, 'TEST_COUPON1', today, today, 'ADMIN'
        )

        coupon_service.create_customer_coupon(
            'AAA', coupon_two.id, 'TEST_COUPON2', today, today, 'ADMIN'
        )

        customer_coupon_count = CustomerCoupon.objects.all().count()
        self.assertEqual(customer_coupon_count, 2)
        self.assertEqual(coupon_service.read_customer_coupon_ins_with_id(coupon_one.id).id, coupon_one.id)

        customer_coupon_list = coupon_service.read_customer_coupon_list('AAA')
        self.assertEqual(len(customer_coupon_list), 2)

        coupon_pack_info = [
            (1, 7, 'APP_DOWN_180612', 'ADMIN'),
            (2, 14, 'APP_DOWN_180612', 'ADMIN'),
        ]
        self.assertEqual(coupon_service.read_customer_coupon_count('AAA', coupon_pack_info), 2)

        coupon_ins = coupon_service.read_coupon_instance_with_id(coupon_one.id)
        self.assertEqual(coupon_ins.id, coupon_one.id)

        coupon_data = coupon_service.read_coupon_data(coupon_ins)
        self.assertNotEqual(coupon_data, None)
        self.assertEqual(coupon_data['id'], coupon_ins.id)

        coupon_qs = coupon_service.read_customer_coupon_qs('AAA', 0, today)
        self.assertEqual(len(coupon_qs), 2)

        coupon_pack_info = [
            (1, 7, 'APP_DOWN_180612', 'ADMIN'),
            (2, 14, 'APP_DOWN_180612', 'ADMIN'),
        ]

        coupon_service.delete_customer_coupon('AAA', coupon_pack_info)
        customer_coupon_count = CustomerCoupon.objects.all().count()
        self.assertEqual(customer_coupon_count, 0)
