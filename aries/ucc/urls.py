from django.conf.urls import url

from aries.ucc import views_review, views_curation, views_event, views_curation_admin, views_referral

urlpatterns = [
    # Product review API
    url(r'^products/(?P<product_id>\d+)/reviews/?$', views_review.CustomerReviewDetailNew.as_view()),
    url(r'^products/reviews/?$', views_review.CustomerReviews.as_view()),
    # Curation API
    url(r'^curation/?$', views_curation.Curation.as_view()),
    url(r'^curation/reset/?$', views_curation.CurationCacheReset.as_view()),
    url(r'^curation/(?P<page_id>\d+)/detail?$', views_curation.CurationDetailList.as_view()),
    # Roulette API
    url(r'^event/roulette/?$', views_event.EventInformation.as_view()),
    url(r'^event/roulette/draw/?$', views_event.EventDrawing.as_view()),
    url(r'^event/roulette/history/?$', views_event.EventDelete.as_view()),
    url(r'^event/history/?$', views_event.EventValidation.as_view()),
    # Referral event API
    url(r'^event/referral/info/?$', views_referral.ReferralInformation.as_view()),
    url(r'^event/referral/?$', views_referral.ReferralBoard.as_view()),
    url(r'^event/referral/coupon/?$', views_referral.ReferralCoupon.as_view()),
    url(r'^event/referral/validation/?$', views_referral.ReferralValidation.as_view()),
    url(r'^event/referral/first/?$', views_referral.ReferralFirstPurchase.as_view()),
    # Curation admin api
    url(r'^admin/curation/?$', views_curation_admin.CurationArticleAdmin.as_view()),
    url(r'^admin/curation/(?P<article_id>\d+)/detail/?$', views_curation_admin.CurationArticleAdminDetail.as_view()),
    url(r'^admin/curation/page/?$', views_curation_admin.CurationPageAdmin.as_view()),
    url(r'^admin/curation/page/(?P<page_id>\d+)/detail/?$', views_curation_admin.CurationPageAdminDetail.as_view()),
    url(r'^admin/curation/list/?$', views_curation_admin.CurationPageListAdmin.as_view()),
]
