import json
import logging

from django.core.paginator import Paginator
from django.db.models import F
from django.db.models import Q

from aries.common import code
from aries.common import dateformatter
from aries.common.models import ResultResponse
from aries.common.sms import SmsSingleSender
from aries.common.utils import message_util
from aries.common.utils import push_util
from aries.common.utils import user_util
from aries.common.utils.push_util import PushInstance
from aries.users.models import User, UserInfo, UserNews, UserNotifyInfo
from aries.users.serializers import UserSerializer

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class UserManager:

    OS_WECHAT = -1
    OS_ANDROID = 0
    OS_IOS = 1

    def send_order_complete_msg(self, open_id, access_token, order_id):
        try:
            user_count = User.objects.filter(open_id=open_id).count()

            if user_count == 0 or order_id is None:
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'User not found')
                return result

            user = User.objects.get(open_id=open_id)
            user_info = UserInfo.objects.get(user=user)

            mdn = user.mdn
            user_os_type = user_info.os_type
            agreement = user_util.get_user_agreement(user.push_agreement)
            cn_header = user_util.get_user_locale(user.locale)

            # User news add
            # self.add_my_news(open_id, message_util.NEWS_ORDER_SUCCESS, order_id)

            if user_os_type == self.OS_WECHAT or not agreement:
                # SMS section
                tencent_app_id = '1400040133'
                tencent_app_key = '060b61830d919d6ec773fcd18f0171e7'

                single_sender = SmsSingleSender(tencent_app_id, tencent_app_key)

                nation = '82'
                if cn_header:
                    templ_id = 59095
                else:
                    templ_id = 59094

                # message = message_util.get_order_success_push(cn_header)
                # params = [message, '1']
                params = []

                result = single_sender.send_with_param(nation, mdn, templ_id, params, '', '', '')
                logger_info.info(result)
            elif (user_os_type == self.OS_ANDROID or user_os_type == self.OS_IOS) and agreement:
                # Push section
                push_instance = PushInstance.factory(
                    push_util.PUSH_ORDER_COMPLETE,
                    user_os_type,
                    order_id,
                    open_id,
                    access_token,
                    cn_header
                )

                response = push_instance.get_response()
                logger_info.info(response.text)

            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            return result
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
            return result

    def send_order_cancel_msg(self, open_id, access_token, order_id):
        try:
            user_count = User.objects.filter(open_id=open_id).count()

            if user_count == 0 or order_id is None:
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'User not found')
                return result

            user = User.objects.get(open_id=open_id)
            user_info = UserInfo.objects.get(user=user)

            mdn = user.mdn
            user_os_type = user_info.os_type
            agreement = user_util.get_user_agreement(user.push_agreement)
            cn_header = user_util.get_user_locale(user.locale)

            # User news add
            # self.add_my_news(open_id, message_util.NEWS_ORDER_CANCEL, order_id)
            message = message_util.get_order_cancel_push(cn_header)

            if user_os_type == self.OS_WECHAT or not agreement:
                # SMS section
                tencent_app_id = '1400040133'
                tencent_app_key = '060b61830d919d6ec773fcd18f0171e7'

                single_sender = SmsSingleSender(tencent_app_id, tencent_app_key)

                nation = '82'
                if cn_header:
                    templ_id = 59099
                else:
                    templ_id = 59097

                # params = [message, '1']
                params = []

                result = single_sender.send_with_param(nation, mdn, templ_id, params, '', '', '')
                logger_info.info(result)
            elif (user_os_type == self.OS_ANDROID or user_os_type == self.OS_IOS) and agreement:
                # Push section
                push_instance = PushInstance.factory(
                    push_util.PUSH_ORDER_CANCEL,
                    user_os_type,
                    order_id,
                    open_id,
                    access_token,
                    cn_header
                )

                response = push_instance.get_response()
                logger_info.info(response.text)

            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            return result

        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
            return result

    def parse_my_news(self, news_data, cn_header):
        if cn_header:
            news_data['title'] = news_data['title_cn']
            news_data['content'] = json.loads(news_data['content_cn'])
            news_data['detail'] = news_data['detail_cn']
        else:
            news_data['content'] = json.loads(news_data['content'])

        news_data['created_date'] = dateformatter.get_yymmdd_with_ampm(news_data['created_date'])

        del news_data['user']
        del news_data['title_cn']
        del news_data['content_cn']
        del news_data['detail_cn']

        return news_data

    def add_my_news(self, open_id, news_type, detail):
        user = User.objects.get(open_id=open_id)
        result = message_util.get_mynews_message(news_type)

        UserNews.objects.create(
            user=user,
            type=news_type,
            title=result[2],
            content=result[3],
            title_cn=result[0],
            content_cn=result[1],
            detail=detail,
            detail_cn=detail
        )

        user_notify_info = UserNotifyInfo.objects.get(user=user)
        user_notify_info.has_news = True
        user_notify_info.news_count = F('news_count') + 1
        user_notify_info.save()

    def get_user_list(self, request):
        access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        query_string = request.GET.get('query', None)

        filter_str = {}

        if query_string is None:
            users = User.objects.filter(**filter_str)
        else:
            users = User.objects.filter(
                Q(name__icontains=query_string) |
                Q(mdn__icontains=query_string) |
                Q(access_token__icontains=query_string) |
                Q(open_id__icontains=query_string)
            )

        paginator = Paginator(users, limit)
        user_objects = paginator.page(page).object_list
        serializer = UserSerializer(user_objects, many=True)
        user_data = serializer.data

        users_list = [user['open_id'] for user in user_data]
        search_list = [{'id': index+((page-1)*limit)+1, 'detail': users_list[index]}
                       for index in range(len(users_list))]

        return search_list
