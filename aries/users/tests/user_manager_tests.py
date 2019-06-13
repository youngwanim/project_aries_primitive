import json
import copy

from django.conf import settings
from django.test import TestCase

from aries.common import dateformatter
from aries.users.manager.user_manager import UserManager
from aries.users.models import User, UserNews, UserInfo, UserNotifyInfo
from aries.users.serializers import UserNewsSerializer


class UserManagerTest(TestCase):

    open_id_dummy = 'DD2E62164AE99E8FA6865383'
    mdn = '01021290054'
    name = 'shanghaiman'
    mdn_verification = True
    access_token = '621D85EAAE4A1978F88C7968A3E15EB9A0371463209AFDE8'
    order_id = 'S20170826AFFZ'

    def setUp(self):
        settings.DEBUG = True

        self.user_manager = UserManager()

        # Dummy data setting
        self.user_instance = User.objects.create(
            open_id=self.open_id_dummy,
            mdn=self.mdn,
            name=self.name,
            mdn_verification=self.mdn_verification,
            access_token=self.access_token,
            parent_type=0,
            push_agreement='Y'
        )

        self.user_info_instance = UserInfo.objects.create(
            user=self.user_instance,
            number_of_logon=0,
            os_type=0
        )

        self.user_notify_info = UserNotifyInfo.objects.create(
            user=self.user_instance
        )

    def test_user_manager_create(self):
        user_count = User.objects.filter(open_id=self.open_id_dummy).count()
        self.assertIsNotNone(self.user_manager)
        self.assertIsNotNone(self.user_instance)
        self.assertIsNotNone(self.user_info_instance)
        self.assertIsNotNone(self.user_notify_info)
        self.assertEqual(user_count, 1)

    def test_user_manager_news(self):
        news_count = UserNews.objects.filter(user=self.user_instance).count()
        self.assertEqual(0, news_count)

        self.user_manager.add_my_news(self.open_id_dummy, 2, self.order_id)
        news_count = UserNews.objects.filter(user=self.user_instance).count()

        self.assertEqual(1, news_count)

        news_instance = UserNews.objects.filter(user=self.user_instance).order_by('-id')[0]
        news_data = UserNewsSerializer(news_instance).data
        compare_data = copy.deepcopy(news_data)

        result_data = self.user_manager.parse_my_news(compare_data, False)

        news_data['content'] = json.loads(news_data['content'])
        news_data['created_date'] = dateformatter.get_yymmdd_with_ampm(news_data['created_date'])

        del news_data['user']
        del news_data['title_cn']
        del news_data['content_cn']
        del news_data['detail_cn']

        self.assertEqual(news_data, result_data)

    def test_user_manager_order_complete(self):
        result = self.user_manager.send_order_complete_msg(self.open_id_dummy, self.access_token, self.order_id)
        self.assertEqual(result.get_code(), 200)

    def test_user_manager_order_canceled(self):
        result = self.user_manager.send_order_cancel_msg(self.open_id_dummy, self.access_token, self.order_id)
        self.assertEqual(result.get_code(), 200)
