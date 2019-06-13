from rest_framework import serializers

from aries.platform.models import AuthToken, AuthScope, OperationStatus, Operator, OperationPopup


class AuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthToken
        fields = '__all__'


class ScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthScope
        fields = '__all__'


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationStatus
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = '__all__'


class PopupSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationPopup
        fields = '__all__'

