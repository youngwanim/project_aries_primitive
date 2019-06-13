import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.models import ResultResponse
from aries.users.common.user_func import check_has_event
from aries.users.models import User, UserNotifyInfo
from aries.users.serializers import UserNotifyInfoSerializer

logger_info = logging.getLogger('users_info')
logger_error = logging.getLogger('users_error')


class NotifyInfoDetail(APIView):

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        try:
            # Get access token
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            user = User.objects.get(access_token=access_token, open_id=open_id)
            user_notify_info = UserNotifyInfo.objects.get(user=user)

            # Check event playable
            has_event = check_has_event(open_id, access_token)
            user_notify_info.has_event = has_event
            user_notify_info.save()
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Auth token or user not found')
            return Response(result.get_response(), result.get_code())

        serializer = UserNotifyInfoSerializer(user_notify_info)
        notify_info_data = serializer.data
        del notify_info_data['id']
        del notify_info_data['user']

        result.set('notification_info', notify_info_data)
        return Response(result.get_response(), result.get_code())

    def put(self, request):
        request_data = request.data
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            user = User.objects.get(access_token=access_token, open_id=open_id)
            user_notify_info = UserNotifyInfo.objects.get(user=user)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Auth token or user not found')
            return Response(result.get_response(), result.get_code())

        # Change data
        serializer = UserNotifyInfoSerializer(user_notify_info, data=request_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(result.get_response(), result.get_code())
        else:
            print(serializer.errors)
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())


class NotifyInfoHandler(APIView):

    coupon = 'coupon'
    upcoming = 'upcoming'
    news = 'news'
    promotion = 'promotion'
    referral = 'referral'

    def get(self, request, domain, operator, count):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            user = User.objects.get(access_token=access_token, open_id=open_id)
            user_notify_info = UserNotifyInfo.objects.get(user=user)
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Auth token or user not found')
            return Response(result.get_response(), result.get_code())

        # Process handler
        try:
            if domain == self.coupon:
                if int(operator) == 0:
                    user_notify_info.coupon_count += int(count)
                else:
                    user_notify_info.coupon_count -= int(count)
                    if user_notify_info.coupon_count < 0:
                        user_notify_info.coupon_count = 0
            elif domain == self.upcoming:
                if int(operator) == 0:
                    user_notify_info.upcoming_order_count += int(count)
                    user_notify_info.has_upcoming_order = True
                else:
                    user_notify_info.upcoming_order_count -= int(count)
                    if user_notify_info.upcoming_order_count < 0:
                        user_notify_info.upcoming_order_count = 0
                        user_notify_info.has_upcoming_order = False
            elif domain == self.news:
                if int(operator) == 0:
                    user_notify_info.news_count += int(count)
                    user_notify_info.has_news = True
                else:
                    user_notify_info.news_count -= int(count)
                    if user_notify_info.news_count < 0:
                        user_notify_info.news_count = 0
                        user_notify_info.has_news = False
            elif domain == self.promotion:
                if int(operator) == 0:
                    user_notify_info.has_promotion = True
                else:
                    user_notify_info.has_promotion = False
            elif domain == self.referral:
                if int(operator) == 0:
                    user_notify_info.has_referral_event = True
                else:
                    user_notify_info.has_referral_event = False

            user_notify_info.save()
            return Response(result.get_response(), result.get_code())
        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Error : ' + str(e))
            return Response(result.get_response(), result.get_code())
