import json

from rest_framework import serializers
from .models import User, UserInfo, UserLoginInfo, UserGrade, UserNews, \
    UserNotifyInfo, UserAddressInfo, UserReferralInformation, UserReceipt, ShoppingBag


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserSmsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('mdn', 'mdn_verification')


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('open_id', 'mdn', 'mdn_verification', 'name', 'email', 'current_delivery_type', 'default_address_id',
                  'default_address', 'default_recipient_name', 'default_recipient_mdn', 'default_hub_id',
                  'default_pickup_hub_id', 'default_pickup_hub', 'default_receipt_id', 'default_receipt',
                  'push_agreement', 'locale', 'profile_image', 'access_token', 'parent_type', 'connection_account')


class UserLoginInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLoginInfo
        exclude = ('user',)


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = '__all__'


class UserNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNews
        fields = '__all__'


class UserGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGrade
        fields = ('type', 'extra_meal_point', 'extra_meal_point_ratio', 'upgrade_date')


class UserShoppingBagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingBag
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['instruction_history'] = json.loads(ret['instruction_history'])

        return ret


class UserAddressManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressInfo
        exclude = ('user',)


class UserAddressInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressInfo
        fields = '__all__'


class UserNotifyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotifyInfo
        fields = '__all__'


class UserReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReceipt
        fields = '__all__'


class UserReferralInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReferralInformation
        fields = '__all__'
