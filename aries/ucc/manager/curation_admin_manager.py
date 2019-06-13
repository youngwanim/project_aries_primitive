import json
from collections import namedtuple

from django.core.paginator import Paginator

from aries.common.exceptions.exceptions import DataValidationError
from aries.ucc.common.curation_func import create_article_validation
from aries.ucc.serializers import CurationArticleSerializer, CurationPageSerializer
from aries.ucc.service.article_service import ArticleService
from aries.ucc.service.curation_service import CurationService
from aries.ucc.service.dp_schedule_service import DisplayScheduleService


def content_to_json(content):
    if type(content['text_data']) == str:
        content['text_data'] = json.loads(content['text_data'])
    if type(content['media_data']) == str:
        content['media_data'] = json.loads(content['media_data'])
    if type(content['tag_data']) == str:
        content['tag_data'] = json.loads(content['tag_data'])
    if type(content['award_data']) == str:
        content['award_data'] = json.loads(content['award_data'])

    return content


def json_to_content(content):
    content['text_data'] = json.dumps(content['text_data'])
    content['media_data'] = json.dumps(content['media_data'])
    content['tag_data'] = json.dumps(content['tag_data'])
    content['award_data'] = json.dumps(content['award_data'])

    return content


class CurationAdminManager:

    ACT_PRODUCT_DETAIL = 4
    ACT_URL_WITHOUT_PR = 13

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.article_service = ArticleService(self.logger_info, self.logger_error)
        self.curation_service = CurationService(self.logger_info, self.logger_error)
        self.display_service = DisplayScheduleService(self.logger_info, self.logger_error)

    """
    Curation article functions
    """
    def create_curation_article(self, article, content_en, content_cn):
        if article['action_type'] == self.ACT_PRODUCT_DETAIL:
            article['action_target'] = json.dumps(article['action_target'])

        if article['action_type'] == self.ACT_URL_WITHOUT_PR:
            article['action_extra'] = json.dumps(article['action_extra'])

        content_en = json_to_content(content_en)
        content_cn = json_to_content(content_cn)

        create_article_validation(article, content_en, content_cn)

        result_article = self.article_service.create_article(article, content_en, content_cn)
        article = result_article['article']

        if article['action_type'] == self.ACT_PRODUCT_DETAIL:
            article['action_target'] = json.loads(article['action_target'])

        if article['action_type'] == self.ACT_URL_WITHOUT_PR:
            article['action_extra'] = json.loads(article['action_extra'])

        content_to_json(article['content_en'])
        content_to_json(article['content_cn'])

        return result_article

    def read_curation_article_list(self, page, limit, layout_type=-1):
        if layout_type != -1:
            query_str = {'layout_type': layout_type}
        else:
            query_str = {}

        article_list = self.article_service.read_article_with_query(query_str)
        article_count = article_list.count()

        paginator = Paginator(article_list, limit)
        article_object_list = paginator.page(page).object_list

        article_list_data = CurationArticleSerializer(article_object_list, many=True).data

        for article in article_list_data:
            if article['action_type'] == self.ACT_PRODUCT_DETAIL:
                article['action_target'] = json.loads(article['action_target'])

            if article['action_type'] == self.ACT_URL_WITHOUT_PR:
                article['action_extra'] = json.loads(article['action_extra'])

            content_en = self.article_service.read_article_content_with_language(article['id'], 0)
            content_cn = self.article_service.read_article_content_with_language(article['id'], 1)
            article['content_en'] = content_to_json(content_en)
            article['content_cn'] = content_to_json(content_cn)

        ArticleList = namedtuple("ArticleList", 'article_list article_count')
        return ArticleList(article_list_data, article_count)

    def update_curation_article(self, article, content_en, content_cn):
        if article['action_type'] == self.ACT_PRODUCT_DETAIL:
            article['action_target'] = json.dumps(article['action_target'])

        if article['action_type'] == self.ACT_URL_WITHOUT_PR:
            article['action_extra'] = json.dumps(article['action_extra'])

        content_en = json_to_content(content_en)
        content_cn = json_to_content(content_cn)

        result_article = self.article_service.update_article(article, content_en, content_cn)
        article = result_article['article']

        if article['action_type'] == self.ACT_PRODUCT_DETAIL:
            article['action_target'] = json.loads(article['action_target'])

        if article['action_type'] == self.ACT_URL_WITHOUT_PR:
            article['action_extra'] = json.loads(article['action_extra'])

        content_to_json(article['content_en'])
        content_to_json(article['content_cn'])

        return result_article

    def delete_curation_article(self, article_id):
        curation_page = self.curation_service.admin_read_all_curation_page()
        page_data = CurationPageSerializer(curation_page, many=True).data

        for page in page_data:
            articles = page['articles']

            if article_id in articles:
                raise DataValidationError('Articles can be deleted without registering in page object.', None)

        return self.article_service.delete_article(article_id)

    """
    Curation page functions
    """
    def read_curation_page_list(self, status, layout_type=-1):
        query_str = {'status': status}

        if layout_type != -1:
            query_str['layout_type'] = layout_type

        page_list = self.curation_service.admin_read_curation_page(query_str)
        page_list_data = CurationPageSerializer(page_list, many=True).data

        for page in page_list_data:
            # Content
            content_en = self.curation_service.admin_read_curation_page_content(page['id'], 0)
            content_cn = self.curation_service.admin_read_curation_page_content(page['id'], 1)
            page['content_en'] = content_en
            page['content_cn'] = content_cn

            # Article data
            article_list = []

            for article_id in page['articles']:
                article_ins = self.article_service.read_article_instance_with_id(article_id)
                article_data = CurationArticleSerializer(article_ins).data
                content_en = self.article_service.read_article_content_with_language(article_id, 0)
                content_cn = self.article_service.read_article_content_with_language(article_id, 1)
                article_data['content_en'] = content_to_json(content_en)
                article_data['content_cn'] = content_to_json(content_cn)
                article_list.append(article_data)

            page['articles'] = article_list

        return page_list_data

    def create_curation_page(self, page, content_en, content_cn):
        return self.curation_service.admin_create_curation_page(page, content_en, content_cn)

    def update_curation_page(self, page, content_en, content_cn):
        page['articles'] = json.dumps(page['articles'])
        return self.curation_service.admin_update_curation_page(page, content_en, content_cn)

    def update_curation_page_list(self, curation_pages):
        return self.curation_service.admin_update_curation_page_list(curation_pages)

    def delete_curation_page(self, page_id):
        return self.curation_service.delete_curation_page(page_id)
