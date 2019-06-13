import datetime

import requests
from django.core.management import BaseCommand

from aries.common import urlmapper
from aries.purchases.models import EventOrderHistory


def get_referral_info(user_open_id):
    url = urlmapper.get_url('USER_REFERRAL_INFO')
    body = {'open_id': user_open_id}
    response = requests.post(url=url, json=body)

    if response.status_code == 200:
        response_json = response.json()
    else:
        raise Exception('Request failed')

    return response_json


def get_first_purchase(referrer_open_id):
    url = 'http://139.196.123.42:8080/ucc/event/referral/first'
    body = {'open_id': referrer_open_id, 'validation_key': 'apple_upper_case'}
    response = requests.post(url=url, json=body)

    if response.status_code == 200:
        response_json = response.json()
        print('success')
    else:
        print('Fail')
        raise Exception('Request failed')

    return response_json


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--date', dest='date', required=False,
            help='Batch target date - Ex) 2018-07-15 (default=Today)',
        )

    def handle(self, *args, **options):
        today = datetime.datetime.today() - datetime.timedelta(days=1)
        today_str = str(today)[:10]
        target_date = options.get('date', today_str)
        print(today, 'Target date :', target_date)

        order_history_qs = EventOrderHistory.objects.filter(
            register_date=target_date, event_target=True, event_batch_check=False
        )
        print(order_history_qs)

        push_send_list = []

        for order_history in order_history_qs:
            user_open_id = order_history.open_id
            order_history.event_batch_check = True
            order_history.save()

            try:
                referral_result = get_referral_info(user_open_id)
            except Exception as e:
                print(str(e))
                referral_result = {'purchase_target': False}

            print(referral_result)

            try:
                if referral_result['purchase_target']:
                    referrer_open_id = referral_result['referrer_open_id']
                    validation_result = get_first_purchase(referrer_open_id)
                    print(validation_result)

                    push_send_list.append(referrer_open_id)
                    order_history.event_reward = True

                order_history.event_batch_check = True
                order_history.save()
            except Exception as e:
                print(str(e))
