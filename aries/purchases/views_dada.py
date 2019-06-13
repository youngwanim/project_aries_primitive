import logging
import aries.purchases.common.dada_func as dada_util

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import DataValidationError, AuthInfoError, BusinessLogicError
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse

from aries.purchases.manager.dada_manager import DadaManager


class DadaOrder(APIView):
    logger_info = logging.getLogger('purchases_info')
    logger_error = logging.getLogger('purchases_error')

    def get(self, request, order_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        auth_info = header_parser.parse_auth_info(request)
        self.logger_info.info(auth_info.access_token)

        dada_manager = DadaManager(self.logger_info, self.logger_error)

        try:
            # Read dada detail
            dada_order_data = dada_manager.read_order_detail(order_id)
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
            result.set('shipping_order_detail', dada_order_data)

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        request_data = request.data
        self.logger_info.info(request_data)

        dada_manager = DadaManager(self.logger_info, self.logger_error)

        try:
            # request data validation
            dada_util.dada_new_order_validation(request_data)
            order_id = request_data['order_id']
            receiver_address = request_data['receiver_address']
            receiver_lat = request_data['receiver_lat']
            receiver_lng = request_data['receiver_lng']

            # Make a new order
            dada_manager.add_order(request_data)

            # Make a new order detail
            dada_manager.add_order_detail(order_id, receiver_address, receiver_lat, receiver_lng)

            # Read dada order detail
            dada_order_data = dada_manager.read_order_detail(order_id)
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
            result.set('shipping_order_detail', dada_order_data)

        return Response(result.get_response(), result.get_code())


class DadaAddTip(APIView):
    logger_info = logging.getLogger('purchases_info')
    logger_error = logging.getLogger('purchases_error')

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        request_data = request.data
        self.logger_info.info(request_data)

        dada_manager = DadaManager(self.logger_info, self.logger_error)

        try:
            # request data validation
            dada_util.dada_order_add_tip_validation(request_data)

            order_id = request_data['order_id']
            tips = request_data['tips']
            city_code = request_data['city_code']
            info = request_data['info']

            # add order tips
            dada_manager.add_tip(order_id, tips, city_code, info)

            # Read dada detail
            dada_order_data = dada_manager.update_order_detail(order_id)
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
            result.set('shipping_order_detail', dada_order_data)

        return Response(result.get_response(), result.get_code())


class DadaReOrder(APIView):
    logger_info = logging.getLogger('purchases_info')
    logger_error = logging.getLogger('purchases_error')

    def post(self, request):
        request_data = request.data

        self.logger_info.info(request_data)

        dada_manager = DadaManager(self.logger_info, self.logger_error)

        try:
            # Request data validation
            dada_util.dada_new_order_validation(request_data)

            # Request data parsing
            order_id = request_data['order_id']

            # Make a new order
            dada_manager.re_add_order(request_data)

            # Read dada detail
            dada_order_data = dada_manager.update_order_detail(order_id)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('shipping_order_detail', dada_order_data)

        return Response(result.get_response(), result.get_code())


class DadaOrderCancel(APIView):
    logger_info = logging.getLogger('purchases_info')
    logger_error = logging.getLogger('purchases_error')

    def post(self, request):
        request_data = request.data

        self.logger_info.info(request_data)

        try:
            # Request data validation
            dada_util.dada_cancel_order_validation(request_data)

            # Request data parsing
            order_id = request_data['order_id']
            cancel_reason_id = request_data['cancel_reason_id']

            # Cancel order request
            dada_manager = DadaManager(self.logger_info, self.logger_error)
            cancel_result = dada_manager.cancel_order(order_id, cancel_reason_id)

            # Read dada detail
            dada_order_data = dada_manager.update_order_detail(order_id)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except AuthInfoError:
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Authentication error')
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('deduct_fee', cancel_result['deduct_fee'])
            result.set('shipping_order_detail', dada_order_data)

        return Response(result.get_response(), result.get_code())


class DadaCallbackDetail(APIView):
    logger_info = logging.getLogger('purchases_info')
    logger_error = logging.getLogger('purchases_error')

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        request_data = request.data

        self.logger_info.info(request_data)

        try:
            order_id = request_data['order_id']

            dada_manager = DadaManager(self.logger_info, self.logger_error)
            update_result = dada_manager.update_order_detail(order_id)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            dada_util.dada_message_to_operation(update_result)

        return Response(result.get_response(), result.get_code())


class DadaQueryFee(APIView):
    logger_info = logging.getLogger('purchases_info')
    logger_error = logging.getLogger('purchases_error')

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        request_data = request.data
        self.logger_info.info(request_data)

        dada_manager = DadaManager(self.logger_info, self.logger_error)

        try:
            # request data validation
            dada_util.dada_new_order_validation(request_data)

            # Make a new order
            query_result = dada_manager.query_delivery_fee(request_data)
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
            result.set_map(query_result)

        return Response(result.get_response(), result.get_code())


class DadaAddAfterQuery(APIView):
    logger_info = logging.getLogger('purchases_info')
    logger_error = logging.getLogger('purchases_error')

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        request_data = request.data
        self.logger_info.info(request_data)

        dada_manager = DadaManager(self.logger_info, self.logger_error)

        try:
            # request data validation
            dada_util.dada_order_add_after_query_validation(request_data)

            # Make a new order
            query_result = dada_manager.order_add_after_query(request_data)
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
            result.set_map(query_result)

        return Response(result.get_response(), result.get_code())


class DadaLocationQuery(APIView):
    logger_info = logging.getLogger('purchases_info')
    logger_error = logging.getLogger('purchases_error')

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        request_data = request.data
        self.logger_info.info(request_data)

        dada_manager = DadaManager(self.logger_info, self.logger_error)

        try:
            # request data validation
            dada_util.dada_query_validation(request_data)

            # Make a new order
            query_result = dada_manager.order_location_query(request_data)

            # Select result of query
            selected_result = {
                'orderId': query_result['orderId'],
                'statusCode': query_result['statusCode'],
                'transporterName': query_result['transporterName'],
                'transporterPhone': query_result['transporterPhone'],
                'transporterLng': query_result['transporterLng'],
                'transporterLat': query_result['transporterLat'],
                'createTime': query_result['createTime'],
                'acceptTime': query_result['acceptTime'],
                'fetchTime': query_result['fetchTime'],
                'finishTime': query_result['finishTime'],
                'cancelTime': query_result['cancelTime']
            }
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
            result.set_map(selected_result)

        return Response(result.get_response(), result.get_code())
