import datetime
from datetime import date

from django.db import transaction

from aries.common.exceptions.exceptions import BusinessLogicError
from aries.purchases.models import Coupon, CustomerCoupon, AutomaticIssueCoupon, AutomaticIssueResult
from aries.purchases.serializers import CouponSerializer


class CouponService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def read_coupon_instance_with_id(self, coupon_id, target_db='default'):
        try:
            coupon_instance = Coupon.objects.using(target_db).get(id=coupon_id)
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e), None, None)
        else:
            self.result = coupon_instance
        return self.result

    def read_coupon_data(self, coupon_instance):
        try:
            coupon_data = CouponSerializer(coupon_instance).data
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e), None, None)
        else:
            self.result = coupon_data
        return self.result

    def create_customer_coupon(self, open_id, coupon_id, coupon_code, start_date, end_date, sender_id):
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            today = date.today()

            CustomerCoupon.objects.create(
                coupon=coupon,
                coupon_code=coupon_code,
                open_id=open_id,
                issue_date=today,
                start_date=start_date,
                end_date=end_date,
                sender_id=sender_id,
                status=0
            )
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e), None, None)

    def read_customer_coupon_ins_with_id(self, coupon_id):
        try:
            coupon_instance = CustomerCoupon.objects.get(id=coupon_id)
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e), None, None)
        else:
            self.result = coupon_instance
        return self.result

    def read_customer_coupon_list(self, open_id, before_date=None):
        try:
            query_str = {'open_id': open_id, 'status': 0}
            if before_date is not None:
                query_str['end_date__gte'] = before_date
            coupon_list = CustomerCoupon.objects.filter(**query_str)
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e), None, None)
        else:
            self.result = coupon_list
        return self.result

    # Coupon detail
    def read_customer_coupon_qs(self, open_id, status, current_date):
        try:
            coupon_qs = CustomerCoupon.objects.filter(open_id=open_id, status=status, start_date__lte=current_date,
                                                      end_date__gte=current_date)
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e), None, None)
        else:
            self.result = coupon_qs
        return self.result

    # Roulette coupon read only
    def read_customer_coupon_count(self, open_id, coupon_list):
        try:
            coupon_count = CustomerCoupon.objects.filter(open_id=open_id, coupon_id__in=coupon_list).count()
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e))
        else:
            self.result = coupon_count

        return self.result

    # Roulette coupon read only
    def delete_customer_coupon(self, open_id, coupon_list):
        try:
            coupon_id_list = [coupon[0] for coupon in coupon_list]
            customer_coupon_list = CustomerCoupon.objects.filter(open_id=open_id, coupon_id__in=coupon_id_list)
            for coupon in customer_coupon_list:
                coupon.delete()
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e))
        else:
            self.result = True

        return self.result

    # Referral coupon information read
    def read_coupon_list(self, coupon_id_list, target_db='default'):
        try:
            coupon_qs = Coupon.objects.using(target_db).filter(id__in=coupon_id_list)
            coupon_data_list = CouponSerializer(coupon_qs, many=True).data
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e))
        else:
            self.result = coupon_data_list

        return self.result

    # Automatic issue coupon information read
    def read_automatic_coupon_count(self, today):
        try:
            auto_coupon_count = AutomaticIssueCoupon.objects.filter(status=1, issue_start_date__lte=today,
                                                                    issue_end_date__gte=today).count()
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e))
        else:
            self.result = auto_coupon_count

        return self.result

    # Automatic issue coupon query string
    def read_automatic_coupon_qs(self, today):
        try:
            coupon_qs = AutomaticIssueCoupon.objects.filter(status=1, issue_start_date__lte=today,
                                                            issue_end_date__gte=today)
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e))
        else:
            self.result = coupon_qs

        return self.result

    # Automatic coupon issue
    def create_automatic_coupon(self, today, open_id):
        try:
            issued_coupon_count = 0

            auto_coupon_qs = AutomaticIssueCoupon.objects.filter(status=1, issue_start_date__lte=today,
                                                                 issue_end_date__gte=today)

            for auto_coupon in auto_coupon_qs:
                coupon_issue_count = AutomaticIssueResult.objects.filter(open_id=open_id,
                                                                         automatic_issue_coupon=auto_coupon).count()
                if coupon_issue_count == 0:
                    coupon = auto_coupon.coupon
                    coupon_code = auto_coupon.coupon_code

                    period_type = coupon.period_type

                    if period_type == 0 or period_type == 1:
                        start_date = coupon.period_start_date
                        end_date = coupon.period_end_date
                    else:
                        period_day = coupon.period_day
                        start_date = today
                        end_date = today + datetime.timedelta(days=period_day)

                    sender_id = 'vs_admin_automatic'

                    with transaction.atomic():
                        CustomerCoupon.objects.create(
                            coupon=coupon,
                            coupon_code=coupon_code,
                            open_id=open_id,
                            issue_date=today,
                            start_date=start_date,
                            end_date=end_date,
                            sender_id=sender_id,
                            status=0
                        )

                        AutomaticIssueResult.objects.create(
                            open_id=open_id,
                            automatic_issue_coupon=auto_coupon
                        )

                        issued_coupon_count += 1
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e))
        else:
            self.result = issued_coupon_count

        return self.result
