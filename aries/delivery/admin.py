from django.contrib import admin
from .models import DeliverySchedule, ShippingAvailability, ShippingMethod

admin.site.register(DeliverySchedule)
admin.site.register(ShippingAvailability)
admin.site.register(ShippingMethod)
