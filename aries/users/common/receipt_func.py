from aries.common.exceptions.exceptions import DataValidationError


def request_validation(open_id, request_data):
    if open_id is None:
        raise DataValidationError('Request data invalid', None)

    if 'type' not in request_data or 'name' not in request_data or 'tax_id_number' not in request_data:
        raise DataValidationError('Request data invalid', None)

    if request_data['type'] == 0 and len(request_data['name']) == 0:
        raise DataValidationError('Request data invalid', None)
