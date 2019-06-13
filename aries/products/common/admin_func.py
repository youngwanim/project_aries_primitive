from aries.common.exceptions.exceptions import DataValidationError


def req_admin_product_list(hub_id):
    if hub_id != 1 or hub_id != 2:
        msg = 'Request data invalid'
        raise DataValidationError(msg, None)


def req_admin_product_update(product_data):
    if 'id' not in product_data:
        raise DataValidationError('Request data invalid', None)
