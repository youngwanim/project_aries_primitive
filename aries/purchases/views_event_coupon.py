import json
import logging

from datetime import date

import requests
import aries.purchases.common.event_coupon_util as coupon_util

from django.db.models import F
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import product_util
from aries.common import urlmapper
from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.purchases.manager.coupon_manager_v3 import CouponManagerV3
from aries.purchases.models import EventCoupon, Coupon, CustomerCoupon


logger_info = logging.getLogger('purchases_info')
logger_error = logging.getLogger('purchases_error')


class WelcomeCoupon(APIView):

    SUCCESS = 'Coupon has been issued successfully'
    SUCCESS_CN = '优惠券已成功发放'
    COUPON_NOT_EXISTS = 'This coupon does not exist'
    COUPON_NOT_EXISTS_CN = '该优惠券不存在'
    ALREADY_ISSUED = 'This coupon has already been registered'
    ALREADY_ISSUED_CN = '优惠券已被注册'
    PROMOTION_EXPIRED = 'This promotion code has been expired'
    PROMOTION_EXPIRED_CN = '该活动码已过期'
    COUPON_KIND_LIMITATION = 'This coupon can be registered one time only'
    COUPON_KIND_LIMITATION_CN = '该优惠券只可以注册一次'
    SELF_ISSUED = 'You cannot register a coupon issued from your own account'
    SELF_ISSUED_CN = '您不可以注册从本机发出的优惠券'
    COUPON_COUNT_LIMITATION = 'Sorry, this coupon code has been issued the maximum number of times already'
    COUPON_COUNT_LIMITATION_CN = '抱歉，此优惠券已达到发出最大数量'

    def post(self, request):
        request_data = request.data

        target_db = 'default'
        cn_header = False
        if request.META.get('HTTP_ACCEPT_LANGUAGE'):
            accept_lang = request.META['HTTP_ACCEPT_LANGUAGE']
            if 'zh' in accept_lang:
                target_db = 'aries_cn'
                cn_header = True

        if cn_header:
            self.SUCCESS = self.SUCCESS_CN
        result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS)

        # Request data parsing
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
            logger_info.info(open_id + ':' + access_token)
            serial_number = request_data['serial_number']
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid(Token or Open id)')
            return Response(result.get_response(), result.get_code())

        # Validation check
        try:
            payload = {'open_id': open_id, 'access_token': access_token}
            url = urlmapper.get_url('USER_VALIDATION')
            response = requests.post(url, json=payload)

            if response.status_code != code.ARIES_200_SUCCESS:
                result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authorization error')
                return Response(result.get_response(), result.get_code())

            promotion_coupon_count = EventCoupon.objects.filter(serial_number=serial_number).count()

            if promotion_coupon_count <= 0:
                if cn_header:
                    self.COUPON_NOT_EXISTS = self.COUPON_NOT_EXISTS_CN
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, self.COUPON_NOT_EXISTS)
                return Response(result.get_response(), result.get_code())

            promotion_coupon = EventCoupon.objects.get(serial_number=serial_number)
            event_type = promotion_coupon.event_type

            if promotion_coupon.name == open_id:
                if cn_header:
                    self.SELF_ISSUED = self.SELF_ISSUED_CN
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, self.SELF_ISSUED)
                return Response(result.get_response(), result.get_code())

            coupon_code = promotion_coupon.coupon_code
            customer_coupon_count = CustomerCoupon.objects.filter(open_id=open_id, coupon_code=coupon_code).count()

            if customer_coupon_count >= 1 and (event_type == 0 or event_type == 2):
                if cn_header:
                    self.COUPON_KIND_LIMITATION = self.COUPON_KIND_LIMITATION_CN
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, self.COUPON_KIND_LIMITATION)
                return Response(result.get_response(), result.get_code())

            if promotion_coupon.issued and event_type != 2:
                if cn_header:
                    self.ALREADY_ISSUED = self.ALREADY_ISSUED_CN
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, self.ALREADY_ISSUED)
                return Response(result.get_response(), result.get_code())

            if event_type == 2 and promotion_coupon.issued_limitation != 0 \
                    and promotion_coupon.issued_count+1 > promotion_coupon.issued_limitation:
                if cn_header:
                    self.COUPON_COUNT_LIMITATION = self.COUPON_COUNT_LIMITATION_CN
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, self.COUPON_COUNT_LIMITATION)
                return Response(result.get_response(), result.get_code())

            if not promotion_coupon.has_coupon_pack:
                today = date.today()
                coupon_count = Coupon.objects.using(target_db).filter(
                    id=promotion_coupon.coupon_id,
                    period_start_date__lte=today,
                    period_end_date__gte=today
                ).count()

                if coupon_count <= 0:
                    if cn_header:
                        self.PROMOTION_EXPIRED = self.PROMOTION_EXPIRED_CN
                    result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, self.PROMOTION_EXPIRED)
                    return Response(result.get_response(), result.get_code())

        except Exception as e:
            print(e)
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
            return Response(result.get_response(), result.get_code())

        # Coupon create
        try:
            coupon_id_list = list()
            today = date.today()

            if promotion_coupon.has_coupon_pack:
                coupon_pack_list = json.loads(promotion_coupon.coupon_pack)
                for coupon_item in coupon_pack_list:
                    coupon = Coupon.objects.using(target_db).get(id=coupon_item['id'])
                    coupon_dates = product_util.get_coupon_date(
                        coupon.period_type, coupon.period_day, coupon.period_start_date, coupon.period_end_date
                    )

                    for index in range(coupon_item['quantity']):
                        customer_coupon = CustomerCoupon.objects.create(
                            coupon=coupon,
                            coupon_code=coupon_code,
                            open_id=open_id,
                            issue_date=today,
                            start_date=coupon_dates[0],
                            end_date=coupon_dates[1],
                            sender_id=promotion_coupon.name,
                            status=0
                        )
                        coupon_id_list.append(customer_coupon.id)
            else:
                coupon = Coupon.objects.using(target_db).get(id=promotion_coupon.coupon_id)
                coupon_dates = product_util.get_coupon_date(
                    coupon.period_type, coupon.period_day, coupon.period_start_date, coupon.period_end_date
                )
                created_coupon_count = promotion_coupon.coupon_count

                for index in range(created_coupon_count):
                    customer_coupon = CustomerCoupon.objects.create(
                        coupon=coupon,
                        coupon_code=coupon_code,
                        open_id=open_id,
                        issue_date=today,
                        start_date=coupon_dates[0],
                        end_date=coupon_dates[1],
                        sender_id=promotion_coupon.name,
                        status=0
                    )
                    coupon_id_list.append(customer_coupon.id)

            coupon_count = len(coupon_id_list)

            if promotion_coupon.issued_limitation != 0:
                promotion_coupon.issued_count = F('issued_count') + 1

            promotion_coupon.issued = True
            promotion_coupon.issued_date = today
            promotion_coupon.issued_user_open_id = open_id
            promotion_coupon.issued_customer_coupon_id = str(coupon_id_list)
            promotion_coupon.save()

            # Coupon count up
            headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}
            url = urlmapper.get_url('USER_NOTIFICATION') + '/coupon/0/' + str(coupon_count)
            response = requests.get(url, headers=headers)
            logger_info.info(response.text)

            # After coupon issued, response current coupon list
            default_page = 1
            default_limit = 100
            expired_date = 7

            coupon_manager = CouponManagerV3(logger_info, logger_error)
            coupon_list = coupon_manager.get_coupon_list(
                open_id, access_token, target_db, default_page, default_limit, expired_date)

            result.set('coupon_id', coupon_id_list)
            result.set_map(coupon_list)
            return Response(result.get_response(), result.get_code())
        except Exception as e:
            print(e)
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
            return Response(result.get_response(), result.get_code())


class DownloadEventCheck(APIView):
    coupon_pack_info = [
        (44, 7, 'APP_DOWN_180531', 'ADMIN'),
        (45, 14, 'APP_DOWN_180531', 'ADMIN'),
        (46, 21, 'APP_DOWN_180531', 'ADMIN'),
        (47, 30, 'APP_DOWN_180531', 'ADMIN')
    ]

    def get(self, request):
        auth_info = header_parser.parse_authentication(request)
        language_info = header_parser.parse_language(request.META)

        try:
            coupon_util.auth_info_validator(auth_info, language_info[0])
            coupon_util.os_info_validator(request)

            coupon_manager = CouponManagerV3(logger_info, logger_error)
            coupon_manager.check_issue_coupon_pack(auth_info, self.coupon_pack_info, language_info[0])
        except BusinessLogicError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message)
            result.set_error(err_code)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())

    def delete(self, request):
        auth_info = header_parser.parse_authentication(request)
        language_info = header_parser.parse_language(request.META)

        try:
            coupon_util.auth_info_validator(auth_info, language_info[0])
            coupon_util.os_info_validator(request)

            coupon_manager = CouponManagerV3(logger_info, logger_error)
            coupon_manager.delete_coupon_pack(auth_info[0], self.coupon_pack_info)
        except BusinessLogicError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message)
            result.set_error(err_code)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())


class PromotionCoupon(APIView):
    coupon_pack_info = [
        (44, 7, 'APP_DOWN_180612', 'ADMIN'),
        (45, 14, 'APP_DOWN_180612', 'ADMIN'),
        (46, 21, 'APP_DOWN_180612', 'ADMIN'),
        (47, 30, 'APP_DOWN_180612', 'ADMIN')
    ]
    r_code = 'ROULETTE1805'

    def get(self, request):
        auth_info = header_parser.parse_authentication(request)
        language_info = header_parser.parse_language(request.META)

        try:
            coupon_util.auth_info_validator(auth_info, language_info[0])
            coupon_util.os_info_validator(request)

            coupon_manager = CouponManagerV3(logger_info, logger_error)
            coupon_manager.create_coupon_pack(auth_info, self.coupon_pack_info, language_info[0])
        except BusinessLogicError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message)
            result.set_error(err_code)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        language_info = header_parser.parse_language(request.META)

        try:
            coupon_data = coupon_util.event_coupon_validator(request, language_info[0])

            open_id = coupon_data['open_id']
            coupon_id = coupon_data['coupon_id']

            coupon_list = [(coupon_id, 0, self.r_code, 'ADMIN')]
            coupon_manager = CouponManagerV3(logger_info, logger_error)

            coupon_manager.create_coupon(open_id, coupon_list)
        except BusinessLogicError as instance:
            message = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())
