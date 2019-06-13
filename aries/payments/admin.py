from django.contrib import admin

from aries.payments.models import Payment, AlipayRefundTransaction, AlipayPaymentTransaction, AlipayNotification, \
    AlipayQueryTransaction, WechatPaymentTransaction, WechatQueryTransaction, WechatRefundTransaction, \
    WechatNotification

admin.site.register(Payment)
admin.site.register(AlipayPaymentTransaction)
admin.site.register(AlipayQueryTransaction)
admin.site.register(AlipayRefundTransaction)
admin.site.register(AlipayNotification)
admin.site.register(WechatPaymentTransaction)
admin.site.register(WechatQueryTransaction)
admin.site.register(WechatRefundTransaction)
admin.site.register(WechatNotification)
