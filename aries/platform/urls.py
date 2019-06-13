from django.conf.urls import url

from aries.platform import views_operation
from aries.platform import views_operator
from aries.platform import views_token, views_scope


urlpatterns = [
    # Platform API
    url(r'^token/?$', views_token.Token.as_view()),
    url(r'^scope/?$', views_scope.Scope.as_view()),
    url(r'^token/verification/?$', views_token.TokenDetail.as_view()),
    url(r'^service/(?P<os_name>.*)/?$', views_operation.Operation.as_view()),
    url(r'^hubs/(?P<hub_id>\d+)/service/?$', views_operation.OperationV2.as_view()),
    # Admin API
    url(r'^operators/?$', views_operator.AdminOperator.as_view()),  # Server API
    url(r'^operator/(?P<operator_id>\d+)/?$', views_operator.AdminOperatorDetail.as_view()),  # Server API
    url(r'^operators/sign/?$', views_operation.OperationSign.as_view()),  # Server API
    url(r'^operators/token/?$', views_token.TokenDetailForAdmin.as_view()),  # Server API
    url(r'^operators/validation/?$', views_operation.OperationVerification.as_view()),  # Server API
]
