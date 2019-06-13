from django.conf import settings

if settings.DEBUG:
    HOST = 'http://139.196.123.42:8080'
    HOST_PLATFORM = 'http://localhost:8080'
    HOST_USER = 'http://localhost:8080'
    HOST_PRODUCT = 'http://localhost:8080'
    HOST_PAYMENT = 'http://localhost:8080'
    HOST_OPERATION = 'http://139.196.123.42:8080'
    HOST_CDN = 'http://139.196.123.42:8080'
    ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
    WECHAT = 'https://api.weixin.qq.com'
    QQ = 'https://graph.qq.com'
elif settings.STAGE:
    HOST = 'https://stg-api.viastelle.com'
    HOST_PLATFORM = 'http://192.168.1.210:80'
    HOST_USER = 'http://192.168.1.210:80'
    HOST_PRODUCT = 'http://192.168.1.210:80'
    HOST_PAYMENT = 'http://192.168.1.210:80'
    HOST_OPERATION = 'http://192.168.1.210:8080'
    HOST_CDN = 'http://192.168.1.210:80'
    ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
    WECHAT = 'https://api.weixin.qq.com'
    QQ = 'https://graph.qq.com'
else:
    HOST = 'https://api.viastelle.com'
    HOST_PLATFORM = 'http://192.168.1.103:80'
    HOST_USER = 'http://192.168.1.104:80'
    HOST_PRODUCT = 'http://192.168.1.105:80'
    HOST_PAYMENT = 'http://192.168.1.106:80'
    HOST_OPERATION = 'http://106.15.205.179:8080'
    HOST_CDN = 'http://192.168.1.104:80'
    ALIPAY_URL = 'https://openapi.alipay.com/gateway.do'
    WECHAT = 'https://api.weixin.qq.com'
    QQ = 'https://graph.qq.com'

url_mapper = dict()

# PRODUCT
url_mapper['PRODUCT'] = HOST_PRODUCT + '/products'
url_mapper['PRODUCT_VALIDATION'] = HOST_PRODUCT + '/products/validation'
url_mapper['PRODUCT_RECOMMEND'] = HOST_PRODUCT + '/products/recommends'
url_mapper['PRODUCT_HUBS'] = HOST_PRODUCT + '/products/hubs'
url_mapper['PRODUCT_STOCK'] = HOST_PRODUCT + '/products/stock'
url_mapper['MENU_VALIDATE'] = HOST_PRODUCT + '/products/menu/validation'
url_mapper['MENU_STATICS'] = HOST_PRODUCT + '/products/menu/statics'
url_mapper['PRODUCT_WITH_MENU'] = HOST_PRODUCT + '/products/v2/hub/{}/menu'
url_mapper['TIME_BOMB_INFO'] = HOST_PRODUCT + '/products/hubs/{}/timebomb'

# PRODUCT V2
url_mapper['PRODUCT_VALIDATION_V2'] = HOST_PRODUCT + '/products/v2/hub/{}/time/{}/purchase/'
url_mapper['PRODUCT_VALIDATION_V3'] = HOST_PRODUCT + '/products/v3/hub/{}/time/{}/purchase/'

# USER
url_mapper['USER_INFO'] = HOST_USER + '/users'
url_mapper['USER_VALIDATION'] = HOST_USER + '/users/validation'
url_mapper['USER_NOTIFICATION'] = HOST_USER + '/users/notification'
url_mapper['USER_SMS_VERIFICATION'] = HOST_USER + '/users/sms/verification/'
url_mapper['USER_PAYMENT_TOKEN'] = HOST_USER + '/users/tokens'
url_mapper['OPERATION_ORDER_COMPLETE'] = HOST_USER + '/users/operation/order_complete'
url_mapper['OPERATION_ORDER_CANCELED'] = HOST_USER + '/users/operation/order_canceled'
url_mapper['PRODUCT_ADDRESS_DETAIL'] = HOST_USER + '/users/v3/addresses'
url_mapper['USER_NOTIFICATION_UPDATE'] = HOST_USER + '/users/notification/{}/{}/{}'
url_mapper['USER_REFERRAL_INFO'] = HOST_USER + '/users/batch/referral'
url_mapper['USER_CART_INFO_SAVE'] = HOST_USER + '/users/v2/cart'

# CDN
url_mapper['CDN_FILE_UPLOAD'] = HOST_USER + '/cdn/file'

# PURCHASE
url_mapper['ORDER'] = HOST_PAYMENT + '/purchases/order'
url_mapper['COUPON_LIST'] = HOST_PAYMENT + '/purchases/coupon'
url_mapper['PREPARATION'] = HOST_PAYMENT + '/purchases/orders/preparation'
url_mapper['PROMOTION_DATE'] = HOST_PAYMENT + '/admin/promotions/list'
url_mapper['NOTIFICATION_COUNT'] = HOST_PAYMENT + '/purchases/notification'
url_mapper['ORDER_DELIVERY_COMPLETE'] = HOST_PAYMENT + '/delivery/complete'
url_mapper['ROULETTE_COUPON'] = HOST_PAYMENT + '/purchases/coupon/roulette'
url_mapper['COUPON_INFORMATION'] = HOST_PAYMENT + '/purchases/information/coupons'
url_mapper['REFERRAL_COUPON'] = HOST_PAYMENT + '/purchases/referral/coupon'
url_mapper['SIGNUP_PROMOTION'] = HOST_PAYMENT + '/purchases/membership/coupon'

# DELIVERY
url_mapper['TIMETABLE_LIST'] = HOST_PRODUCT + '/delivery/timetable'
url_mapper['TIMETABLE_LIST_V2'] = HOST_PRODUCT + '/delivery/v2/timetable/hubs'

# PAYMENT
url_mapper['PAYMENT'] = HOST_PAYMENT + '/payments'
url_mapper['ALIPAY_CALLBACK_URL'] = HOST + '/payments/alipay/notification/'

# PLATFORM
url_mapper['PLATFORM_SERVER'] = HOST_PLATFORM + '/platform/token'
url_mapper['TOKEN_VALIDATE'] = HOST_PLATFORM + '/platform/token/verification'
url_mapper['ADMIN_VALIDATE'] = HOST_PLATFORM + '/platform/operators/validation'

# UCC
url_mapper['PRODUCT_REVIEW'] = HOST_USER + '/ucc/products'
url_mapper['REVIEW_DATA'] = HOST_USER + '/ucc/products/reviews'
url_mapper['HAS_EVENT'] = HOST_USER + '/ucc/event/history'
url_mapper['SHARE_ID_VALIDATION'] = HOST_USER + '/ucc/event/referral/validation/'
url_mapper['FIRST_PURCHASE'] = HOST_USER + '/ucc/event/referral/first'

# PUSH
url_mapper['PUSH_SINGLE'] = HOST_PLATFORM + '/push/single'
url_mapper['PUSH_ACCOUNT_ANDROID'] = HOST_OPERATION + '/push/android/account'
url_mapper['PUSH_ACCOUNT_IOS'] = HOST_OPERATION + '/push/ios/account'

# OPERATION
url_mapper['OPERATION_MESSAGE'] = HOST + '/operation/message'
url_mapper['HUB_MESSAGE_ANDROID'] = 'http://106.15.205.179:8080/operation/hub/message'
# url_mapper['HUB_MESSAGE_ANDROID'] = 'http://139.196.123.42:9000/operation/hub/message'
url_mapper['OPERATION_API'] = HOST

# WECHAT
url_mapper['WECHAT_ACCESS_TOKEN'] = WECHAT + 'sns/oauth2/access_token'

# QQ platform URL
url_mapper['QQ_CODE'] = QQ + '/oauth2.0/authorize'
url_mapper['QQ_ACCESS_TOKEN'] = QQ + '/oauth2.0/token'
url_mapper['QQ_OPEN_ID'] = QQ + '/oauth2.0/me'

# ADMIN
url_mapper['ADMIN_USER_INFO'] = HOST_USER + '/users/admin/userinfo'


def get_url(url_domain):
    return url_mapper.get(url_domain)


def get_purchase_validation(hub_id, time):
    return url_mapper.get('PRODUCT_VALIDATION_V2').format(hub_id, time)


def get_purchase_validation_v2(hub_id, time):
    return url_mapper.get('PRODUCT_VALIDATION_V3').format(hub_id, time)


def get_push_url(os_type):
    if os_type == 0:
        return url_mapper.get('PUSH_ACCOUNT_ANDROID')
    else:
        return url_mapper.get('PUSH_ACCOUNT_IOS')


def get_recommend_url_v2(hub_id):
    hub_id = int(hub_id)
    url = HOST_PRODUCT + '/products/v2/hubs/{0}/recommend/'.format(hub_id)
    return url


def get_review_url(product_id, page, limit):
    url = get_url('PRODUCT_REVIEW') + '/{0}/reviews?page={1}&limit={2}'.format(
        product_id, page, limit
    )
    return url


def get_expert_review_url(product_id):
    return get_url('PRODUCT') + '/{0}/experts'.format(product_id)


def get_time_table_url(hub_id, sales_time):
    return get_url('TIMETABLE_LIST') + '/{0}?sales_time={1}'.format(hub_id, sales_time)


def get_time_table_url_v2(hub_id):
    return get_url('TIMETABLE_LIST_V2') + '/{0}'.format(hub_id)
