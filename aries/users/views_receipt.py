import logging
import aries.users.common.receipt_func as receipt_util

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import BusinessLogicError, DataValidationError, AuthInfoError
from aries.common.http_utils import header_parser
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse
from aries.common.utils.user_util import check_auth_info_v2

from aries.users.manager.receipt_manager import ReceiptManager


class UserReceiptList(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def get(self, request):
        self.logger_info.info('[UserReceiptList][get]')
        auth_info = header_parser.parse_auth_info(request)
        lang_info = parse_language_v2(request.META)

        try:
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            receipt_manager = ReceiptManager(self.logger_info, self.logger_error)
            receipt_list = receipt_manager.read_user_receipt(auth_info.open_id, lang_info.cn_header)
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
            result.set('user_receipts', receipt_list)

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        request_data = request.data
        self.logger_info.info('[UserReceiptList][post][' + str(request_data) + ']')
        auth_info = header_parser.parse_auth_info(request)
        lang_info = parse_language_v2(request.META)

        try:
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            receipt_util.request_validation(auth_info.open_id, request_data)
            receipt_manager = ReceiptManager(self.logger_info, self.logger_error)
            receipt_list = receipt_manager.create_user_receipt(auth_info.open_id, request_data, lang_info.cn_header)
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
            result.set('user_receipts', receipt_list)

        return Response(result.get_response(), result.get_code())


class UserReceiptDetail(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def put(self, request, receipt_id):
        request_data = request.data
        self.logger_info.info('[UserReceiptDetail][put][' + str(request_data) + ']')
        auth_info = header_parser.parse_auth_info(request)
        lang_info = parse_language_v2(request.META)

        try:
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)
            receipt_util.request_validation(auth_info.open_id, request_data)

            receipt_manager = ReceiptManager(self.logger_info, self.logger_error)
            receipt_list = receipt_manager.update_user_receipt(
                auth_info.open_id, int(receipt_id), request_data, lang_info.cn_header)
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
            result.set('user_receipts', receipt_list)

        return Response(result.get_response(), result.get_code())

    def delete(self, request, receipt_id):
        self.logger_info.info('[UserReceiptDetail][delete]')
        auth_info = header_parser.parse_auth_info(request)
        lang_info = parse_language_v2(request.META)

        try:
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            receipt_manager = ReceiptManager(self.logger_info, self.logger_error)
            receipt_list = receipt_manager.delete_user_receipt(auth_info.open_id, int(receipt_id), lang_info.cn_header)
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
            result.set('user_receipts', receipt_list)

        return Response(result.get_response(), result.get_code())


class UserReceiptSelect(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def put(self, request, receipt_id):
        self.logger_info.info('[UserReceiptDetail][get][' + str(receipt_id) + ']')
        auth_info = header_parser.parse_auth_info(request)
        lang_info = parse_language_v2(request.META)

        try:
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            receipt_manager = ReceiptManager(self.logger_info, self.logger_error)
            receipt_manager.select_user_receipt(auth_info.open_id, int(receipt_id))

            user_receipts = receipt_manager.read_user_receipt(auth_info.open_id, lang_info.cn_header)
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
            result.set('user_receipts', user_receipts)

        return Response(result.get_response(), result.get_code())
