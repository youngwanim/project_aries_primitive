from django.conf.urls import url

from aries.cdn import views_cdn_admin
from aries.cdn import views_cdn_users
from . import views


urlpatterns = [
    url(r'^$', views.CdnFile.as_view()),
    url(r'^users/(?P<folder_name>.*)/?$', views_cdn_users.CdnFile.as_view()),
    url(r'^file/(?P<folder_name>.*)/?$', views_cdn_admin.CdnFile.as_view()),
]
