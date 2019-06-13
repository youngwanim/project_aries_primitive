from rest_framework import serializers
from .models import ShippingMethod


class ShippingMethodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        exclude = ('id', 'hub_id',)
