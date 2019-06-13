from django.conf.urls import url

from aries.delivery import views_schedule, views_sales_time, views_time_table

urlpatterns = [
    url(r'^timetable/(?P<hub_id>\d+)/?$', views_schedule.DeliveryTargetSchedule.as_view()),
    url(r'^v2/timetable/hubs/(?P<hub_id>\d+)/?$', views_time_table.DeliveryTimeTable.as_view()),
    url(r'^timetable/(?P<hub_id>\d+)/(?P<date>\d{4}-\d{2}-\d{2})/(?P<table_id>\d+)/(?P<shipping_type>\d+)/?$',
        views_schedule.DeliveryTargetScheduleDetail.as_view()),
    url(r'^time/?$', views_sales_time.ProductSalesTime.as_view()),
]
