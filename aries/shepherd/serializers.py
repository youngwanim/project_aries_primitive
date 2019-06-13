from rest_framework import serializers

from aries.shepherd.models import RewardBatchResult, WechatEventMessage


class RewardBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardBatchResult
        fields = '__all__'


class WechatEventMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WechatEventMessage
        fields = '__all__'
