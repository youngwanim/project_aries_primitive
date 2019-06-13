from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.message_utils import message_mapper


def event_coupon_validator(request, cn_header=True):
    request_data = request.data

    if 'open_id' not in request_data or 'coupon_id' not in request_data:
        raise BusinessLogicError(message_mapper.get(1016, cn_header), 1016)

    return request_data


def auth_info_validator(auth_info, cn_header=True):
    if auth_info[0] is None or auth_info[1] is None:
        raise BusinessLogicError(message_mapper.get(1016, cn_header), 1016)
    return True


def os_info_validator(request, cn_header=True):
    os_type = int(request.GET.get('os_type', 2))

    if os_type > 1:
        raise BusinessLogicError(message_mapper.get(3106, cn_header), 3106)
    return True
