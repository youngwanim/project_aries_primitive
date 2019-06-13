import json

from rest_framework import serializers
from .models import CustomerReview, ReviewItem, DisplaySchedule, CurationArticle, CurationPage, \
    CurationContent, Event, Reward, EventInformation, EventReward, EventHistory, EventContent, RewardContent, \
    CurationPageContent, ReferralEvent, ReferralInformation


class CustomerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReview
        fields = '__all__'


class ReviewItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewItem
        fields = ('type', 'name', 'name_cn')


class DisplayScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplaySchedule
        fields = '__all__'


class CurationArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurationArticle
        fields = '__all__'


class CurationContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurationContent
        exclude = ('curation_article', 'language_type')


class CurationPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurationPage
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['articles'] = json.loads(ret['articles'])
        return ret


class CurationPageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurationPageContent
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class EventContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventContent
        fields = '__all__'


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = '__all__'


class RewardContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardContent
        fields = '__all__'


class EventInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventInformation
        fields = '__all__'


class EventRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReward
        fields = '__all__'


class EventHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventHistory
        fields = '__all__'


class ReferralEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralEvent
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['friend_coupon_status'] = json.loads(ret['friend_coupon_status'])
        ret['first_coupon_status'] = json.loads(ret['first_coupon_status'])
        del ret['id']
        return ret


class ReferralInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralInformation
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = ret['reward_id']

        del ret['reward_id']
        del ret['referral_type']
        del ret['reward_sequence']

        return ret
