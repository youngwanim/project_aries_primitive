import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import DataValidationError, AuthInfoError, BusinessLogicError
from aries.common.http_utils import header_parser
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse
from aries.common.utils.user_util import check_auth_info_v2

from aries.users.common.address_func import address_req_validation, address_create_data_check, address_select_validation
from aries.users.manager.address_manager_v2 import AddressManagerV2


class UserAddressList(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def get(self, request):
        self.logger_info.info('[UserAddressList][get]')

        auth_info = header_parser.parse_auth_info(request)

        try:
            address_req_validation(auth_info.open_id, auth_info.access_token)
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            # Read latest address list
            address_manager = AddressManagerV2(self.logger_info, self.logger_error)
            address_list = address_manager.get_address_list(auth_info.open_id)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('user_addresses', address_list)

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        request_data = request.data
        self.logger_info.info('[UserAddressList][post][' + str(request_data) + ']')

        auth_info = header_parser.parse_auth_info(request)

        try:
            address_req_validation(auth_info.open_id, auth_info.access_token)
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            # Request data check
            address_create_data_check(request_data)

            # Create user address
            address_manager = AddressManagerV2(self.logger_info, self.logger_error)
            created_address = address_manager.create_address(auth_info.open_id, request_data)

            # Read latest address list
            address_list = address_manager.get_address_list(auth_info.open_id)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('user_addresses', address_list)
            result.set('user_address_id', created_address['id'])

        return Response(result.get_response(), result.get_code())


class UserAddressDetail(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def get(self, request, address_id):
        self.logger_info.info('[UserAddressDetail][get][' + str(address_id) + ']')
        auth_info = header_parser.parse_auth_info(request)

        try:
            address_req_validation(auth_info.open_id, auth_info.access_token)
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            # Read specific address
            address_manager = AddressManagerV2(self.logger_info, self.logger_error)
            user_address = address_manager.get_address(auth_info.open_id, int(address_id))
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('user_address', user_address)

        return Response(result.get_response(), result.get_code())

    def put(self, request, address_id):
        request_data = request.data
        self.logger_info.info('[UserAddressDetail][put][' + str(request_data) + ']')
        auth_info = header_parser.parse_auth_info(request)

        try:
            address_req_validation(auth_info.open_id, auth_info.access_token)
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            # Update address
            address_manager = AddressManagerV2(self.logger_info, self.logger_error)
            updated_address = address_manager.update_address(auth_info.open_id, int(address_id), request_data)

            # Read latest address list
            address_list = address_manager.get_address_list(auth_info.open_id)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('user_addresses', address_list)
            result.set('user_address_id', updated_address['id'])

        return Response(result.get_response(), result.get_code())

    def delete(self, request, address_id):
        self.logger_info.info('[UserAddressDetail][delete][' + str(address_id) + ']')
        auth_info = header_parser.parse_auth_info(request)

        try:
            address_req_validation(auth_info.open_id, auth_info.access_token)
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            # Delete address
            address_manager = AddressManagerV2(self.logger_info, self.logger_error)
            result_map = address_manager.delete_address(auth_info.open_id, int(address_id))

            # Read latest address list
            address_list = address_manager.get_address_list(auth_info.open_id)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('user_addresses', address_list)
            result.set_map(result_map)

        return Response(result.get_response(), result.get_code())


class UserAddressSelector(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def put(self, request, address_id):
        self.logger_info.info('[UserAddressSelector][put][' + str(address_id) + ']')
        auth_info = header_parser.parse_auth_info(request)

        try:
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            # Get address data
            address_manager = AddressManagerV2(self.logger_info, self.logger_error)
            address_data = address_manager.get_address(auth_info.open_id, address_id)

            # Check delivery area
            address_select_validation(address_data['delivery_area'])

            # Select address
            address_list = address_manager.select_address(auth_info.open_id, int(address_id))
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('user_addresses', address_list)

        return Response(result.get_response(), result.get_code())


class UserAddressHubSelector(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def put(self, request, hub_id):
        self.logger_info.info('[UserAddressHubSelector][put][' + str(hub_id) + ']')
        auth_info = header_parser.parse_auth_info(request)
        lang_info = parse_language_v2(request.META)

        try:
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            address_manager = AddressManagerV2(self.logger_info, self.logger_error)
            address_list = address_manager.select_hub(auth_info.open_id, lang_info.cn_header, int(hub_id))
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('user_addresses', address_list)

        return Response(result.get_response(), result.get_code())