import json

from rest_framework import serializers

from aries.purchases.models import Order, Coupon, CustomerCoupon, PurchaseOrder, Promotion, EventCoupon, \
    MemberPromotion, DadaOrderRequest, DadaOrderDetail, DadaCallback

"""
Model Serializer
"""


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'


class PurchaseOrderEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ('user_telephone', 'extra_telephone_usage', 'extra_telephone', 'delivery_address_id',
                  'delivery_as_fast', 'delivery_schedule', 'special_instruction')


class PurchaseOrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ('hub_id', 'user_telephone', 'shipping_method', 'shipping_cost',
                  'delivery_schedule', 'phase_next_day', 'extra_telephone', 'price_unit',
                  'price_sub_total', 'price_discount', 'price_delivery_fee', 'price_total',
                  'delivery_address_id', 'user_name', 'special_instruction', 'extra_telephone_usage',
                  'delivery_on_site', 'payment_type')


class UpcomingPurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        exclude = ('id', 'created_date', 'open_id', 'last_modified_date')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'order_start_date', 'order_id', 'order_status', 'order_status_history',
                  'operation_status', 'operation_status_history', 'open_id', 'user_name', 'user_telephone',
                  'user_receipt', 'delivery_schedule', 'delivery_as_fast', 'delivery_on_site', 'delivery_address_lat',
                  'delivery_address_lng', 'delivery_recipient_name', 'delivery_recipient_mdn', 'shipping_method',
                  'shipping_status', 'shipping_rider_id', 'shipping_rider_telephone')


class FailedOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class UpcomingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ('id', 'hub_id', 'open_id', 'order_finish_date', 'order_modified_date',
                   'shipping_status', 'shipping_rider_id', 'shipping_rider_telephone', 'delivery_customer_name',
                   'comments', 'operation_status', 'operation_status_history')


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        exclude = ('status', 'period_type', 'period_day', 'period_start_date', 'period_end_date')


class CustomerCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCoupon
        fields = '__all__'


class CouponInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCoupon
        fields = ('id', 'issue_date', 'start_date', 'end_date', 'used_date', 'status', 'target_id', 'coupon')


class EventCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCoupon
        fields = '__all__'


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        exclude = ('has_button', 'button_type', 'button_text', 'button_action_type', 'button_action_detail',
                   'has_display_group', 'android_display', 'ios_display', 'web_display')


class PromotionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'


class MemberPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberPromotion
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['description'] = json.loads(ret['description'])
        del ret['language_type']
        del ret['status']

        return ret


class DadaOrderReqSerializer(serializers.ModelSerializer):
    class Meta:
        model = DadaOrderRequest
        fields = '__all__'


class DadaOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DadaOrderDetail
        fields = '__all__'


class DadaOrderCallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DadaCallback
        fields = '__all__'
