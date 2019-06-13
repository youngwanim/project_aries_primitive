from rest_framework import serializers
from .models import Result


class ResultSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    message = serializers.CharField(max_length=200)
    response = serializers.JSONField()

    def update(self, instance, validated_data):
        instance.code = validated_data.get('code', instance.code)
        instance.message = validated_data.get('message', instance.message)
        instance.response = validated_data.get('response', instance.response)

    def create(self, validated_data):
        return Result(**validated_data)
