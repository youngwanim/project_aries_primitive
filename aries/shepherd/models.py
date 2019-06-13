from django.db import models


class RewardBatchResult(models.Model):
    open_id = models.CharField(max_length=128, null=False)
    hub_id = models.IntegerField(default=1, null=False)
    order_id = models.CharField(max_length=200, null=False, unique=True)
    batch_result = models.BooleanField(default=False)
    batch_date = models.DateTimeField(auto_now_add=True)
    batch_log = models.TextField(null=True, blank=True)

    def __str__(self):
        return '[' + str(self.batch_date) + '] ' + str(self.open_id) + ' : ' + str(self.order_id)

    class Meta:
        ordering = ('-id',)


class WechatEventMessage(models.Model):
    Event = models.CharField(max_length=30, null=False)
    ToUserName = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    FromUserName = models.CharField(max_length=200, null=True, blank=True)
    CreateTime = models.CharField(max_length=20, null=True, blank=True)
    MsgType = models.CharField(max_length=20, null=True, blank=True)
    EventKey = models.CharField(max_length=50, null=True, blank=True)
    Ticket = models.CharField(max_length=50, null=True, blank=True)
    Latitude = models.FloatField(null=True, blank=True)
    Longitude = models.FloatField(null=True, blank=True)
    Precision = models.FloatField(null=True, blank=True)

    def __str__(self):
        return '[%s] From: %s, To: %s'.format(self.Event, self.ToUserName, self.FromUserName)

    class Meta:
        ordering = ('-id', )
