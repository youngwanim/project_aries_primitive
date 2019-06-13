"""aries URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^.*', include('aries.apigateway.urls')),
    # url(r'^platform/', include('aries.platform.urls')),
    #url(r'^products/', include('aries.products.urls')),
    #url(r'^users/', include('aries.users.urls')),
    #url(r'^cdn/', include('aries.cdn.urls')),
    #url(r'^partners/', include('aries.partners.urls')),
    #url(r'^purchases/', include('aries.purchases.urls')),
    #url(r'^delivery/', include('aries.delivery.urls')),
    #url(r'^payments/', include('aries.payments.urls')),
    #url(r'^ucc/', include('aries.ucc.urls')),
    #url(r'^push/', include('aries.shepherd.urls')),
    #url(r'^rndkitchen/', include('aries.rndkitchen.urls')),
    #url(r'^operation/', include('aries.operation.urls')),
    # url(r'^$', include('aries.apigateway.urls')),
]
