import requests

from aries.common import urlmapper
from aries.common.exceptions.exceptions import DataValidationError


def coupon_operation(open_id, access_token, operator, count):
    url = urlmapper.get_url('USER_NOTIFICATION') + '/coupon/' + str(operator) + '/' + str(count)
    headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}
    requests.get(url, headers=headers)


def coupon_issue_validation(request_data):
    if 'coupon_list' not in request_data or 'open_id' not in request_data:
        raise DataValidationError('Request data invalid', None)

    if 'coupon_code' not in request_data or 'sender_id' not in request_data:
        raise DataValidationError('Request data invalid', None)


def member_coupon_issue_validation(request_data):
    if 'open_id' not in request_data:
        raise DataValidationError('Request data invalid', None)


def member_promotion_filtering(member_promotion):
    if 'id' in member_promotion:
        del member_promotion['id']
    if 'coupon_id' in member_promotion:
        del member_promotion['coupon_id']
    if 'coupon_code' in member_promotion:
        del member_promotion['coupon_code']
    if 'coupon_days' in member_promotion:
        del member_promotion['coupon_days']
    if 'sender_id' in member_promotion:
        del member_promotion['sender_id']

    return member_promotion
