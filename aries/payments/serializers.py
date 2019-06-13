from rest_framework import serializers

from aries.payments.models import Payment, AlipayRefundTransaction, AlipayNotification, AlipayPaymentTransaction, \
    WechatPaymentTransaction, WechatQueryTransaction, WechatNotification, WechatRefundTransaction, \
    AlipayQueryTransaction


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class AlipayPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlipayPaymentTransaction
        fields = '__all__'


class AlipayQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = AlipayQueryTransaction
        fields = '__all__'


class AlipayRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlipayRefundTransaction
        fields = '__all__'


class AlipayNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlipayNotification
        fields = '__all__'


class WechatPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WechatPaymentTransaction
        fields = '__all__'


class WechatQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = WechatQueryTransaction
        fields = '__all__'


class WechatRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = WechatRefundTransaction
        fields = '__all__'


class WechatNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WechatNotification
        fields = '__all__'
