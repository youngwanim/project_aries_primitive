import json

from django.db import transaction

from aries.common.exceptions.exceptions import BusinessLogicError
from aries.ucc.models import CurationPage, CurationPageContent
from aries.ucc.serializers import CurationPageSerializer, CurationPageContentSerializer


class CurationService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def create_curation_page(self, page_data):
        try:
            page_instance = CurationPage.objects.create(**page_data)
            curation_page = CurationPageSerializer(page_instance).data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = curation_page

        return self.result

    def create_curation_page_with_list(self, page_data):
        try:
            page_list = []
            for page in page_data:
                curation_instance = CurationPage.objects.create(**page)
                page_list.append(CurationPageSerializer(curation_instance).data)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = json.loads(page_list)

        return self.result

    def read_curation_page(self, query_str, language_type=0):
        try:
            page_qs = CurationPage.objects.filter(**query_str)

            page_data_list = []
            for page_instance in page_qs:
                page_data = CurationPageSerializer(CurationPage.objects.get(id=page_instance.id)).data
                page_content_instance = CurationPageContent.objects.get(
                    curation_page=page_instance, language_type=language_type
                )
                page_content_data = CurationPageContentSerializer(page_content_instance).data
                page_data['title'] = page_content_data.get('title', '')
                page_data['sub_title'] = page_content_data.get('sub_title', '')
                page_data['has_title_img'] = page_content_data.get('has_title_img', False)
                page_data['title_img'] = page_content_data.get('title_img', '')
                page_data['has_sub_title_img'] = page_content_data.get('has_sub_title_img', False)
                page_data['sub_title_img'] = page_content_data.get('sub_title_img', '')

                page_data_list.append(page_data)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = page_data_list

        return self.result

    def read_curation_page_data(self, curation_page_id):
        try:
            curation_page_ins = CurationPage.objects.get(id=curation_page_id)
            curation_page_data = CurationPageSerializer(curation_page_ins).data
        except Exception as e:
            self.logger_error.error(str(e))
            curation_page_data = None

        return curation_page_data

    def read_curation_page_content(self, curation_page_id, lang_type):
        try:
            page_content_ins = CurationPageContent.objects.get(curation_page=curation_page_id, language_type=lang_type)
            page_content_data = CurationPageContentSerializer(page_content_ins).data
        except Exception as e:
            self.logger_error.error(str(e))
            page_content_data = None

        return page_content_data

    def update_curation_page(self, page_id, page_data):
        try:
            page_instance = CurationPage.objects.get(id=page_id)
            serializer = CurationPageSerializer()
            serializer.update(page_instance, page_data)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = serializer.data

        return self.result

    def delete_curation_page(self, page_id):
        try:
            page_instance = CurationPage.objects.get(id=page_id)
            page_instance.delete()
        except Exception as e:
            raise BusinessLogicError(str(e), None, None)
        else:
            self.result = True

        return self.result

    # Curation page Admin functions
    def admin_read_curation_page(self, query_str):
        try:
            page_qs = CurationPage.objects.filter(**query_str).order_by('list_index')
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = page_qs

        return self.result

    def admin_read_all_curation_page(self):
        try:
            page_qs = CurationPage.objects.all().order_by('list_index')
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = page_qs

        return self.result

    def admin_read_curation_page_content(self, page_id, language_type):
        try:
            page_instance = CurationPageContent.objects.get(curation_page=page_id, language_type=language_type)
            page_content_data = CurationPageContentSerializer(page_instance).data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = page_content_data

        return self.result

    def admin_create_curation_page(self, page, content_en, content_cn):
        action_type_see_all = 14

        try:
            with transaction.atomic():
                page['status'] = 0
                page['articles'] = json.dumps(page['articles'])

                page_instance = CurationPage.objects.create(**page)

                content_en['curation_page'] = page_instance
                content_cn['curation_page'] = page_instance

                content_en_ins = CurationPageContent.objects.create(**content_en)
                content_cn_ins = CurationPageContent.objects.create(**content_cn)

                # Action type see all -> binding object's id
                if int(page_instance.action_type) == action_type_see_all:
                    page_instance.action_target = str(page_instance.id)
                    page_instance.save()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            page_data = CurationPageSerializer(page_instance).data
            content_en_data = CurationPageContentSerializer(content_en_ins).data
            content_cn_data = CurationPageContentSerializer(content_cn_ins).data

            page_data['content_en'] = content_en_data
            page_data['content_cn'] = content_cn_data

            self.result = page_data

        return self.result

    def admin_update_curation_page(self, page, content_en, content_cn):
        try:
            with transaction.atomic():
                page_instance = CurationPage.objects.get(id=page['id'])

                content_en_ins = CurationPageContent.objects.get(curation_page=page_instance, language_type=0)
                content_cn_ins = CurationPageContent.objects.get(curation_page=page_instance, language_type=1)

                page_serializer = CurationPageSerializer(page_instance, data=page, partial=True)
                en_serializer = CurationPageContentSerializer(content_en_ins, data=content_en, partial=True)
                cn_serializer = CurationPageContentSerializer(content_cn_ins, data=content_cn, partial=True)

                if page_serializer.is_valid():
                    page_serializer.save()
                else:
                    print(page_serializer.errors)

                if en_serializer.is_valid():
                    en_serializer.save()
                else:
                    print(page_serializer.errors)

                if cn_serializer.is_valid():
                    cn_serializer.save()
                else:
                    print(page_serializer.errors)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            page_data = page_serializer.data
            page_data['content_en'] = en_serializer.data
            page_data['content_cn'] = cn_serializer.data
            print(page_data)
            self.result = page_data

        return self.result

    def admin_update_curation_page_list(self, page_list):
        try:
            for page in page_list:
                page_instance = CurationPage.objects.get(id=page['id'])
                page_instance.status = page['status']
                page_instance.list_index = page['list_index']
                page_instance.save()
        except Exception as e:
            self.logger_error.error(str(e))
            self.result = False

        return self.result

    def admin_delete_curation_page(self, page_id):
        self.result = True
        try:
            page_instance = CurationPage.objects.get(id=page_id)
            page_instance.delete()
        except Exception as e:
            self.logger_error.error(str(e))
            self.result = False

        return self.result
