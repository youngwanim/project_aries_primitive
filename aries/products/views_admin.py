import datetime
import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import DataValidationError, BusinessLogicError, AuthInfoError
from aries.common.http_utils import api_request_util
from aries.common.http_utils import header_parser
from aries.common.http_utils.api_request_util import get_admin_token_validate_v2
from aries.common.http_utils.header_parser import parse_language_v2
from aries.common.models import ResultResponse
from aries.products.common.admin_func import req_admin_product_update
from aries.products.common.time_bomb_func import create_time_bomb_validation, time_bomb_activation_validation
from aries.products.manager.hub_manager_v2 import HubManagerV2

from aries.products.manager.menu_manager import MenuManager
from aries.products.manager.menu_manager_v2 import MenuManagerV2
from aries.products.manager.product_manager_v3 import ProductManagerV3
from aries.products.manager.stock_manager import StockManager
from aries.products.manager.time_bomb_manager import TimeBombManager


class AdminHubStockV2(APIView):
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    SUCCESS_STR = 'success'

    def get(self, request, hub_id):
        authentication = header_parser.parse_authentication(request)
        if not api_request_util.get_admin_token_validate(authentication[1]):
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))

        stock_manager = StockManager(self.logger_info, self.logger_error)
        hub_stock_result = stock_manager.get_stock_list(hub_id, page, limit)

        result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS_STR)
        result.set('total_count', hub_stock_result[0])
        result.set('hub_stock', hub_stock_result[1])

        return Response(result.get_response(), result.get_code())

    def put(self, request, hub_id):
        authentication = header_parser.parse_authentication(request)
        if not api_request_util.get_admin_token_validate(authentication[1]):
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        hub_stock_list = request.data.get('hub_stock_list', [])

        stock_manager = StockManager(self.logger_info, self.logger_error)
        if not stock_manager.update_stock_list(hub_id, hub_stock_list):
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Internal error')
            return Response(result.get_response(), result.get_code())

        result = ResultResponse(code.ARIES_200_SUCCESS, self.SUCCESS_STR)
        return Response(result.get_response(), result.get_code())


class AdminProductV2(APIView):
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    def get(self, request, hub_id):
        self.logger_info.info('[AdminProductV2][get][' + hub_id + ']')

        lang_info = parse_language_v2(request.META)
        target_db = lang_info.target_db
        cn_header = lang_info.cn_header

        today_str = str(datetime.datetime.today())[:10]
        start_date = str(request.GET.get('start_date', today_str))
        end_date = str(request.GET.get('end_date', today_str))

        try:
            product_manager = ProductManagerV3(self.logger_info, self.logger_error)
            product_list = product_manager.get_product_list_with_query(hub_id, start_date, end_date)

            menu_manager = MenuManagerV2(self.logger_info, self.logger_error)

            for product in product_list:
                menu_manager.get_menu_data(product, target_db, cn_header)
                menu_data = product['menu']
                product['menu'] = {
                    'image_main': menu_data['image_main'],
                    'name': menu_data['name'],
                    'restaurant_name': menu_data['restaurant']['name']
                }

                product_data = product_manager.get_product_data(product['id'])
                product['badge_en'] = json.loads(product_data['badge_en'])
                product['badge_cn'] = json.loads(product_data['badge_cn'])
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('product_list', product_list)
            result.set('hub_id', int(hub_id))

        return Response(result.get_response(), result.get_code())


class AdminProductDetailV2(APIView):
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    def put(self, request):
        request_data = request.data

        self.logger_info.info('[AdminProductDetailV2][put][' + str(request_data) + ']')

        try:
            req_admin_product_update(request_data)

            product_manager = ProductManagerV3(self.logger_info, self.logger_error)
            product_data = product_manager.update_product(request_data)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except BusinessLogicError as instance:
            message, err_code, data_set = instance.args
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, message, err_code)
            result.set_map(data_set)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('product', product_data)

        return Response(result.get_response(), result.get_code())


class AdminMenuListV2(APIView):
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        # authentication = header_parser.parse_authentication(request)
        #
        # if not api_request_util.get_admin_token_validate(authentication[1]):
        #     logger_error.error('Token grant error')
        #     result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
        #     return Response(result.get_response(), result.get_code())

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 100))

        try:
            menu_manager = MenuManager(self.logger_info, self.logger_error)
            menus = menu_manager.get_menu_list(page, limit)
            menus_cn = menu_manager.get_menu_list(page, limit, 'aries_cn')
            menu_count = menu_manager.get_menu_count()

            result.set('menus', menus)
            result.set('menus_cn', menus_cn)
            result.set('total_count', menu_count)
        except ObjectDoesNotExist:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Object not found')
        except Exception as e:
            self.logger_info.info(str(e))
            print(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        authentication = header_parser.parse_authentication(request)

        if not api_request_util.get_admin_token_validate(authentication[1]):
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        try:
            request_data = request.data
            menu_en = request_data['menu_en']
            menu_cn = request_data['menu_cn']
        except Exception as e:
            self.logger_error.error(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        try:
            menu_manager = MenuManager(self.logger_info, self.logger_error)
            result = menu_manager.create_menu(menu_en, menu_cn)
        except Exception as e:
            self.logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data error')

        return Response(result.get_response(), result.get_code())


class TimeBombAdminList(APIView):
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    def get(self, request, hub_id):
        auth_info = header_parser.parse_auth_info(request)

        try:
            get_admin_token_validate_v2(auth_info.access_token)

            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            time_bomb_list = time_bomb_manager.get_time_bomb_list(hub_id)
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
            self.logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e), None)
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('time_bomb_list', time_bomb_list)

        return Response(result.get_response(), result.get_code())

    def post(self, request, hub_id):
        auth_info = header_parser.parse_auth_info(request)
        request_data = request.data

        try:
            # Request data validation
            create_time_bomb_validation(request_data)

            time_bomb = request_data['time_bomb']
            tb_content_en = time_bomb['time_bomb_content_en']
            tb_content_cn = time_bomb['time_bomb_content_cn']

            del time_bomb['time_bomb_content_en']
            del time_bomb['time_bomb_content_cn']

            if 'time_bomb_discount_info' in time_bomb:
                discount_info = time_bomb['time_bomb_discount_info']
                del time_bomb['time_bomb_discount_info']
            else:
                discount_info = []

            # Admin token check
            get_admin_token_validate_v2(auth_info.access_token)

            # Product available check
            product_manager = ProductManagerV3(self.logger_info, self.logger_error)
            product_manager.get_product_validation(discount_info)

            # Get target hub instance
            hub_manager = HubManagerV2(self.logger_info, self.logger_error)
            time_bomb['hub'] = hub_manager.get_hub_instance(int(time_bomb['hub']))

            # Create time bomb
            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            time_bomb_manager.create_time_bomb(time_bomb, tb_content_en, tb_content_cn, discount_info)

            # Get time bomb list
            time_bomb_list = time_bomb_manager.get_time_bomb_list(hub_id)
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
            self.logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e), None)
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('time_bomb_list', time_bomb_list)

        return Response(result.get_response(), result.get_code())


class TimeBombAdminDetail(APIView):
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    def get(self, request, time_bomb_id):
        auth_info = header_parser.parse_auth_info(request)

        try:
            get_admin_token_validate_v2(auth_info.access_token)

            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            time_bomb = time_bomb_manager.get_time_bomb_with_id(time_bomb_id)
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
            self.logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e), None)
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('time_bomb', time_bomb)

        return Response(result.get_response(), result.get_code())

    def put(self, request, time_bomb_id):
        auth_info = header_parser.parse_auth_info(request)
        request_data = request.data

        try:
            get_admin_token_validate_v2(auth_info.access_token)

            # Request data validation
            create_time_bomb_validation(request_data)

            time_bomb = request_data['time_bomb']
            tb_content_en = time_bomb['time_bomb_content_en']
            tb_content_cn = time_bomb['time_bomb_content_cn']

            del time_bomb['time_bomb_content_en']
            del time_bomb['time_bomb_content_cn']

            if 'time_bomb_discount_info' in time_bomb:
                discount_info = time_bomb['time_bomb_discount_info']
                del time_bomb['time_bomb_discount_info']
            else:
                discount_info = []

            # Admin token check
            get_admin_token_validate_v2(auth_info.access_token)

            # Product available check
            product_manager = ProductManagerV3(self.logger_info, self.logger_error)
            product_manager.get_product_validation(discount_info)

            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            time_bomb_manager.update_time_bomb(time_bomb_id, time_bomb, tb_content_en, tb_content_cn, discount_info)
            time_bomb = time_bomb_manager.get_time_bomb_with_id(time_bomb_id)
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
            self.logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e), None)
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('time_bomb', time_bomb)

        return Response(result.get_response(), result.get_code())

    def delete(self, request, time_bomb_id):
        auth_info = header_parser.parse_auth_info(request)

        try:
            get_admin_token_validate_v2(auth_info.access_token)

            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            time_bomb_manager.delete_time_bomb(time_bomb_id)
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
            self.logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e), None)
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())


class TimeBombActivation(APIView):
    logger_info = logging.getLogger('products_info')
    logger_error = logging.getLogger('products_error')

    def post(self, request, time_bomb_id):
        auth_info = header_parser.parse_auth_info(request)
        request_data = request.data

        try:
            get_admin_token_validate_v2(auth_info.access_token)

            # Request data validation
            time_bomb_activation_validation(request_data)

            # Get activate value
            activate = request_data['activate']

            time_bomb_manager = TimeBombManager(self.logger_info, self.logger_error)
            activate_result = time_bomb_manager.set_time_bomb_activate_with_id(time_bomb_id, activate)
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
            self.logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e), None)
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set('result', activate_result)

        return Response(result.get_response(), result.get_code())