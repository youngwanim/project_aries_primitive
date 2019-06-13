import datetime
import logging

from django.core.cache import caches
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code, product_util
from aries.common.exceptions.exceptions import DataValidationError
from aries.common.http_utils import header_parser
from aries.common.models import ResultResponse
from aries.ucc.common.curation_func import get_article_validation, get_banner_section
from aries.ucc.manager.curation_manager import CurationManager


class Curation(APIView):

    logger_info = logging.getLogger('ucc_info')
    logger_error = logging.getLogger('ucc_error')

    def get(self, request):
        auth_info = header_parser.parse_auth_info(request)
        lang_info = header_parser.parse_language_v2(request.META)

        accept_lang = lang_info.accept_lang
        os_type = lang_info.os_type
        cache_reset = int(request.GET.get('reset', 0))

        self.logger_info.info('[Curation][get][{},{}]'
                              .format(auth_info.open_id, auth_info.access_token))

        hub_id = int(request.GET.get('hub_id', 1))
        curation_manager = CurationManager(self.logger_info, self.logger_error)

        try:
            cache_key = 'curation_list_' + str(hub_id) + '_' + lang_info.accept_lang
            curation_list = caches['redis'].get(cache_key)

            if curation_list is None or cache_reset == 1:
                curation_list = curation_manager.get_curation_list(lang_info.cn_header, hub_id, os_type)

                # Time bomb article add
                curation_section = get_banner_section(curation_list)
                curation_manager.add_time_bomb_information(curation_section, hub_id, accept_lang, os_type)

                # Save cache
                caches['redis'].set(cache_key, curation_list)

        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

            result.set('curation_list', curation_list)
            result.set('total_count', len(curation_list))
            result.set('phase_date', datetime.date.today().isoformat())
            result.set('sales_time', product_util.get_sales_time_str())

        return Response(result.get_response(), result.get_code())


class CurationCacheReset(APIView):

    logger_info = logging.getLogger('ucc_info')
    logger_error = logging.getLogger('ucc_error')

    def get(self, request):
        auth_info = header_parser.parse_auth_info(request)

        self.logger_info.info('[CurationCacheReset][get][{},{}]'
                              .format(auth_info.open_id, auth_info.access_token))

        hub_id = int(request.GET.get('hub_id', 1))

        try:
            cache_key_en = 'curation_list_' + str(hub_id) + '_en'
            cache_key_cn = 'curation_list_' + str(hub_id) + '_zh'
            caches['redis'].delete(cache_key_en)
            caches['redis'].delete(cache_key_cn)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        return Response(result.get_response(), result.get_code())


class CurationDetailList(APIView):

    logger_info = logging.getLogger('ucc_info')
    logger_error = logging.getLogger('ucc_error')

    def get(self, request, page_id):
        auth_info = header_parser.parse_auth_info(request)
        lang_info = header_parser.parse_language_v2(request.META)

        self.logger_info.info('[CurationDetailList][get][{},{}]'.format(auth_info.open_id, auth_info.access_token))

        cn_header = lang_info.cn_header
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        hub_id = int(request.GET.get('hub_id', 1))
        os_type = lang_info.os_type

        try:
            get_article_validation(page_id)

            curation_manager = CurationManager(self.logger_info, self.logger_error)
            detail_result = curation_manager.get_curation_detail(hub_id, cn_header, os_type, page_id, page, limit)
        except DataValidationError as instance:
            message, err_code = instance.args
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, message, err_code)
        except Exception as e:
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, str(e))
        else:
            result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
            result.set_map(detail_result)

        return Response(result.get_response(), result.get_code())
