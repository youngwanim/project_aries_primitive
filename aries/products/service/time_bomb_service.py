import datetime
import json

from django.db import transaction

from aries.common.exceptions.exceptions import BusinessLogicError
from aries.products.common.time_bomb_func import check_status, get_time_bomb_platform_query
from aries.products.models import TimeBomb, TimeBombContent, TimeBombDiscountInfo
from aries.products.serializers import TimeBombSerializer, TimeBombContentSerializer, TimeBombAdminSerializer, \
    TimeBombDiscountInfoSerializer


class TimeBombService:

    STATUS_INACTIVATED = 0
    STATUS_ACTIVATED = 1

    STATUS_AVAILABLE = 1
    STATUS_SOLD_OUT = 2
    STATUS_TIME_EXPIRED = 3

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def check_time_bomb_now(self, hub_id, os_type):
        try:
            current_date = datetime.datetime.today()
            query_str = get_time_bomb_platform_query(os_type)
            query_str['hub'] = hub_id
            query_str['status'] = self.STATUS_ACTIVATED
            query_str['start_time__lte'] = current_date
            query_str['end_time__gte'] = current_date

            time_bomb = TimeBomb.objects.filter(**query_str)
        except Exception as e:
            msg = '[TimeBombService][check_time_bomb_now][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = time_bomb.exists()

        return self.result

    def check_time_bomb_with_date(self, hub, start_time, end_time):
        try:
            time_bomb_qs = TimeBomb.objects.filter(
                hub=hub,
                status=self.STATUS_ACTIVATED,
                start_time__lte=start_time,
                end_time__gte=end_time
            )
        except Exception as e:
            msg = '[TimeBombService][check_time_bomb_with_date][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = time_bomb_qs.exists()

        return self.result

    def get_current_time_bomb_id(self, hub_id, os_type):
        try:
            current_date = datetime.datetime.today()
            query_str = get_time_bomb_platform_query(os_type)
            query_str['hub'] = hub_id
            query_str['status'] = self.STATUS_ACTIVATED
            query_str['start_time__lte'] = current_date
            query_str['end_time__gte'] = current_date

            time_bomb = TimeBomb.objects.filter(**query_str)
        except Exception as e:
            msg = '[TimeBombService][get_current_time_bomb_id][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            if time_bomb.exists():
                self.result = time_bomb[0].id

        return self.result

    def get_current_time_bomb_after(self, hub_id, os_type, has_after):
        try:
            current_date = datetime.datetime.today()

            if has_after:
                after_date = current_date - datetime.timedelta(minutes=30)
            else:
                after_date = current_date

            query_str = get_time_bomb_platform_query(os_type)
            query_str['hub'] = hub_id
            query_str['status'] = self.STATUS_ACTIVATED
            query_str['start_time__lte'] = current_date
            query_str['end_time__gte'] = after_date

            time_bomb = TimeBomb.objects.filter(**query_str)
        except Exception as e:
            msg = '[TimeBombService][get_current_time_bomb_after][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            if time_bomb.count() == 1:
                self.result = time_bomb[0].id

        return self.result

    def read_time_bomb_products(self, time_bomb_id):
        try:
            time_bomb_discounts = TimeBombDiscountInfo.objects.filter(time_bomb=time_bomb_id)
            product_list = [discount.product_id for discount in time_bomb_discounts]
        except Exception as e:
            msg = '[TimeBombService][read_time_bomb_products][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = product_list

        return self.result

    def read_time_bomb_with_id(self, time_bomb_id, lang_type, os_type):
        try:
            time_bomb = TimeBomb.objects.get(id=time_bomb_id)
            time_bomb_content = TimeBombContent.objects.get(time_bomb=time_bomb, language_type=lang_type)

            time_bomb_data = TimeBombSerializer(time_bomb).data
            content_data = TimeBombContentSerializer(time_bomb_content).data

            # Status check
            start_time = time_bomb.start_time.time()
            end_time = time_bomb.end_time.time()

            if not self.check_time_bomb_now(time_bomb.hub.code, os_type):
                status = self.STATUS_TIME_EXPIRED
            elif check_status(start_time, end_time):
                status = self.STATUS_AVAILABLE
                time_bomb_data['products'] = self.read_time_bomb_products(time_bomb_id)
            else:
                status = self.STATUS_TIME_EXPIRED

            del content_data['id']
            time_bomb_data['status'] = status
            time_bomb_data.update(content_data)
        except Exception as e:
            msg = '[TimeBombService][read_time_bomb_with_id][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = time_bomb_data

        return self.result

    def read_time_bomb_list(self, hub_id):
        try:
            time_bomb_qs = TimeBomb.objects.filter(hub=hub_id)
            time_bomb_list = []

            for time_bomb in time_bomb_qs:
                time_bomb_data = TimeBombAdminSerializer(time_bomb).data
                time_bomb_list.append(time_bomb_data)
        except Exception as e:
            msg = '[TimeBombService][read_time_bomb_list][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = time_bomb_list

        return self.result

    def read_time_bomb_with_id_admin(self, time_bomb_id):
        try:
            time_bomb = TimeBomb.objects.get(id=time_bomb_id)
            tb_content_en = TimeBombContent.objects.get(time_bomb=time_bomb, language_type=0)
            tb_content_cn = TimeBombContent.objects.get(time_bomb=time_bomb, language_type=1)
            tb_discount_info = TimeBombDiscountInfo.objects.filter(time_bomb=time_bomb)
            discount_info = TimeBombDiscountInfoSerializer(tb_discount_info, many=True).data

            time_bomb_data = TimeBombAdminSerializer(time_bomb).data
            time_bomb_data['time_bomb_content_en'] = TimeBombContentSerializer(tb_content_en).data
            time_bomb_data['time_bomb_content_cn'] = TimeBombContentSerializer(tb_content_cn).data
            time_bomb_data['time_bomb_discount_info'] = discount_info
        except Exception as e:
            msg = '[TimeBombService][read_time_bomb_with_id][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = time_bomb_data

        return self.result

    def create_time_bomb(self, time_bomb, tb_content_en, tb_content_cn, discount_info_list):
        try:
            # Time change and verification
            start_time = datetime.datetime.fromtimestamp(time_bomb['start_time'])
            end_time = datetime.datetime.fromtimestamp(time_bomb['end_time'])

            time_bomb['start_time'] = start_time
            time_bomb['end_time'] = end_time
            time_bomb['start_date'] = start_time.date()
            time_bomb['end_date'] = end_time.date()

            tb_content_en['language_type'] = 0
            tb_content_cn['language_type'] = 1

            with transaction.atomic():
                # Create time bomb
                time_bomb_ins = TimeBomb.objects.create(**time_bomb)

                # Setting created time bomb
                tb_content_en['time_bomb'] = time_bomb_ins
                tb_content_cn['time_bomb'] = time_bomb_ins
                tb_content_en['guide_content'] = json.dumps(tb_content_en['guide_content'])
                tb_content_cn['guide_content'] = json.dumps(tb_content_cn['guide_content'])

                # Create time bomb content
                TimeBombContent.objects.create(**tb_content_en)
                TimeBombContent.objects.create(**tb_content_cn)

                # Create discount info
                for discount_info in discount_info_list:
                    discount_info['time_bomb'] = time_bomb_ins
                    TimeBombDiscountInfo.objects.create(**discount_info)
        except Exception as e:
            msg = '[TimeBombService][create_time_bomb][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = time_bomb_ins.id

        return self.result

    def update_time_bomb(self, time_bomb_id, time_bomb, tb_content_en, tb_content_cn, discount_info_list):
        try:
            # Time change and verification
            start_time = datetime.datetime.fromtimestamp(time_bomb['start_time'])
            end_time = datetime.datetime.fromtimestamp(time_bomb['end_time'])

            time_bomb['start_time'] = start_time
            time_bomb['end_time'] = end_time
            time_bomb['start_date'] = start_time.date()
            time_bomb['end_date'] = end_time.date()

            tb_content_en['language_type'] = 0
            tb_content_cn['language_type'] = 1

            with transaction.atomic():
                # Update time bomb
                time_bomb_ins = TimeBomb.objects.get(id=time_bomb_id)
                time_bomb_serializer = TimeBombSerializer(time_bomb_ins, data=time_bomb)

                if time_bomb_serializer.is_valid():
                    time_bomb_serializer.save()
                else:
                    raise BusinessLogicError(time_bomb_serializer.errors, None, None)

                # Update time bomb content
                tb_content_en_ins = TimeBombContent.objects.get(time_bomb=time_bomb_ins, language_type=0)
                tb_content_cn_ins = TimeBombContent.objects.get(time_bomb=time_bomb_ins, language_type=1)

                tb_content_en['guide_content'] = json.dumps(tb_content_en['guide_content'])
                tb_content_cn['guide_content'] = json.dumps(tb_content_cn['guide_content'])

                tb_content_serializer = TimeBombContentSerializer(tb_content_en_ins, data=tb_content_en, partial=True)

                if tb_content_serializer.is_valid():
                    tb_content_serializer.save()
                else:
                    raise BusinessLogicError(tb_content_serializer.errors, None, None)

                tb_content_serializer = TimeBombContentSerializer(tb_content_cn_ins, data=tb_content_cn, partial=True)

                if tb_content_serializer.is_valid():
                    tb_content_serializer.save()
                else:
                    raise BusinessLogicError(tb_content_serializer.errors, None, None)

                # Create discount info
                discount_info_qs = TimeBombDiscountInfo.objects.filter(time_bomb=time_bomb_ins)
                discount_info_qs.delete()

                for discount_info in discount_info_list:
                    if 'id' in discount_info:
                        del discount_info['id']

                    discount_info['time_bomb'] = time_bomb_ins
                    TimeBombDiscountInfo.objects.create(**discount_info)
        except Exception as e:
            msg = '[TimeBombService][update_time_bomb][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = time_bomb_ins.id

        return self.result

    def delete_time_bomb(self, time_bomb_id):
        try:
            # Update time bomb
            time_bomb_ins = TimeBomb.objects.get(id=time_bomb_id)
            time_bomb_ins.delete()
        except Exception as e:
            msg = '[TimeBombService][delete_time_bomb][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = True

        return self.result

    def set_time_bomb_activate(self, time_bomb_id, activation):
        inactivation_status = 0
        activation_status = 1

        try:
            # set activation
            time_bomb_ins = TimeBomb.objects.get(id=time_bomb_id)
            hub = time_bomb_ins.hub

            # Time change and verification
            start_time = time_bomb_ins.start_time
            end_time = time_bomb_ins.end_time

            # Check same time in current time bomb
            if activation:
                # First condition
                time_bomb_qs = TimeBomb.objects.filter(
                    hub=hub, status=activation_status, start_time__range=(start_time, end_time)
                )

                if time_bomb_qs.exists():
                    raise BusinessLogicError('There is a time bomb at same time', None, None)

                time_bomb_qs = TimeBomb.objects.filter(
                    hub=hub, status=activation_status, end_time__range=(start_time, end_time)
                )

                if time_bomb_qs.exists():
                    raise BusinessLogicError('There is a time bomb at same time', None, None)

                time_bomb_qs = TimeBomb.objects.filter(
                    hub=hub, status=activation_status, start_time__lte=start_time, end_time__gte=end_time
                )

                if time_bomb_qs.exists():
                    raise BusinessLogicError('There is a time bomb at same time', None, None)

                status = activation_status
            else:
                status = inactivation_status

            # Change status
            time_bomb_ins.status = status
            time_bomb_ins.save()
        except Exception as e:
            msg = '[TimeBombService][set_time_bomb_activate][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = True

        return self.result

    def check_time_bomb_with_id(self, time_bomb_id):
        available_status = 1

        try:
            # Update time bomb
            time_bomb_ins = TimeBomb.objects.filter(id=time_bomb_id, status=available_status)
        except Exception as e:
            msg = '[TimeBombService][check_time_bomb_with_id][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)
        else:
            self.result = time_bomb_ins.exists()

        return self.result
