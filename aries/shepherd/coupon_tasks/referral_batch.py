import datetime
import json
import requests

from aries.common import code

# admin_sign_in_url = 'http://139.196.123.42:8080/platform/operators/sign'
admin_sign_in_url = 'https://api.viastelle.com/platform/operators/sign'
# delivery_complete_url = 'http://139.196.123.42:8080/purchases/delivery/complete?page=1&limit=100&'
delivery_complete_url = 'https://api.viastelle.com/purchases/delivery/complete?page=1&limit=100&'
# admin_coupon_url = 'http://139.196.123.42:8080/purchases/admin/reward/referral'
admin_coupon_url = 'https://api.viastelle.com/purchases/admin/reward/referral'
# admin_news_url = 'http://139.196.123.42:8080/users/admin/news'
admin_news_url = 'https://api.viastelle.com/users/admin/news'
# user_info_url = 'http://139.196.123.42:8080/users/admin/userinfo'
user_info_url = 'https://api.viastelle.com/users/admin/userinfo'

push_android_url = 'http://localhost:8080/push/android/account'
push_ios_url = 'http://localhost:8080/push/ios/account'
reward_result_url = 'http://localhost:8080/push/reward'

REWARD_TITLE = '[Referral Event] Coupon received'
REWARD_TITLE_CN = '[邀请活动] 收到优惠券'
REWARD_CONTENT = '["You have received a 50RMB coupon from the purchase made by your friend!"]'
REWARD_CONTENT_CN = '["您已收到一张50元优惠券，来自您邀请的朋友的购买激活！"]'
PUSH_CONTENT = 'You have received a 50RMB coupon from the purchase made by your friend!'
PUSH_CONTENT_CN = '您已收到一张50元优惠券，来自您邀请的朋友的购买激活！'


def batch_referral_reward():

    # Operator login
    payload = {'account': 'reward_admin', 'password': 'shanghai_reward01'}
    response = requests.post(admin_sign_in_url, json=payload)

    if response.status_code != code.ARIES_200_SUCCESS:
        print(response.status_code)
        return False

    response_json = response.json()
    print(response_json)
    access_token = response_json['token']

    # today = 'date=' + str(datetime.date.today() - datetime.timedelta(days=1))
    today = 'date=' + str(datetime.date.today())

    headers = {'authorization': 'bearer ' + access_token}
    response = requests.get(delivery_complete_url + today, headers=headers)

    if response.status_code != code.ARIES_200_SUCCESS:
        print(response.status_code)
        return False

    response_json = response.json()
    orders = response_json['orders']

    for order in orders:
        api_requests = {}
        batch_result = True
        open_id = order['open_id']
        order_id = order['order_id']
        hub_id = order['hub_id']
        coupon_list = order['coupon_list']
        promo_code = 'REFERRAL_171023'

        if promo_code in coupon_list:
            # Reward target
            # Coupon registration
            coupon_payload = {
                'open_id': open_id,
                'coupon_id': 5,
                'coupon_code': promo_code
            }
            response = requests.post(admin_coupon_url, headers=headers, json=coupon_payload)
            api_requests['coupon_register'] = response.text

            if response.status_code == code.ARIES_200_SUCCESS:
                # User news registration
                user_news_payload = {
                    'open_id': open_id,
                    'type': 1,
                    'title': REWARD_TITLE,
                    'title_cn': REWARD_TITLE_CN,
                    'content': REWARD_CONTENT,
                    'content_cn': REWARD_CONTENT_CN,
                    'detail': order_id,
                    'detail_cn': order_id
                }
                response = requests.post(admin_news_url, headers=headers, json=user_news_payload)
                api_requests['user_news'] = response.text
            else:
                api_requests['user_news'] = ''
                batch_result = False

            # Send push to reward member
            user_info_payload = {
                'open_id': open_id
            }
            response = requests.post(user_info_url, headers=headers, json=user_info_payload)

            if response.status_code == 200:
                response_json = response.json()
                user = response_json['user']
                user_info = response_json['user_info']
                content_tuple = get_title_content(user['locale'])

                push_payload = {
                    'open_id': open_id,
                    'title': content_tuple[0],
                    'content': content_tuple[1],
                    'custom': {
                        'visibility': 'public',
                        'target': '6',
                        'extra': order_id
                    }
                }

                if user_info['os_type'] == 0 and user['push_agreement'] == 'Y':
                    push_url = push_android_url
                    response = requests.post(push_url, headers=headers, json=push_payload)
                    api_requests['push_send'] = response.text
                elif user_info['os_type'] == 1 and user['push_agreement'] == 'Y':
                    push_url = push_ios_url
                    response = requests.post(push_url, headers=headers, json=push_payload)
                    api_requests['push_send'] = response.text

            else:
                batch_result = False
        else:
            # Not reward target
            batch_result = True

        batch_result = {
            'open_id': open_id,
            'hub_id': hub_id,
            'order_id': order_id,
            'batch_result': batch_result,
            'batch_log': json.dumps(api_requests)
        }

        response = requests.post(reward_result_url, json=batch_result)
        print(response.text)

    return True


def get_title_content(locale):
    if locale.upper() == 'EN':
        result = (REWARD_TITLE, PUSH_CONTENT)
    else:
        result = (REWARD_TITLE_CN, PUSH_CONTENT_CN)
    return result
