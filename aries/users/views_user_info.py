import json

import logging
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import dateformatter
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.users.manager.user_manager import UserManager
from aries.users.models import User, UserNews, UserNotifyInfo
from aries.users.serializers import UserNewsSerializer

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class MyNews(APIView):

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]

            language_info = header_parser.parse_language(request.META)
            cn_header = language_info[0]

            page = int(request.GET.get('page'))
            limit = int(request.GET.get('limit'))
            user = User.objects.get(access_token=access_token, open_id=open_id)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # My News part
        try:
            user_news_list = UserNews.objects.filter(user=user)
            user_news_count = user_news_list.count()
            paginator = Paginator(user_news_list, limit)

            user_news = paginator.page(page).object_list
            serializer = UserNewsSerializer(user_news, many=True)
            news_data = serializer.data

            user_manager = UserManager()
            news_list = [user_manager.parse_my_news(news, cn_header) for news in news_data]

            result.set('total_count', user_news_count)
            result.set('news', news_list)
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())


class MyNewsDetail(APIView):

    def put(self, request, news_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            user = User.objects.get(access_token=access_token, open_id=open_id)
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Get news object
        try:
            user_news = UserNews.objects.get(user=user, id=news_id)

            # Check if readable content
            if not user_news.has_read:
                user_news.has_read = True
                user_news.save()

            notify_info = UserNotifyInfo.objects.get(user=user)
            current_count = notify_info.news_count - 1

            if current_count <= 0:
                notify_info.news_count = 0
                notify_info.has_news = False
            else:
                notify_info.news_count = current_count

            notify_info.save()

            news_serializer = UserNewsSerializer(user_news)
            news_data = news_serializer.data
            news_data['content'] = json.loads(news_data['content'])
            news_data['created_date'] = dateformatter.get_yymmdd_with_ampm(news_data['created_date'])

            del news_data['user']

            result.set('news', news_data)
            return Response(result.get_response(), result.get_code())

        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request invalid')
            return Response(result.get_response(), result.get_code())

