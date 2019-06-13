from collections import namedtuple


def parse_language(request_meta):
    cn_header = False
    target_db = 'default'
    accept_lang = 'en'
    if request_meta.get('HTTP_ACCEPT_LANGUAGE'):
        accept_lang = request_meta['HTTP_ACCEPT_LANGUAGE']
        if 'zh' in accept_lang:
            target_db = 'aries_cn'
            cn_header = True
    result = (cn_header, target_db, accept_lang)
    return result


def parse_language_v2(request_meta):
    default_os_type = 0
    cn_header = False
    target_db = 'default'
    accept_lang = 'en'
    if request_meta.get('HTTP_ACCEPT_LANGUAGE'):
        accept_lang = request_meta['HTTP_ACCEPT_LANGUAGE']
        if 'zh' in accept_lang or 'Zh' in accept_lang:
            target_db = 'aries_cn'
            cn_header = True
    if 'HTTP_OS_TYPE' in request_meta:
        os_type = int(request_meta['HTTP_OS_TYPE'])
    else:
        os_type = default_os_type
    LanguageInfo = namedtuple("LanguageInfo", 'cn_header target_db accept_lang os_type')
    return LanguageInfo(cn_header, target_db, accept_lang, os_type)


def parse_authentication(request):
    if request.META.get('HTTP_OPEN_ID'):
        open_id = request.META['HTTP_OPEN_ID']
    else:
        open_id = None

    if request.META.get('HTTP_AUTHORIZATION'):
        authorization = str(request.META['HTTP_AUTHORIZATION']).split(' ')
        if len(authorization) >= 2:
            access_token = authorization[1]
        else:
            access_token = None
    else:
        access_token = None

    result = (open_id, access_token)
    return result


# V2 function
def parse_auth_info(request):
    if request.META.get('HTTP_OPEN_ID'):
        open_id = request.META['HTTP_OPEN_ID']
    else:
        open_id = None

    if request.META.get('HTTP_AUTHORIZATION'):
        authorization = str(request.META['HTTP_AUTHORIZATION']).split(' ')
        if len(authorization) >= 2:
            access_token = authorization[1]
        else:
            access_token = None
    else:
        access_token = None

    AuthInfo = namedtuple("AuthInfo", 'open_id access_token')
    return AuthInfo(open_id=open_id, access_token=access_token)
