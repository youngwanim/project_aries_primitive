import datetime
import json

from django.core.paginator import Paginator

from aries.common import dateformatter
from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.http_utils.purchase_api_util import update_coupon_count
from aries.common.message_utils import message_mapper
from aries.purchases.common.coupon_util import coupon_operation
from aries.purchases.serializers import CouponInfoSerializer
from aries.purchases.service.coupon_service import CouponService


class CouponManagerV3:
    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def create_coupon(self, open_id, coupon_list):
        coupon_service = CouponService(self.logger_info, self.logger_error)

        start_date = datetime.datetime.today()

        for coupon in coupon_list:
            coupon_id = coupon[0]
            period = coupon[1]
            coupon_code = coupon[2]
            sender_id = coupon[3]

            end_date = start_date + datetime.timedelta(days=period)
            coupon_service.create_customer_coupon(open_id, coupon_id, coupon_code, start_date, end_date, sender_id)

    def create_coupon_pack(self, auth_info, coupon_list, cn_header):
        coupon_service = CouponService(self.logger_info, self.logger_error)
        coupon_id_list = [coupon[0] for coupon in coupon_list]

        if coupon_service.read_customer_coupon_count(auth_info[0], coupon_id_list) != 0:
            raise BusinessLogicError(message_mapper.get(3105, cn_header), 3105)

        start_date = datetime.datetime.today()

        for coupon in coupon_list:
            coupon_id = coupon[0]
            period = coupon[1]
            coupon_code = coupon[2]
            sender_id = coupon[3]

            end_date = start_date + datetime.timedelta(days=period)
            if period >= 1:
                end_date = end_date - datetime.timedelta(days=1)

            coupon_service.create_customer_coupon(auth_info[0], coupon_id, coupon_code, start_date, end_date, sender_id)

        update_coupon_count(self.logger_info, self.logger_error, auth_info[0], auth_info[1], 0, len(coupon_list))

    def create_coupon_with_coupon_list(self, open_id, coupon_list, coupon_code, sender_id):
        coupon_service = CouponService(self.logger_info, self.logger_error)

        start_date = datetime.datetime.today()
        end_date = start_date + datetime.timedelta(days=30)

        for coupon in coupon_list:
            coupon_id = coupon['id']
            coupon_service.create_customer_coupon(open_id, coupon_id, coupon_code, start_date, end_date, sender_id)

    # Coupon create with promotion id
    def create_coupon_with_promotion(self, open_id, coupon_id, coupon_days, coupon_code, sender_id):
        coupon_service = CouponService(self.logger_info, self.logger_error)

        start_date = datetime.datetime.today()
        end_date = start_date + datetime.timedelta(days=coupon_days)

        coupon_service.create_customer_coupon(open_id, coupon_id, coupon_code, start_date, end_date, sender_id)

    def check_issue_coupon_pack(self, auth_info, coupon_list, cn_header):
        coupon_service = CouponService(self.logger_info, self.logger_error)
        coupon_id_list = [coupon[0] for coupon in coupon_list]

        if coupon_service.read_customer_coupon_count(auth_info[0], coupon_id_list) != 0:
            raise BusinessLogicError(message_mapper.get(3105, cn_header), 3105)

    def read_coupon_information(self, coupon_id_list, target_db):
        coupon_service = CouponService(self.logger_info, self.logger_error)
        return coupon_service.read_coupon_list(coupon_id_list, target_db)

    def delete_coupon_pack(self, open_id, coupon_list):
        coupon_service = CouponService(self.logger_info, self.logger_error)
        coupon_service.delete_customer_coupon(open_id, coupon_list)

    def check_auto_issue_coupon(self, open_id):

        pass

    def get_coupon_list(self, open_id, access_token, target_db, page, limit, expired_date):
        coupon_service = CouponService(self.logger_info, self.logger_error)

        # Automatic coupon check
        today = datetime.datetime.today()
        if coupon_service.read_automatic_coupon_count(today) >= 1:
            issued_coupon_count = coupon_service.create_automatic_coupon(today, open_id)
            if issued_coupon_count >= 1:
                coupon_operation(open_id, access_token, 0, issued_coupon_count)

        primary_list = []
        primary_expired_list = []
        additional_list = []
        additional_expired_list = []

        today_date = datetime.datetime.today().date()
        expired_date = today_date - datetime.timedelta(days=expired_date)

        coupon_list = coupon_service.read_customer_coupon_list(open_id, expired_date)
        coupon_count = coupon_list.count()

        paginator = Paginator(coupon_list, limit)

        coupon_list_obj = paginator.page(page).object_list
        coupon_list_data = CouponInfoSerializer(coupon_list_obj, many=True).data

        expired_count = 0

        for cs_coupon in coupon_list_data:
            coupon_id = cs_coupon['coupon']
            coupon_instance = coupon_service.read_coupon_instance_with_id(coupon_id, target_db)
            prev_date = dateformatter.str_to_date(cs_coupon['end_date'])

            if cs_coupon['status'] == 0 and prev_date < today_date:
                cs_coupon['status'] = 2
                expired_coupon = coupon_service.read_customer_coupon_ins_with_id(cs_coupon['id'])
                expired_coupon.status = 2
                expired_coupon.save()
                expired_count += 1

            coupon_data = coupon_service.read_coupon_data(coupon_instance)

            coupon_data['description'] = json.loads(coupon_data['description'])
            coupon_data['target_product_ids'] = json.loads(coupon_data['target_product_ids'])

            del coupon_data['id']

            if cs_coupon['status'] == 1:
                date = cs_coupon['used_date']
                cs_coupon['used_date'] = datetime.datetime.strptime((str(date)[:10]), '%Y-%m-%d').strftime('%Y-%m-%d')
            else:
                cs_coupon['used_date'] = ''

            cs_coupon['coupon'] = coupon_data
            cs_coupon['issue_date'] = cs_coupon['issue_date'].replace('-', '. ')
            cs_coupon['start_date'] = cs_coupon['start_date'].replace('-', '. ')
            cs_coupon['end_date'] = cs_coupon['end_date'].replace('-', '. ')

            if coupon_data['is_primary_coupon']:
                if cs_coupon['status'] == 0:
                    primary_list.append(cs_coupon)
                else:
                    primary_expired_list.append(cs_coupon)
            else:
                if cs_coupon['status'] == 0:
                    additional_list.append(cs_coupon)
                else:
                    additional_expired_list.append(cs_coupon)

        if expired_count >= 1:
            coupon_operation(open_id, access_token, 1, expired_count)

        result_map = {
            'total_count': coupon_count,
            'coupons': primary_list + additional_list + primary_expired_list + additional_expired_list,
            'primary_coupons': primary_list + primary_expired_list,
            'additional_coupons': additional_list + additional_expired_list
        }

        return result_map

    def get_coupon_detail(self, open_id, target_db, access_token):
        coupon_service = CouponService(self.logger_info, self.logger_error)

        # Automatic coupon check
        today = datetime.datetime.today()
        if coupon_service.read_automatic_coupon_count(today) >= 1:
            issued_coupon_count = coupon_service.create_automatic_coupon(today, open_id)
            if issued_coupon_count >= 1:
                coupon_operation(open_id, access_token, 0, issued_coupon_count)

        # After automatic coupon issued
        current_date = dateformatter.get_yyyy_mm_dd_now()
        coupon_qs = coupon_service.read_customer_coupon_qs(open_id, 0, current_date)
        coupon_count = coupon_qs.count()

        result_map = {}

        if coupon_count == 0:
            result_map['coupons'] = json.loads('[]')
            result_map['primary_coupons'] = json.loads('[]')
            result_map['additional_coupons'] = json.loads('[]')
        else:
            customer_coupon_serializer = CouponInfoSerializer(coupon_qs, many=True)
            coupon_data = customer_coupon_serializer.data

            coupon_list = list()
            primary_list = list()
            additional_list = list()

            for coupon in coupon_data:
                coupon_id = coupon['coupon']
                coupon_instance = coupon_service.read_coupon_instance_with_id(coupon_id, target_db)
                coupon_data = coupon_service.read_coupon_data(coupon_instance)
                coupon_data['description'] = json.loads(coupon_data['description'])
                coupon_data['target_product_ids'] = json.loads(coupon_data['target_product_ids'])

                del coupon_data['id']

                if coupon['status'] == 1:
                    date = coupon['used_date']
                    coupon['used_date'] = datetime.datetime.strptime((str(date)[:10]),
                                                                     '%Y-%m-%d').strftime('%Y. %m. %d')
                else:
                    coupon['used_date'] = ''

                coupon['start_date'] = coupon['start_date'].replace('-', '. ')
                coupon['end_date'] = coupon['end_date'].replace('-', '. ')
                coupon['coupon'] = coupon_data

                coupon_list.append(coupon)

                if coupon_data['is_primary_coupon']:
                    primary_list.append(coupon)
                else:
                    additional_list.append(coupon)
            result_map['coupons'] = coupon_list
            result_map['primary_coupons'] = primary_list
            result_map['additional_coupons'] = additional_list

        return result_map
