from django.conf.urls import url

from aries.payments import views_alipay
from aries.payments import views_payment
from aries.payments import views_wechat

urlpatterns = [
    # Payments API for private
    url(r'^alipay/?$', views_alipay.Payments.as_view()),
    url(r'^alipay/notification/?$', views_alipay.AlipayNotificationHandler.as_view()),
    url(r'^wechat/?$', views_wechat.WechatPayment.as_view()),
    url(r'^wechat/notification/?$', views_wechat.WechatPayNotificationApp.as_view()),
    url(r'^(?P<order_id>.*)/detail/?$', views_payment.PaymentDetail.as_view()),
]
