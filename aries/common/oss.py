import hashlib
import locale
import datetime
import base64
import hmac


def get_oss_header(filename, verb, content_md5, content_type, oss_domain):
    access_id = 'viastelle'
    access_key_secret = b'viastelle'

#    access_dummy_secret = b"OtxrzxIsfpFjA7SwPzILwy8Bw21TLhquhboDYROV"
#    new_raw = b"PUT\nODBGOERFMDMzQTczRUY3NUE3NzA5QzdFNUYzMDQxNEM=\ntext/html\nThu, 17 Nov 2005 18:49:58 GMT\nx-oss-magic:abracadabra\nx-oss-meta-platform:foo@bar.com\n/oss-example/nelson"

    today_utc = get_gmt_date()

    raw = bytes(verb + '\n' + content_md5 + '\nimage/'
                + content_type + '\n' + today_utc + '\n' + oss_domain + filename, encoding='utf-8')

    print(raw.decode('utf-8'))

    h = hmac.new(access_key_secret, raw, digestmod=hashlib.sha1)

    signature = base64.encodebytes(h.digest()).strip()
    print(signature.decode('utf-8'))

    return 'OSS ' + access_id + ':' + signature.decode('utf-8')


def get_gmt_date():
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
