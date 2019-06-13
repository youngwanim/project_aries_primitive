import logging
import aries.ucc.common.curation_func as curation_util

from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common.exceptions.exceptions import AuthInfoError, BusinessLogicError, DataValidationError
from aries.common.http_utils import header_parser
from aries.common.http_utils.api_request_util import get_admin_token_validate_v2
from aries.common.models import ResultResponse
from aries.ucc.manager.curation_admin_manager import CurationAdminManager


class CurationArticleAdmin(APIView):

    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    ARTICLE_PAGE = 1
    DEFAULT_LIMIT = 20
    DEFAULT_LAYOUT = -1

    def get(self, request):
        auth_info = header_parser.parse_auth_info(request)
        self.logger_info.info('[CurationArticleAdmin][get][' +
                              str(auth_info.open_id) + str(auth_info.access_token) + ']')

        page = int(request.GET.get('page', self.ARTICLE_PAGE))
        limit = int(request.GET.get('limit', self.DEFAULT_LIMIT))
        layout_type = int(request.GET.get('layout_type', self.DEFAULT_LAYOUT))

        curation_manager = CurationAdminManager(self.logger_info, self.logger_error)

        try:
            # Admin token validate
            get_admin_token_validate_v2(auth_info.access_token)

            # Get article list
            article_result = curation_manager.read_curation_article_list(page, limit, layout_type)
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
            result.set('articles', article_result.article_list)
            result.set('total_count', article_result.article_count)

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        auth_info = header_parser.parse_auth_info(request)
        request_data = request.data

        curation_manager = CurationAdminManager(self.logger_info, self.logger_error)

        self.logger_info.info('[CurationArticleAdmin][post]['
                              + str(auth_info.open_id) + str(auth_info.access_token) + ']')
        self.logger_info.info('[CurationArticleAdmin][post][' + str(request_data) + ']')

        try:
            # Admin token validate
            get_admin_token_validate_v2(auth_info.access_token)

            # Data validation
            curation_util.article_post_validation(request_data)

            article = request_data['article']
            content_en = article['content_en']
            content_cn = article['content_cn']
            del article['content_en']
            del article['content_cn']

            # Create curation article
            curation_article = curation_manager.create_curation_article(article, content_en, content_cn)
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
            result.set_map(curation_article)

        return Response(result.get_response(), result.get_code())

    def put(self, request):
        auth_info = header_parser.parse_auth_info(request)
        request_data = request.data

        curation_manager = CurationAdminManager(self.logger_info, self.logger_error)

        self.logger_info.info('[CurationArticleAdmin][put]['
                              + str(auth_info.open_id) + str(auth_info.access_token) + ']')
        self.logger_info.info('[CurationArticleAdmin][put][' + str(request_data) + ']')

        try:
            # Admin token validate
            get_admin_token_validate_v2(auth_info.access_token)

            # Data validation
            curation_util.article_post_validation(request_data)

            article = request_data['article']
            content_en = article['content_en']
            content_cn = article['content_cn']
            del article['content_en']
            del article['content_cn']

            # Create curation article
            curation_article = curation_manager.update_curation_article(article, content_en, content_cn)
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
            result.set_map(curation_article)

        return Response(result.get_response(), result.get_code())


class CurationArticleAdminDetail(APIView):
    logger_info = logging.getLogger('users_info')
    logger_error = logging.getLogger('users_error')

    def delete(self, request, article_id):
        auth_info = header_parser.parse_auth_info(request)
        curation_manager = CurationAdminManager(self.logger_info, self.logger_error)

        self.logger_info.info('[CurationArticleAdmin][delete]['
                              + str(auth_info.open_id) + str(auth_info.access_token) + ']')

        try:
            # Admin token validate
            get_admin_token_validate_v2(auth_info.access_token)

            # Data validation
            curation_util.get_article_validation(int(article_id))

            # Delete article
            curation_manager.delete_curation_article(int(article_id))
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


class CurationPageAdmin(APIView):

    logger_info = logging.getLogger('ucc_info')
    logger_error = logging.getLogger('ucc_error')

    DEFAULT_PAGE = 1
    DEFAULT_LIMIT = 20
    LAYOUT_TYPE = -1
    VISIBLE = 1

    def get(self, request):
        auth_info = header_parser.parse_auth_info(request)
        self.logger_info.info('[CurationPageAdmin][get]['
                              + str(auth_info.open_id) + str(auth_info.access_token) + ']')

        status = int(request.GET.get('status', self.VISIBLE))

        curation_manager = CurationAdminManager(self.logger_info, self.logger_error)

        try:
            # Admin token validate
            get_admin_token_validate_v2(auth_info.access_token)

            page_list = curation_manager.read_curation_page_list(status, self.LAYOUT_TYPE)
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
            result.set('curation_pages', page_list)

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        auth_info = header_parser.parse_auth_info(request)
        request_data = request.data

        curation_manager = CurationAdminManager(self.logger_info, self.logger_error)

        self.logger_info.info('[CurationPageAdmin][post]['
                              + str(auth_info.open_id) + str(auth_info.access_token) + ']')
        self.logger_info.info('[CurationPageAdmin][post][' + str(request_data) + ']')

        try:
            curation_util.page_post_validation(request_data)

            # Admin token validate
            get_admin_token_validate_v2(auth_info.access_token)

            # Page data separation
            curation_page = request_data['curation_page']

            content_en = curation_page['content_en']
            content_cn = curation_page['content_cn']
            del curation_page['content_en']
            del curation_page['content_cn']

            curation_page = curation_manager.create_curation_page(curation_page, content_en, content_cn)
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
            result.set('curation_page', curation_page)

        return Response(result.get_response(), result.get_code())

    def put(self, request):
        auth_info = header_parser.parse_auth_info(request)
        request_data = request.data

        curation_manager = CurationAdminManager(self.logger_info, self.logger_error)

        self.logger_info.info('[CurationPageAdmin][put]['
                              + str(auth_info.open_id) + str(auth_info.access_token) + ']')
        self.logger_info.info('[CurationPageAdmin][put][' + str(request_data) + ']')

        try:
            curation_util.page_post_validation(request_data)

            # Admin token validate
            get_admin_token_validate_v2(auth_info.access_token)

            # Page data separation
            curation_page = request_data['curation_page']
            content_en = curation_page['content_en']
            content_cn = curation_page['content_cn']
            del curation_page['content_en']
            del curation_page['content_cn']

            curation_page = curation_manager.update_curation_page(curation_page, content_en, content_cn)
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
            result.set('curation_page', curation_page)

        return Response(result.get_response(), result.get_code())


class CurationPageListAdmin(APIView):
    logger_info = logging.getLogger('ucc_info')
    logger_error = logging.getLogger('ucc_error')

    STATUS_VISIBLE = 1
    LAYOUT_DEFAULT = -1

    def put(self, request):
        auth_info = header_parser.parse_auth_info(request)
        request_data = request.data

        curation_manager = CurationAdminManager(self.logger_info, self.logger_error)

        self.logger_info.info('[CurationPageListAdmin][put]['
                              + str(auth_info.open_id) + str(auth_info.access_token) + ']')
        self.logger_info.info('[CurationPageListAdmin][put][' + str(request_data) + ']')

        try:
            # Request validation
            curation_util.page_list_update_post_validation(request_data)

            # Admin token validate
            get_admin_token_validate_v2(auth_info.access_token)

            curation_pages = request_data['curation_pages']
            curation_manager.update_curation_page_list(curation_pages)
            page_list = curation_manager.read_curation_page_list(self.STATUS_VISIBLE, self.LAYOUT_DEFAULT)
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
            result.set('curation_pages', page_list)

        return Response(result.get_response(), result.get_code())


class CurationPageAdminDetail(APIView):
    logger_info = logging.getLogger('ucc_info')
    logger_error = logging.getLogger('ucc_error')

    def delete(self, request, page_id):
        auth_info = header_parser.parse_auth_info(request)

        curation_manager = CurationAdminManager(self.logger_info, self.logger_error)

        self.logger_info.info('[CurationPageAdmin][delete]['
                              + str(auth_info.open_id) + str(auth_info.access_token) + ']')
        try:
            # Admin token validate
            get_admin_token_validate_v2(auth_info.access_token)

            curation_util.get_article_validation(page_id)
            curation_manager.delete_curation_page(page_id)
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
