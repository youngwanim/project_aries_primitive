import datetime

from aries.common.utils import display_util
from aries.ucc.common.curation_func import get_product_info_from_menu, get_product_info_for_curation, \
    get_time_bomb_info_from_menu, get_curation_article
from aries.ucc.service.article_service import ArticleService
from aries.ucc.service.curation_service import CurationService
from aries.ucc.service.dp_schedule_service import DisplayScheduleService


class CurationManager:

    L_TEXT = 0
    L_GENERAL_BANNER = 1
    L_SLIM_BANNER = 2
    L_READ_AND_WATCH = 3
    L_LARGE_THUMBNAIL = 4
    L_MEDIUM_CUBE = 5
    L_SMALL_CUBE = 6

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.article_service = ArticleService(self.logger_info, self.logger_error)
        self.curation_service = CurationService(self.logger_info, self.logger_error)
        self.display_service = DisplayScheduleService(self.logger_info, self.logger_error)

    def get_curation_list(self, cn_header=False, hub_id=1, os_type=0):
        lang_type = 1 if cn_header else 0

        current_date = datetime.date.today()
        query_str = {
            'status': 1,
            'start_date__lte': current_date,
            'end_date__gte': current_date
        }

        curation_list = self.curation_service.read_curation_page(query_str, lang_type)
        curation_dp_list = self.make_display_list(curation_list)

        for curation in curation_dp_list:
            article_list = []
            for article_number in curation['articles']:
                article_ins = self.article_service.read_article_with_id(article_number, lang_type)
                if article_ins is not None:
                    article_list.append(article_ins)

            curation_article_limit = curation['article_limit']
            if curation_article_limit != 0:
                article_list = article_list[:curation_article_limit]

            menu_display_list = self.make_product_information(article_list, hub_id, cn_header, os_type)
            curation['articles'] = self.make_display_list(menu_display_list)

        return curation_dp_list

    def add_time_bomb_information(self, curation_section, hub_id=1, accept_lang='zh', os_type=0):
        self.logger_info.info('[CurationManager][add_time_bomb_information]')
        banner_layout = 1
        time_bomb_action = 102

        time_bomb_info = get_time_bomb_info_from_menu(hub_id, accept_lang, os_type)

        if time_bomb_info is not None and time_bomb_info['status'] != 0:
            time_bomb_id = time_bomb_info['id']
            if time_bomb_info['status'] == 1 or time_bomb_info['status'] == 2:
                start_banner = time_bomb_info['start_banner_image']
            else:
                start_banner = time_bomb_info['end_banner_image']

            article_list = [get_curation_article(0, banner_layout, start_banner, time_bomb_action, time_bomb_id, '')]
            curation_section['articles'] = article_list + curation_section['articles']

    def make_display_list(self, dp_object_list):
        display_list = []
        for dp_object in dp_object_list:
            has_dp_schedule = dp_object['has_dp_schedule']
            dp_schedule_id = dp_object['dp_schedule_id']

            if has_dp_schedule:
                dp_instance = self.display_service.read_dp_schedule(dp_schedule_id)
                if display_util.display_check(dp_instance):
                    display_list.append(dp_object)
            else:
                display_list.append(dp_object)

        return display_list

    def make_product_information(self, dp_object_list, hub_id, cn_header, os_type):
        action_type_prod = 4

        menu_id_list = []
        for dp_object in dp_object_list:
            if dp_object['has_menu_data']:
                menu_id_list.append(dp_object['menu_id'])
        if len(menu_id_list) >= 1:
            product_result = get_product_info_from_menu(hub_id, menu_id_list, cn_header, os_type)
            product_list = [] if product_result is None else product_result['products']
            product_map = {}

            for product in product_list:
                product_map[product['menu']['id']] = product

            self.logger_info.info(len(product_map))

            for dp_object in dp_object_list:
                if dp_object['has_menu_data']:
                    menu_id = dp_object['menu_id']

                    if menu_id in product_map:
                        product = product_map[menu_id]
                        dp_object['product_data'] = get_product_info_for_curation(product)

                        # Action type 4 parsing
                        if dp_object['action_type'] == action_type_prod:
                            dp_object['action_target'] = str(dp_object['product_data']['id'])
                            dp_object['action_extra'] = str(dp_object['product_data']['type'])
                    else:
                        dp_object['product_data'] = get_product_info_for_curation(None)

        return dp_object_list

    def get_curation_detail(self, hub_id, cn_header, os_type, curation_page_id, page, limit):
        curation_page = self.curation_service.read_curation_page_data(curation_page_id)

        layout_type = curation_page['layout_type']
        lang_type = 1 if cn_header else 0

        page_content = self.curation_service.read_curation_page_content(curation_page['id'], lang_type)
        page_title = page_content['title']

        article_list = []
        product_list = []

        result_map = {
            'hub_id': hub_id, 'layout_type': layout_type, 'title': page_title,
            'products': product_list, 'articles': article_list, 'total_count': 0
        }

        if layout_type == self.L_READ_AND_WATCH:
            query_str = {'layout_type': layout_type}

            article_result = self.article_service.read_article_with_page(query_str, page, limit)
            result_map['total_count'] = article_result['total_count']

            for article in article_result['articles']:
                article_ins = self.article_service.read_article_with_id(article['id'], lang_type)
                article_list.append(article_ins)
        elif layout_type == self.L_MEDIUM_CUBE:
            menu_id_list = []
            for article_number in curation_page['articles']:
                article_data = self.article_service.read_article_with_id(article_number, lang_type)
                menu_id_list.append(article_data['menu_id'])

            product_result = get_product_info_from_menu(hub_id, menu_id_list, cn_header, os_type)

            if product_result is not None:
                products = product_result['products']
                result_map['total_count'] = len(products)
                result_map.update(**product_result)

        return result_map
