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

urlpatterns = [
    # Products
    url(r'^products/', include('aries.products.urls')),
    url(r'^delivery/', include('aries.delivery.urls')),
    # Operation
    url(r'^operation/', include('aries.operation.urls')),
    # Payments
    url(r'^payments/', include('aries.payments.urls')),
    url(r'^purchases/', include('aries.purchases.urls')),
    # Platform
    url(r'^platform/', include('aries.platform.urls')),
    url(r'^push/', include('aries.shepherd.urls')),
    # Users
    url(r'^users/', include('aries.users.urls')),
    url(r'^cdn/', include('aries.cdn.urls')),
    url(r'^ucc/', include('aries.ucc.urls')),
]
