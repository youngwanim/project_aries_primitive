from django.conf.urls import url

from aries.users import views_referral_history, views_receipt, views_shopping_cart, views_address_v3
from aries.users import views_connect
from aries.users import views_admin
from aries.users import views_notify_info
from aries.users import views_operation
from aries.users import views_user
from aries.users import views_user_info
from aries.users import views_sms, views_sign


urlpatterns = [
    # V3 address API
    url(r'^v3/addresses/?$', views_address_v3.UserAddressList.as_view()),
    url(r'^v3/addresses/(?P<address_id>\d+)/?$', views_address_v3.UserAddressDetail.as_view()),
    url(r'^v3/addresses/(?P<address_id>\d+)/select/?$', views_address_v3.UserAddressSelector.as_view()),
    url(r'^v3/hubs/(?P<hub_id>\d+)/select/?$', views_address_v3.UserAddressHubSelector.as_view()),
    # Receipt API
    url(r'^v2/receipts/?$', views_receipt.UserReceiptList.as_view()),
    url(r'^v2/receipts/(?P<receipt_id>\d+)/?$', views_receipt.UserReceiptDetail.as_view()),
    url(r'^v2/receipts/(?P<receipt_id>\d+)/select/?$', views_receipt.UserReceiptSelect.as_view()),
    # SMS API
    url(r'^sms/?$', views_sms.SmsRequest.as_view()),
    url(r'^sms/verification/?$', views_sms.SmsVerification.as_view()),
    url(r'^sms/verification/(?P<login_key>\d+)/?$', views_sms.SmsVerification.as_view()),
    # Member API
    url(r'^signup/?$', views_sign.SignUp.as_view()),
    url(r'^signin/?$', views_sign.SignIn.as_view()),
    url(r'^signout/?$', views_sign.SignOut.as_view()),
    url(r'^signup/connect/?$', views_connect.ConnectDetail.as_view()),
    url(r'^signin/callback/?$', views_connect.ConnectDetail.as_view()),
    url(r'^v2/signin/validation/?$', views_sign.SignInValidation.as_view()),
    # Shopping bag API
    url(r'^v2/cart/?$', views_shopping_cart.ShoppingCart.as_view()),
    # User API
    url(r'^(?P<open_id>.*)/detail/?$', views_user.UserDetail.as_view()),
    url(r'^(?P<open_id>.*)/password/?$', views_user.Password.as_view()),
    url(r'^(?P<open_id>.*)/info/?$', views_user.UserInfoDetail.as_view()),
    url(r'^news/?$', views_user_info.MyNews.as_view()),
    url(r'^news/(?P<news_id>.*)/read/?$', views_user_info.MyNewsDetail.as_view()),
    # Notification API
    url(r'^notification/?$', views_notify_info.NotifyInfoDetail.as_view()),
    url(r'^notification/(?P<domain>.*)/(?P<operator>.*)/(?P<count>.*)/?$',
        views_notify_info.NotifyInfoHandler.as_view()),
    # Server API
    url(r'^validation/?$', views_user.UserValidation.as_view()),  # Server API
    url(r'^tokens/?$', views_user.UserInformationForPayment.as_view()),  # Server API
    url(r'^operation/order_complete/?$', views_operation.OrderComplete.as_view()),  # Server API
    url(r'^operation/order_canceled/?$', views_operation.OrderCanceled.as_view()),  # Server API
    # Server batch API
    url(r'^batch/referral/?$', views_referral_history.UserReferralHistory.as_view()),  # Server API
    # Admin API (Server API)
    url(r'^admin/userinfo/?$', views_admin.UserInformationDetail.as_view()),  # Server API
    url(r'^admin/news/?$', views_admin.UserNewsDetail.as_view()),  # Server API
    url(r'^admin/customers/?$', views_admin.Customer.as_view()),
    url(r'^admin/customer/(?P<user_id>.*)/?$', views_admin.CustomerDetail.as_view()),
    url(r'^admin/customers/search/?$', views_admin.CustomerSearch.as_view()),
    # Hub API
    url(r'^v2/admin/search/list/?$', views_admin.UserSearchListV2.as_view()),
]
