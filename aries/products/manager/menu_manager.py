import json

from django.core.paginator import Paginator
from django.db import transaction

from aries.common import code
from aries.common.models import ResultResponse
from aries.common.utils import message_util
from aries.products.models import Menu, Restaurant, MenuReviewStatics, Product
from aries.products.serializers import MenuListInfoSerializer, MenuReviewStaticsSerializer, \
    MenuListGuideSerializer, MenuListInfoAdminSerializer


class MenuManager:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

    def get_menu_data(self, target_db, menu_id, sales_time, cn_header):
        microwave = message_util.get_about_the_menu_microwave(cn_header)
        if sales_time == 2:
            menu_desc = message_util.get_about_the_menu_lunch(cn_header)
        else:
            menu_desc = message_util.get_about_the_menu_dinner(cn_header)

        menu_data = MenuListInfoSerializer(Menu.objects.using(target_db).get(id=menu_id)).data
        try:
            menu_data['description'] = json.loads(menu_data['description'])
            menu_data['description'][0] = menu_data['description'][0].format(microwave, menu_desc)
        except Exception as e:
            self.logger_info.info(str(e))
            self.logger_info.info(menu_id)
            self.logger_info.info('parsing failed')
            menu_data['description'] = ['']
        menu_data['prep_tips'] = json.loads(menu_data['prep_tips'])
        menu_data['ingredients'] = json.loads(menu_data['ingredients'])
        menu_data['nutrition'] = json.loads(menu_data['nutrition'])
        menu_data['notices'] = json.loads(menu_data['notices'])
        menu_data['subs_contents'] = json.loads(menu_data['subs_contents'])
        menu_data['media_contents'] = json.loads(menu_data['media_contents'])

        menu_list = json.loads(menu_data['image_detail'])
        menu_data['image_detail'] = menu_list[0]
        menu_data['image_detail_list'] = menu_list

        return menu_data

    def get_menu_list_data(self, target_db, menu_id):
        menu_data = MenuListGuideSerializer(Menu.objects.using(target_db).get(id=menu_id)).data
        del menu_data['restaurant']
        return menu_data

    def get_menu_list(self, page, limit, target_db='default'):
        try:
            menus = Menu.objects.using(target_db).filter(type__lt=10).order_by('-id')
            paginator = Paginator(menus, limit)

            menu_objects = paginator.page(page).object_list
            serializer = MenuListInfoAdminSerializer(menu_objects, many=True)

            menu_data = serializer.data
            menu_list = [self.parse_menu_data(True, menu) for menu in menu_data]

            for menu in menu_list:
                menu_instance = Menu.objects.using(target_db).get(id=menu['id'])
                product_qs = Product.objects.using(target_db).filter(menu=menu_instance)

                action_map = {'hub_1': {}, 'hub_2': {}}
                for product in product_qs:
                    if product.sales_time == 2:
                        action_map['hub_{}'.format(str(product.hub.code))]['lunch'] = product.id
                    if product.sales_time == 3:
                        action_map['hub_{}'.format(str(product.hub.code))]['dinner'] = product.id

                hub_1 = action_map['hub_1']
                hub_2 = action_map['hub_2']

                if len(hub_1) == 0:
                    action_map['hub_1'] = action_map['hub_2']

                if len(hub_2) == 0:
                    action_map['hub_2'] = action_map['hub_1']

                menu['hub_product_info'] = json.dumps(action_map)
            return menu_list
        except Exception as e:
            print(e)
            return []

    def create_menu(self, menu_en, menu_cn):
        try:
            en_count = Menu.objects.using('default').filter(type__lt=10).order_by('-id')[0].id
            cn_count = Menu.objects.using('aries_cn').filter(type__lt=10).order_by('-id')[0].id

            if en_count >= cn_count:
                index = en_count + 1
            else:
                index = cn_count + 1

            menu_en = self.parse_menu_data(False, menu_en)
            menu_cn = self.parse_menu_data(False, menu_cn)

            restaurant_en = Restaurant.objects.using('default').get(id=menu_en['restaurant'])
            restaurant_cn = Restaurant.objects.using('aries_cn').get(id=menu_cn['restaurant'])

            menu_en['restaurant'] = restaurant_en
            menu_cn['restaurant'] = restaurant_cn

            menu_en['id'] = index
            menu_cn['id'] = index
        except Exception as e:
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Error : ' + str(e))
            return result

        with transaction.atomic():
            try:
                menu = Menu.objects.using('default').create(**menu_en)
                Menu.objects.using('aries_cn').create(**menu_cn)
                MenuReviewStatics.objects.using('default').create(
                    menu=menu,
                    average_point=0.0,
                    review_count=0
                )
            except Exception as e:
                result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Error : ' + str(e))
                return result

        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        return result

    def get_menu_count(self):
        return Menu.objects.filter(type__lt=10).count()

    def get_menu_statics(self, menu_id):
        statics_count = MenuReviewStatics.objects.filter(menu=menu_id).count()
        if statics_count >= 1:
            statics = MenuReviewStatics.objects.get(menu=menu_id)
            statics_data = MenuReviewStaticsSerializer(statics).data
            result = statics_data
        else:
            result = {
                'average_point': 0.0,
                'review_count': 0,
                'review_count_postfix': ''
            }
        return result

    def parse_menu_data(self, parse_option, menu_data):
        if parse_option:
            menu_data['image_detail'] = json.loads(menu_data['image_detail'])
            menu_data['description'] = json.loads(menu_data['description'])
            menu_data['ingredients'] = json.loads(menu_data['ingredients'])
            menu_data['prep_tips'] = json.loads(menu_data['prep_tips'])
            menu_data['nutrition'] = json.loads(menu_data['nutrition'])
        else:
            menu_data['image_detail'] = json.dumps(menu_data['image_detail'])
            menu_data['description'] = json.dumps(menu_data['description'])
            menu_data['ingredients'] = json.dumps(menu_data['ingredients'])
            menu_data['prep_tips'] = json.dumps(menu_data['prep_tips'])
            menu_data['nutrition'] = json.dumps(menu_data['nutrition'])
        return menu_data
