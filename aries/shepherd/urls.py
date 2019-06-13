from django.conf.urls import url

from aries.shepherd import views_push_ios, views_wechat_event
from aries.shepherd import views_push_single

urlpatterns = [
    url(r'^ios/single/?$', views_push_ios.PushCustom.as_view()),
    url(r'^ios/account/?$', views_push_ios.PushCustom.as_view()),
    url(r'^android/single/?$', views_push_single.PushOrderComplete.as_view()),
    url(r'^android/account/?$', views_push_single.PushOrderComplete.as_view()),
    url(r'^wechat/event/?$', views_wechat_event.WechatEventNotification.as_view()),
]
