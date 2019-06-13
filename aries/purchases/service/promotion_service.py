import datetime

from django.core.paginator import Paginator

from aries.purchases.models import Promotion, MemberPromotion
from aries.purchases.serializers import PromotionDetailSerializer, PromotionSerializer, MemberPromotionSerializer


def promotion_with_os_query(hub_id, os_type):
    min_day = datetime.datetime.now() - datetime.timedelta(days=30)

    promotion_query = {
        'hub_id': hub_id,
        'end_date__gte': min_day,
        'has_display_group': True,
        'status': 1
    }

    if os_type == 0:
        promotion_query['android_display'] = True
    elif os_type == 1:
        promotion_query['ios_display'] = True
    elif os_type == 2:
        promotion_query['web_display'] = True

    return promotion_query


class PromotionService:

    def __init__(self, logger_info, logger_error, target_db):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.target_db = target_db
        self.result = None

    def read_promotion_with_id(self, promotion_id):
        promotion = Promotion.objects.using(self.target_db).get(id=promotion_id)

        serializer = PromotionDetailSerializer(promotion)
        promotion_data = serializer.data

        return promotion_data

    def read_promotion_list(self, page, limit, hub_id):
        min_day = datetime.datetime.now() - datetime.timedelta(days=30)

        promotion_object_list = Promotion.objects.using(self.target_db).filter(
            hub_id=hub_id,
            end_date__gte=min_day,
            has_display_group=False
        )

        promotion_count = promotion_object_list.count()
        paginator = Paginator(promotion_object_list, limit)

        promotions = paginator.page(page).object_list
        serializer = PromotionSerializer(promotions, many=True)
        promotion_data = serializer.data

        result = (promotion_data, promotion_count)

        return result

    def read_promotion_list_with_os(self, hub_id, os_type):
        query_str = promotion_with_os_query(hub_id, os_type)

        promotion_object_list = Promotion.objects.using(self.target_db).filter(**query_str)
        promotion_data = PromotionSerializer(promotion_object_list, many=True).data
        promotion_count = promotion_object_list.count()

        result = (promotion_data, promotion_count)

        return result

    def read_coupon_promotion_with_latest(self, promotion_type, language_type=0):
        member_promotion_qs = MemberPromotion.objects.filter(
            type=promotion_type, language_type=language_type, status=1
        )

        if member_promotion_qs.count() == 0:
            self.result = None
        else:
            member_promotion_qs = MemberPromotion.objects.filter(
                type=promotion_type, language_type=language_type, status=1
            ).latest('id')
            self.result = MemberPromotionSerializer(member_promotion_qs).data

        return self.result
