import json

from django.core.paginator import Paginator
from django.db import transaction

from aries.common.exceptions.exceptions import BusinessLogicError
from aries.ucc.models import CurationArticle, CurationContent
from aries.ucc.serializers import CurationArticleSerializer, CurationContentSerializer


def merge_content(article, content):
    # Character data
    article['title'] = content['title']
    article['sub_title'] = content['sub_title']
    article['content'] = content['content']
    article['sub_content'] = content['sub_content']
    # Text data parsing
    article['text_data'] = json.loads(content['text_data'])
    article['media_data'] = json.loads(content['media_data'])
    article['tag_data'] = json.loads(content['tag_data'])
    article['award_data'] = json.loads(content['award_data'])


def get_content_desc(content_type, language_type):
    content_list_en = [
        {'type': 0, 'color': '#f39e15', 'name': 'MOST VIEWED'},
        {'type': 1, 'color': '#e72b27', 'name': 'FEATURE'},
        {'type': 2, 'color': '#8dc130', 'name': 'STYLISH WAY'},
        {'type': 3, 'color': '#27afe7', 'name': 'INTERVIEW'},
    ]

    content_list_cn = [
        {'type': 0, 'color': '#f39e15', 'name': 'MOST VIEWED(CHN)'},
        {'type': 1, 'color': '#e72b27', 'name': 'FEATURE(CHN)'},
        {'type': 2, 'color': '#8dc130', 'name': 'STYLISH WAY(CHN)'},
        {'type': 3, 'color': '#27afe7', 'name': 'INTERVIEW(CHN)'},
    ]

    mapping_list = content_list_en if language_type == 0 else content_list_cn
    return mapping_list[content_type]


def merge_content_type(article, content_type, layout_type, language_type):
    if layout_type == 3:
        content_type_desc = get_content_desc(content_type, language_type)
        content_type_desc['name'] = article['title']
        article['content_type_desc'] = content_type_desc


def merge_action_type(article, action_type):
    if action_type == 13:
        action_extra = json.loads(article['action_extra'])
        if action_extra['share_enable']:
            media_data = article['media_data']
            if len(media_data) >= 1:
                new_extra = {
                    'share_image': media_data[0]['detail'],
                    'share_title': article['title'],
                    'share_description': article['content'],
                    'share_enable': True,
                    'title': article['title'],
                    'link': article['action_target']
                }
                article['action_extra'] = json.dumps(new_extra)


class ArticleService:
    LANG_EN = 0
    LANG_CN = 1

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def create_article(self, article, content_en, content_cn):
        try:
            with transaction.atomic():
                article_instance = CurationArticle.objects.create(**article)

                content_en['curation_article'] = article_instance
                content_cn['curation_article'] = article_instance

                content_en_ins = CurationContent.objects.create(**content_en)
                content_cn_ins = CurationContent.objects.create(**content_cn)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            article_data = CurationArticleSerializer(article_instance).data
            content_en_data = CurationContentSerializer(content_en_ins).data
            content_cn_data = CurationContentSerializer(content_cn_ins).data

            article_data['content_en'] = content_en_data
            article_data['content_cn'] = content_cn_data

            self.result = {
                'article': article_data,
            }

        return self.result

    def read_article_with_id(self, article_id, lang_type=0):
        try:
            article_instance = CurationArticle.objects.get(id=article_id)
            article_data = CurationArticleSerializer(article_instance).data
            article_content_data = self.read_article_content_with_language(article_id, lang_type)
            merge_content(article_data, article_content_data)

            content_type = article_instance.content_type
            layout_type = article_instance.layout_type
            action_type = article_instance.action_type
            merge_content_type(article_data, content_type, layout_type, lang_type)
            merge_action_type(article_data, action_type)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = article_data

        return self.result

    def read_article_instance_with_id(self, article_id):
        try:
            article_instance = CurationArticle.objects.get(id=article_id)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = article_instance

        return self.result

    def read_article_with_query(self, query_str):
        try:
            article_qs = CurationArticle.objects.filter(**query_str)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = article_qs

        return self.result

    def read_article_with_page(self, query_str, page, limit):
        try:
            article_qs = CurationArticle.objects.filter(**query_str)
            article_count = article_qs.count()

            paginator = Paginator(article_qs, limit)

            article_list_obj = paginator.page(page).object_list
            article_list_data = CurationArticleSerializer(article_list_obj, many=True).data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = {'total_count': article_count, 'articles': article_list_data}

        return self.result

    def read_article_content_with_language(self, article_id, language_type=0):
        try:
            article_content_instance = CurationContent.objects.get(
                curation_article=article_id, language_type=language_type
            )
            article_content_data = CurationContentSerializer(article_content_instance).data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = article_content_data

        return self.result

    def update_article(self, article_data, content_en, content_cn):
        try:
            article_id = article_data['id']
            article_ins = CurationArticle.objects.get(id=article_id)
            content_en_ins = CurationContent.objects.get(curation_article=article_ins, language_type=self.LANG_EN)
            content_cn_ins = CurationContent.objects.get(curation_article=article_ins, language_type=self.LANG_CN)

            with transaction.atomic():
                article_serializer = CurationArticleSerializer(article_ins, data=article_data, partial=True)
                content_en_serial = CurationContentSerializer(content_en_ins, data=content_en, partial=True)
                content_cn_serial = CurationContentSerializer(content_cn_ins, data=content_cn, partial=True)

                if article_serializer.is_valid():
                    article_serializer.save()

                if content_en_serial.is_valid():
                    content_en_serial.save()

                if content_cn_serial.is_valid():
                    content_cn_serial.save()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            article_data = article_serializer.data
            content_en_data = content_en_serial.data
            content_cn_data = content_cn_serial.data

            article_data['content_en'] = content_en_data
            article_data['content_cn'] = content_cn_data

            self.result = {
                'article': article_data,
            }

        return self.result

    def delete_article(self, article_id):
        try:
            article_instance = CurationArticle.objects.get(id=article_id)
            article_instance.delete()
        except Exception as e:
            raise BusinessLogicError(str(e), None, None)
        else:
            self.result = True

        return self.result
