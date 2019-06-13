import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import BusinessLogicError, DataValidationError, AuthInfoError
from aries.common.http_utils import header_parser
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse
from aries.purchases.common.reserve_func import request_validation, purchase_validation
from aries.purchases.factory.pay_param_factory import PayParamInstance
from aries.purchases.manager.coupon_manager_v2 import CouponManagerV2
from aries.purchases.manager.order_reserve_manager import OrderReserveManager


class PurchaseOrderV2(APIView):
    logger_info = logging.getLogger('purchases_info')
    logger_error = logging.getLogger('purchases_error')

    def post(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        request_data = request.data
        self.logger_info.info(request_data)

        auth_info = header_parser.parse_auth_info(request)
        lang_info = parse_language_v2(request.META)

        open_id = auth_info.open_id
        access_token = auth_info.access_token
        cn_header = lang_info.cn_header
        accept_lang = lang_info.accept_lang
        os_type = lang_info.os_type
        hub_id = request_data.get('hub_id', 1)

        try:
            # Order reserve manager
            reserve_manager = OrderReserveManager(self.logger_info, self.logger_error, request_data)

            # Request data validation
            request_validation(open_id, access_token, request_data)

            # Request product validation
            validation_result = purchase_validation(accept_lang, request_data, os_type)

            # Product check
            valid_result = reserve_manager.product_validation(validation_result, cn_header)

            # Sales time check
            delivery_time_result = reserve_manager.delivery_time_validation(valid_result, accept_lang,
                                                                            os_type, hub_id)

            # Product detail setting
            product_list = reserve_manager.set_product_detail(delivery_time_result)

            # Delivery detail check
            reserve_manager.set_delivery_detail(lang_info.cn_header)

            # Coupon business logic process, product list from sales_time_response
            coupon_list = request_data['coupon_list']

            coupon_manager = CouponManagerV2(self.logger_info, self.logger_error)
            coupon_manager.coupon_validate(auth_info.open_id, product_list, coupon_list)

            # Calculate total price
            coupon_detail = coupon_manager.get_coupon_detail()
            discount_amount = -coupon_manager.get_discount_price()
            reserve_manager.set_total_price(coupon_detail, discount_amount, open_id)

            # Set misc parameters
            reserve_manager.set_misc_params()

            # Get payment params from payment parameter factory
            param_result = reserve_manager.get_payment_param(cn_header)
            payment_param_factory = PayParamInstance.factory(param_result[0], self.logger_info, self.logger_error)
            payment_params = payment_param_factory.get_payment_params(param_result[1])

            for key in payment_params.keys():
                result.set(key, payment_params[key])

            # Save purchase order object to database
            order_id = reserve_manager.save_purchase_order()
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
            result.set('order_id', order_id)

        return Response(result.get_response(), result.get_code())
