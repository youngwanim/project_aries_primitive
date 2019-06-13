from django.conf.urls import url

from aries.products import views_admin, views_menu_v2, views_validation_v3, views_time_bomb
from aries.products import views_brand
from aries.products import views_hub
from aries.products import views_menu_review
from aries.products import views_product_list
from aries.products import views_recommend
from aries.products import views_stock
from aries.products import views_product


urlpatterns = [
    # Products api
    url(r'^v2/hubs/(?P<hub_id>\d+)/?$', views_product_list.ProductListV2.as_view()),
    url(r'^(?P<product_id>\d+)/detail/?$', views_product.ProductDetail.as_view()),
    url(r'^v2/hub/(?P<hub_id>\d+)/menu/?$', views_menu_v2.ProductInfoWithMenu.as_view()),
    url(r'^v2/hubs/(?P<hub_id>\d+)/recommend/?$', views_recommend.RecommendProductV2.as_view()),
    # TimeBomb api
    url(r'^timebomb/(?P<time_bomb_id>\d+)/?$', views_time_bomb.TimeBomb.as_view()),
    url(r'^hubs/(?P<hub_id>\d+)/timebomb/?$', views_time_bomb.TimeBombDetail.as_view()),
    url(r'^timebomb/(?P<time_bomb_id>\d+)/stock/?$', views_time_bomb.TimeBombStock.as_view()),
    # TimeBomb admin api
    url(r'^admin/timebomb/hubs/(?P<hub_id>\d+)/?$', views_admin.TimeBombAdminList.as_view()),
    url(r'^admin/timebomb/(?P<time_bomb_id>\d+)/?$', views_admin.TimeBombAdminDetail.as_view()),
    url(r'^admin/timebomb/(?P<time_bomb_id>\d+)/activate/?$', views_admin.TimeBombActivation.as_view()),
    # Validation V2
    url(r'^v3/hub/(?P<hub_id>\d+)/validation/?$', views_validation_v3.ProductValidationBasic.as_view()),
    url(r'^v3/hub/(?P<hub_id>\d+)/time/(?P<time>.*)/validation/?$', views_validation_v3.ProductValidationV3.as_view()),
    url(r'^v3/hub/(?P<hub_id>\d+)/time/(?P<time>.*)/purchase/?$', views_validation_v3.PurchaseValidationV3.as_view()),
    # Restaurants
    url(r'^restaurant/(?P<restaurant_id>\d+)/brand/?$', views_brand.RestaurantBrandInfoPageDetail.as_view()),
    url(r'^v2/restaurant/(?P<restaurant_id>\d+)/brand/?$', views_brand.RestaurantBrandInfoPageDetail.as_view()),
    # Hubs
    url(r'^hubs/?$', views_hub.HubGeoInformation.as_view()),
    url(r'^hubs/delivery/?$', views_hub.HubDelivery.as_view()),
    # Server API for internal - product, menu
    url(r'^(?P<product_id>\d+)/?$', views_product.Products.as_view()),
    url(r'^validation/?$', views_product.ProductValidation.as_view()),
    url(r'^stock/?$', views_stock.ProductStock.as_view()),
    url(r'^menu/validation/?$', views_menu_review.PastOrderReview.as_view()),
    url(r'^menu/statics/?$', views_menu_review.ReviewStaticsDetail.as_view()),
    # Admin API for internal V2
    url(r'^v2/admin/hub/(?P<hub_id>\d+)/stock/?$', views_admin.AdminHubStockV2.as_view()),
    url(r'^v2/admin/hub/(?P<hub_id>\d+)/product/?$', views_admin.AdminProductV2.as_view()),
    url(r'^v2/admin/product/detail/?$', views_admin.AdminProductDetailV2.as_view()),
    url(r'^v2/admin/menus/?$', views_admin.AdminMenuListV2.as_view()),
]
