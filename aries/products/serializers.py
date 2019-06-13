import datetime
import json

from rest_framework import serializers
from .models import Restaurant, Menu, Hub, Product, ExpertReview, MenuReviewStatics, \
    RestaurantBrandInfo, MenuPairingInformation, HubStock, ProductType, TimeBomb, TimeBombContent, TimeBombDiscountInfo


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class RestaurantInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'chef', 'introduce_image', 'award_info', 'cuisine_info', 'address', 'keyword')

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['award_info'] = json.loads(ret['award_info'])
        ret['cuisine_info'] = json.loads(ret['cuisine_info'])

        return ret


class RestaurantBrandInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantBrandInfo
        exclude = ('restaurant', )


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['popup_contents'] = json.loads(ret['popup_contents'])

        return ret


class MenuListInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'restaurant', 'icon_type', 'name', 'cooking_materials', 'image_main', 'image_detail',
                  'image_sub', 'image_thumbnail', 'description', 'image_package', 'prep_tips', 'prep_plating_thumbnail',
                  'prep_plating_url', 'ingredients', 'nutrition', 'notices', 'subs_contents', 'media_contents',
                  'has_popup_contents', 'popup_contents')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['popup_contents'] = json.loads(ret['popup_contents'])

        return ret


class MenuListInfoAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'restaurant', 'name', 'type', 'icon_type', 'cooking_materials', 'image_main', 'image_detail',
                  'image_sub', 'image_thumbnail', 'description', 'image_package', 'prep_tips', 'prep_plating_thumbnail',
                  'prep_plating_url', 'ingredients', 'nutrition', 'notices', 'subs_contents', 'media_contents',
                  'has_popup_contents', 'popup_contents')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['popup_contents'] = json.loads(ret['popup_contents'])

        return ret


class MenuListGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('restaurant', 'name', 'image_main')


class MenuValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'name',)


class MenuReviewStaticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuReviewStatics
        exclude = ('id', 'menu', )


class HubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hub
        fields = '__all__'


class HubStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = HubStock
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductSerializerV2(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['price_discount_schedule'] = json.loads(ret['price_discount_schedule'])
        ret['badge_en'] = json.loads(ret['badge_en'])
        ret['badge_cn'] = json.loads(ret['badge_cn'])
        ret['category'] = json.loads(ret['category'])
        ret['sales_schedule'] = json.loads(ret['sales_schedule'])

        return list(ret)


class ProductAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'list_index', 'price', 'price_discount', 'price_discount_event', 'event_product',
                  'badge_en', 'badge_cn', 'status')

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['badge_en'] = json.loads(ret['badge_en'])
        ret['badge_cn'] = json.loads(ret['badge_cn'])

        return ret


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'menu', 'price', 'price_unit', 'status')


class ProductListInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'hub', 'menu', 'list_index', 'type', 'price', 'price_discount', 'price_discount_event',
                  'price_discount_schedule', 'price_unit', 'badge_en', 'badge_cn', 'category', 'status', 'sales_time',
                  'has_sales_schedule', 'has_description', 'description_type', 'sales_schedule', 'event_product')


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'


class ExpertReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertReview
        fields = ('created_date', 'expert_job', 'expert_name', 'expert_image', 'expert_comment')


class MenuPairingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuPairingInformation
        fields = '__all__'


class TimeBombSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBomb
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        start_time = instance.start_time.timestamp()
        end_time = instance.end_time.timestamp()
        current_time = datetime.datetime.today().timestamp()

        ret['start_time'] = start_time
        ret['end_time'] = end_time
        ret['current_time'] = int(current_time)

        del ret['target_android']
        del ret['target_ios']
        del ret['target_mobile_web']

        return ret


class TimeBombAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBomb
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        start_time = instance.start_time.timestamp()
        end_time = instance.end_time.timestamp()
        current_time = datetime.datetime.today().timestamp()

        ret['start_time'] = start_time
        ret['end_time'] = end_time
        ret['current_time'] = int(current_time)

        return ret


class TimeBombContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBombContent
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['guide_content'] = json.loads(ret['guide_content'])
        del ret['time_bomb']
        del ret['language_type']

        return ret


class TimeBombDiscountInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBombDiscountInfo
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        del ret['time_bomb']

        return ret
