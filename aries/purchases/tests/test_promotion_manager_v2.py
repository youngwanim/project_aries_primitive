import logging

from django.test import TestCase

from aries.purchases.manager.promotion_manager import PromotionManager
from aries.purchases.models import Promotion

promotion1_hub_1 = {
    'status': 1,
    'hub_id': 1,
    'type': 0,
    'main_image': 'googlelogo_color_272x92dp-812922.png',
    'main_list_image': 'main_list_image',
    'promotion_list_image': 'promotion_list_image',
    'image_detail': '',
    'main_title': 'SIGN UP PROMOTION',
    'content': 'Coupon promotion for user.',
    'share_image': '',
    'start_date': '2018-01-26',
    'end_date': '2018-11-29',
    'promotion_url': '0',
    'product_list_index': 1,
    'target_type': 0,
    'target_detail': '',
    'target_extra': ''
}

promotion2_hub_1 = {
    'status': 1,
    'hub_id': 1,
    'type': 0,
    'main_image': 'googlelogo_color_272x92dp-812922.png',
    'main_list_image': 'main_list_image',
    'promotion_list_image': 'promotion_list_image',
    'image_detail': '',
    'main_title': 'SIGN UP PROMOTION',
    'content': 'Coupon promotion for user.',
    'share_image': '',
    'start_date': '2018-01-26',
    'end_date': '2018-11-29',
    'promotion_url': '0',
    'product_list_index': 1,
    'target_type': 0,
    'target_detail': '',
    'target_extra': ''
}

promotion1_hub_2 = {
    'status': 1,
    'hub_id': 2,
    'type': 0,
    'main_image': 'googlelogo_color_272x92dp-812922.png',
    'main_list_image': 'main_list_image',
    'promotion_list_image': 'promotion_list_image',
    'image_detail': '',
    'main_title': 'SIGN UP PROMOTION',
    'content': 'Coupon promotion for user.',
    'share_image': '',
    'start_date': '2018-01-26',
    'end_date': '2018-11-29',
    'promotion_url': '0',
    'product_list_index': 1,
    'target_type': 0,
    'target_detail': '',
    'target_extra': ''
}


class TestPromotionManager(TestCase):

    def setUp(self):
        self.promotion1 = Promotion.objects.create(**promotion1_hub_1)
        self.promotion2 = Promotion.objects.create(**promotion2_hub_1)
        self.promotion3 = Promotion.objects.create(**promotion1_hub_2)
        self.language_info = (False, 'default', 'en')
        self.auth_info = (None, None)
        self.logger_info = logging.getLogger('purchases_info')
        self.logger_error = logging.getLogger('purchases_error')

    def test_create_object(self):
        self.assertEqual(Promotion.objects.all().count(), 3)

    def test_promotion_manager(self):
        promotion_manager = PromotionManager(self.logger_info, self.logger_error, self.language_info)
        self.assertEqual(promotion_manager.update_notification_count(self.auth_info), True)

        promotion_result = promotion_manager.get_promotion_list(1, 10, 1, 0)
        promotion_count = promotion_result[0]
        promotion_list = promotion_result[1]
        self.assertEqual(promotion_count, 2)
        self.assertEqual(len(promotion_list), 2)

        promotion_result = promotion_manager.get_promotion_list(1, 10, 2, 0)
        promotion_count = promotion_result[0]
        promotion_list = promotion_result[1]
        self.assertEqual(promotion_count, 1)
        self.assertEqual(len(promotion_list), 1)

        promotion = promotion_manager.get_promotion(self.promotion1.id)
        self.assertEqual(self.promotion1.id, promotion['id'])

        promotion = promotion_manager.get_promotion(self.promotion2.id)
        self.assertEqual(self.promotion2.id, promotion['id'])

        promotion = promotion_manager.get_promotion(self.promotion3.id)
        self.assertEqual(self.promotion3.id, promotion['id'])
