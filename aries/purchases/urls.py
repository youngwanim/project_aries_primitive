from django.conf.urls import url

from aries.purchases import views_coupon, views_promotion_v2, views_purchase_order_v2, views_referral_coupon, views_dada
from aries.purchases import views_event_coupon
from aries.purchases import views_notification_count
from aries.purchases import views_order
from aries.purchases import views_order_operation

urlpatterns = [
    # Coupon API
    url(r'^coupon/?$', views_coupon.CouponDetail.as_view()),
    url(r'^coupons/?$', views_coupon.CouponPage.as_view()),
    url(r'^coupon/issue/?$', views_event_coupon.WelcomeCoupon.as_view()),
    # For roulette coupon
    url(r'^coupon/roulette/?$', views_event_coupon.PromotionCoupon.as_view()),
    url(r'^coupon/event/download/?$', views_event_coupon.PromotionCoupon.as_view()),
    url(r'^coupon/event/download/check/?$', views_event_coupon.DownloadEventCheck.as_view()),
    # Order Reserve API
    url(r'^v2/order/reserve/?$', views_purchase_order_v2.PurchaseOrderV2.as_view()),
    # Order API
    url(r'^order/?$', views_order.Orders.as_view()),
    # Order Detail API
    url(r'^order/(?P<order_id>.*)/?$', views_order.OrdersDetail.as_view()),
    url(r'^orders/past/?$', views_order.PastOrders.as_view()),
    url(r'^orders/upcoming/?$', views_order.UpcomingOrders.as_view()),
    # Promotion
    url(r'^v2/hub/(?P<hub_id>\d+)/promotions/?$', views_promotion_v2.PromotionView.as_view()),
    url(r'^v2/promotion/(?P<promotion_id>.*)/?$', views_promotion_v2.PromotionDetailView.as_view()),
    # For server api
    url(r'^notification/?$', views_notification_count.NotificationCount.as_view()),
    url(r'^information/coupons/?$', views_coupon.CouponInformation.as_view()),
    url(r'^referral/coupon/?$', views_referral_coupon.ReferralCoupon.as_view()),
    url(r'^membership/coupon/?$', views_referral_coupon.MembershipPromotion.as_view()),
    # Admin API for internal
    url(r'^admin/orders/?$', views_order_operation.OrderOperation.as_view()),
    url(r'^admin/order/(?P<order_id>.*)/preparing/?$', views_order_operation.OrderPreparingOperation.as_view()),
    url(r'^admin/order/(?P<order_id>.*)/detail/?$', views_order_operation.OrderDetailOperation.as_view()),
    url(r'^admin/search/orders/?$', views_order_operation.OrderSearchOperation.as_view()),
    url(r'^v2/admin/hub/(?P<hub_id>\d+)/orders/?$', views_order_operation.OrderOperationV2.as_view()),
    url(r'^v2/admin/(?P<hub_id>\d+)/orders/?$', views_order_operation.OrderOperationV2.as_view()),
    url(r'^v2/admin/order/(?P<order_id>.*)/detail/?$', views_order_operation.OrderDetailOperationV2.as_view()),
    url(r'^v2/admin/search/orders/?$', views_order_operation.OrderSearchV2.as_view()),
    url(r'^v2/admin/search/list/?$', views_order_operation.OrderSearchListV2.as_view()),
    # DADA extension support
    url(r'^extension/dada/new/?$', views_dada.DadaOrder.as_view()),
    url(r'^extension/dada/new/fee/?$', views_dada.DadaAddAfterQuery.as_view()),
    url(r'^extension/dada/tips/?$', views_dada.DadaAddTip.as_view()),
    url(r'^extension/dada/cancel/?$', views_dada.DadaOrderCancel.as_view()),
    url(r'^extension/dada/reorder/?$', views_dada.DadaReOrder.as_view()),
    url(r'^extension/dada/fee/?$', views_dada.DadaQueryFee.as_view()),
    url(r'^extension/dada/(?P<order_id>.*)/detail/?$', views_dada.DadaOrder.as_view()),
    url(r'^extension/dada/location/?$', views_dada.DadaLocationQuery.as_view()),
    url(r'^callback/dada/?$', views_dada.DadaCallbackDetail.as_view()),
]
