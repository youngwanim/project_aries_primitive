from __future__ import absolute_import
import os

from celery import Celery
from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings

from aries.shepherd.coupon_tasks.referral_batch import batch_referral_reward

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('shepherd', broker='redis://localhost')

app.config_from_object('django.conf:settings')
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@periodic_task(run_every=(crontab(minute="*", hour="*", day_of_week="*",)))
def referral_reward():
    result = batch_referral_reward()
    print(result)

