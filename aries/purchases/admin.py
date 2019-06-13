from django.contrib import admin
from .models import Order, Coupon, CustomerCoupon, PurchaseOrder, Promotion, EventCoupon, MemberPromotion, \
    EventOrderHistory, DadaOrderRequest, DadaOrderDetail, DadaCallback

admin.site.register(PurchaseOrder)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(EventCoupon)
admin.site.register(CustomerCoupon)
admin.site.register(Promotion)
admin.site.register(MemberPromotion)
admin.site.register(EventOrderHistory)
admin.site.register(DadaOrderRequest)
admin.site.register(DadaOrderDetail)
admin.site.register(DadaCallback)
