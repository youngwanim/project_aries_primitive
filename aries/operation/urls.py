from django.conf.urls import url

from aries.operation import views_hub
from aries.operation import views_notification

urlpatterns = [
    url(r'^test/?$', views_notification.OrderNotification.as_view()),
    url(r'^message/?$', views_notification.OperationNofitication.as_view()),
    url(r'^hub/message/?$', views_hub.HubMessageSender.as_view()),
]
