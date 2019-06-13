from django.conf.urls import url

from aries.apigateway import views_gateway

urlpatterns = [
    url(r'.*', views_gateway.GatewayDetail.as_view())
]