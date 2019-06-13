import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import payment_util
from aries.common import product_util
from aries.common.exceptions.exceptions import DataValidationError, BusinessLogicError, AuthInfoError
from aries.common.http_utils import header_parser
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse
from aries.common.utils.user_util import check_auth_info_v2
from aries.users.common import shopping_bag_func as cart_util
from aries.users.common.shopping_bag_func import cart_inst_validation
from aries.users.manager.user_manager_v2 import UserManagerV2


class ShoppingCart(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def get(self, request):

        auth_info = header_parser.parse_auth_info(request)
        lang_info = parse_language_v2(request.META)

        open_id = auth_info.open_id
        access_token = auth_info.access_token
        cn_header = lang_info.cn_header
        accept_lang = lang_info.accept_lang

        try:
            check_auth_info_v2(auth_info.open_id, auth_info.access_token)

            user_manager = UserManagerV2(self.logger_info, self.logger_error)

            # User information
            user_data = user_manager.get_user_data(open_id)
            user_info = user_manager.get_user_info(open_id)

            # Default hub id
            default_hub_id = user_data['default_hub_id']

            # Latest payment method and shipping method
            latest_payment_method = user_info['latest_payment_method']
            latest_shipping_method = user_info['latest_shipping_method']

            # Latest cart information and special instruction template
            cart_info = user_manager.get_user_cart_info_data(open_id)
            include_cutlery = cart_info['include_cutlery']
            user_inst_template = cart_util.get_user_inst_list(cn_header, cart_info['instruction_history'])
            special_instruction_template = cart_util.get_sp_inst_template(cn_header)

            # Delivery time table information (map)
            delivery_map = cart_util.get_delivery_time(default_hub_id, lang_info.accept_lang)

            # Add order unavailable message
            order_available = delivery_map['order_available']
            order_un_msg = payment_util.get_order_unavailable_msg(cn_header) if not order_available else ''

            # Purchase information (map)
            purchase_map = cart_util.get_purchases_data(open_id, access_token, accept_lang)

            # Next day information
            phase_next_day = product_util.get_phase_next_day()

            # Recommend product information
            products = cart_util.get_recommend_product(default_hub_id, accept_lang)
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
            result.set('latest_payment_method', latest_payment_method)
            result.set('latest_shipping_method', latest_shipping_method)
            result.set('special_instruction_template', special_instruction_template + user_inst_template)
            result.set('order_unavailable_message', order_un_msg)
            result.set('phase_next_day', phase_next_day)
            result.set('products', products)
            result.set('include_cutlery', include_cutlery)
            result.set_map(delivery_map)
            result.set_map(purchase_map)

        return Response(result.get_response(), result.get_code())

    def put(self, request):
        auth_info = header_parser.parse_auth_info(request)
        open_id = auth_info.open_id

        request_data = request.data

        try:
            # Cart request validation
            cart_inst_validation(request_data)

            include_cutlery = request_data['include_cutlery']
            special_instruction = request_data['special_instruction']

            user_manager = UserManagerV2(self.logger_info, self.logger_error)

            # User information
            cart_info = user_manager.get_user_cart_info_data(open_id)
            user_manager.update_cart_info(cart_info, include_cutlery, special_instruction)
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

        return Response(result.get_response(), result.get_code())
