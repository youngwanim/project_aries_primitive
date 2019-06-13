from django.conf import settings

HOST_DEV = 'http://139.196.123.42:8080'

ALIPAY_CALLBACK_URL_DEV = 'http://139.196.123.42:8080/payments/alipay/notification/'
ALIPAY_CALLBACK_URL_STG = 'https://stg-api.viastelle.com/payments/alipay/notification/'
ALIPAY_CALLBACK_URL_REL = 'https://api.viastelle.com/payments/alipay/notification/'

# DATE FORMAT
DATE_WITH_AM_PM = '%Y-%m-%d %I:%M %p'

# QQ platform URL
QQ_CODE_URL = 'https://graph.qq.com/oauth2.0/authorize'
QQ_ACCESS_TOKEN_URL = 'https://graph.qq.com/oauth2.0/token'
QQ_OPEN_ID_URL = 'https://graph.qq.com/oauth2.0/me'

# ALIPAY URL
ALIPAY_REL_URL = 'https://openapi.alipay.com/gateway.do'
ALIPAY_DEV_URL = 'https://openapi.alipaydev.com/gateway.do'

# WeChat URL
WECHAT_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
WECHAT_SANDBOX_SIGN_KEY = 'https://api.mch.weixin.qq.com/sandboxnew/pay/getsignkey'

WECHAT_PREPAID_RELEASE = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
WECHAT_PREPAID_DEV = 'https://api.mch.weixin.qq.com/sandboxnew/pay/unifiedorder'

WECHAT_QUERY_URL = 'https://api.mch.weixin.qq.com/pay/orderquery'
WECHAT_QUERY_URL_DEV = 'https://api.mch.weixin.qq.com/sandboxnew/pay/orderquery'

WECHAT_REFUND_URL = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
WECHAT_REFUND_URL_DEV = 'https://api.mch.weixin.qq.com/sandboxnew/secapi/pay/refund'

WECHAT_NOTIFY_URL_RELEASE = 'https://api.viastelle.com/payments/wechat/notification/'
WECHAT_NOTIFY_URL_STAGE = 'https://stg-api.viastelle.com/payments/wechat/notification/'
WECHAT_NOTIFY_URL_DEV = 'http://139.196.123.42:8080/payments/wechat/notification/'

# Key folder
VIA_PUB_KEY_DEV = '/home/nexttf/workspace/python/project_aries/docs/04.pub_key/alipay_sandbox_pub_key.txt'
VIA_PUB_KEY_STG = '/home/nexttf/workspace/project_aries/docs/04.pub_key/alipay_sandbox_pub_key.txt'
VIA_PUB_KEY_REL = '/home/nexttf/workspace/project_aries/docs/04.pub_key/viastelle_pub_key.txt'

VIA_PRI_KEY_DEV = '/home/nexttf/workspace/python/project_aries/docs/04.pub_key/viastelle_pri_key.txt'
VIA_PRI_KEY_STG = '/home/nexttf/workspace/project_aries/docs/04.pub_key/viastelle_pri_key.txt'
VIA_PRI_KEY_REL = '/home/nexttf/workspace/project_aries/docs/04.pub_key/viastelle_pri_key.txt'

VIA_PUB_KEY_LOCAL = '/Users/keanu/workspace/python/aries_project/config/keys/viastelle_pub_key.txt'
VIA_PRI_KEY_LOCAL = '/Users/keanu/workspace/python/aries_project/config/keys/viastelle_pri_key.txt'

ALIPAY_SANDBOX_APP_ID = 'viastelle'
ALIPAY_APP_ID = 'viastelle'

ALIPAY_CALLBACK_MWEB_DEV = 'https://test.viastelle.com/dist/#/mybag/received'
ALIPAY_CALLBACK_MWEB_STG = 'https://stg-cli.viastelle.com/dist/#/mybag/received'
ALIPAY_CALLBACK_MWEB_REL = 'https://m.viastelle.com/dist/#/mybag/received'


def get_viastelle_pub_key():
    if settings.DEBUG:
        return VIA_PUB_KEY_DEV
    elif settings.STAGE:
        return VIA_PUB_KEY_STG
    else:
        return VIA_PUB_KEY_REL


def get_viastelle_pri_key():
    if settings.DEBUG:
        return VIA_PRI_KEY_DEV
    elif settings.STAGE:
        return VIA_PRI_KEY_STG
    else:
        return VIA_PRI_KEY_REL


def get_alipay_app_id():
    if settings.DEBUG:
        return ALIPAY_SANDBOX_APP_ID
    elif settings.STAGE:
        return ALIPAY_SANDBOX_APP_ID
    else:
        return ALIPAY_APP_ID


def get_alipay_notify_url():
    if settings.DEBUG and not settings.STAGE:
        return ALIPAY_CALLBACK_URL_DEV
    elif settings.STAGE:
        return ALIPAY_CALLBACK_URL_STG
    else:
        return ALIPAY_CALLBACK_URL_REL


def get_callback_url():
    if settings.DEBUG:
        return ALIPAY_CALLBACK_MWEB_DEV
    elif settings.STAGE:
        return ALIPAY_CALLBACK_MWEB_STG
    else:
        return ALIPAY_CALLBACK_MWEB_REL


# WeChat URL function
def get_wechat_prepaid_url():
    if settings.DEBUG:
        return WECHAT_PREPAID_DEV
    elif settings.STAGE:
        return WECHAT_PREPAID_RELEASE
    else:
        return WECHAT_PREPAID_RELEASE


def get_wechat_query_url():
    if settings.DEBUG:
        return WECHAT_QUERY_URL_DEV
    elif settings.STAGE:
        return WECHAT_QUERY_URL
    else:
        return WECHAT_QUERY_URL


def get_wechat_refund_url():
    if settings.DEBUG:
        return WECHAT_REFUND_URL_DEV
    elif settings.STAGE:
        return WECHAT_REFUND_URL
    else:
        return WECHAT_REFUND_URL


def get_wechat_notify_url():
    if settings.DEBUG:
        return WECHAT_NOTIFY_URL_DEV
    elif not settings.DEBUG and settings.STAGE:
        return WECHAT_NOTIFY_URL_STAGE
    else:
        return WECHAT_NOTIFY_URL_RELEASE
