from django.db import models
import json

default_data = '[{"endtime": "5PM", "starttime": "4PM", ' \
               '"shipping": [{"available": false, "shipping_type": 0}, ' \
               '{"available": true, "shipping_type": 1}], "index": 32}, ' \
               '{"endtime": "6PM", "starttime": "5PM", ' \
               '"shipping": [{"available": false, "shipping_type": 0}, ' \
               '{"available": true, "shipping_type": 1}], "index": 34}, ' \
               '{"endtime": "7PM", "starttime": "6PM", ' \
               '"shipping": [{"available": false, "shipping_type": 0}, ' \
               '{"available": true, "shipping_type": 1}], "index": 36}, ' \
               '{"endtime": "8PM", "starttime": "7PM", ' \
               '"shipping": [{"available": false, "shipping_type": 0}, ' \
               '{"available": true, "shipping_type": 1}], "index": 38}, ' \
               '{"endtime": "9PM", "starttime": "8PM", ' \
               '"shipping": [{"available": false, "shipping_type": 0}, ' \
               '{"available": true, "shipping_type": 1}], "index": 40}, ' \
               '{"endtime": "10PM", "starttime": "9PM", ' \
               '"shipping": [{"available": false, "shipping_type": 0}, ' \
               '{"available": true, "shipping_type": 1}], "index": 42}]'


class DeliverySchedule(models.Model):
    hub_id = models.IntegerField(default=0)
    # working day
    working_day = models.DateField()
    # 5~6, 6~7 ==> total_timeslot = 5
    total_timeslot = models.IntegerField()
    # means = minutes 60, time gap between delivery start times and end time of each time slot
    time_gap = models.IntegerField()
    # 17 o'clock
    delivery_start = models.TimeField()
    # last delivery time slot of the day.
    delivery_end = models.TimeField()
    # contains array : [{"index":34, "starttime":"5:00 PM"}, "endtime":"18:00 PM"}, ...]
    delivery_time_table = models.TextField(default=default_data)
    delivery_time_table_lunch = models.TextField(default=default_data)
    delivery_time_table_dinner = models.TextField(default=default_data)
    delivery_price = models.FloatField(default=8.0)
    minimum_order_price = models.FloatField(default=30.0)
    order_available = models.BooleanField(default=True)
    unavailable_msg_eng = models.CharField(default='', max_length=200, null=True, blank=True)
    unavailable_msg_chn = models.CharField(default='', max_length=200, null=True, blank=True)

    def __str__(self):
        return "delivery schedule on {0}".format(str(self.working_day))


class ShippingAvailability(models.Model):
    hub_id = models.IntegerField()
    ds_id = models.ForeignKey(DeliverySchedule, on_delete=models.CASCADE)
    shipping_availability_table = models.TextField(blank=True, null=True)
    # [{"index":34, "shipping": [{"shipping_type":0, "available":true}, {"shipping_type":1, "available":true}]]

    def save(self, *args, **kwargs):
        if self.pk is None:
            table = json.loads(self.ds_id.delivery_time_table)
            shipping_list = list()
            shipping_methods = ShippingMethod.objects.filter(hub_id=self.hub_id)
            for slot in table:
                list_element = []
                shipping_element = {}
                for sm in shipping_methods:
                    shipping_avail_element = dict(shipping_type=sm.shipping_type)
                    shipping_avail_element['available'] = True
                    list_element.append(shipping_avail_element)
                shipping_element['index'] = slot['index']
                shipping_element['starttime'] = slot['starttime']
                shipping_element['endtime'] = slot['endtime']
                shipping_element['shipping'] = list_element

                shipping_list.append(shipping_element)

            self.shipping_availability_table = json.dumps(shipping_list)
        super(ShippingAvailability, self).save(*args, **kwargs)


class ShippingMethod(models.Model):
    hub_id = models.IntegerField()
    shipping_type = models.IntegerField(default=0)
    shipping_cost = models.FloatField(default=10)
    shipping_name = models.CharField(max_length=32, default="ViaStelle Premium")

    def __str__(self):
        return self.shipping_name
