import json

from django.db import transaction
from django.test import TestCase
from django.test import TransactionTestCase

from aries.common import product_util
from aries.common.http_utils import header_parser
from aries.products.models import Menu, Restaurant


menu_dummy_data = '{"name": "Broccoli covered by cream cheese", "cooking_materials": "", "type": 1, "image_main": ' \
                  '"is_2_main.png", "image_detail": ["is_3_dessert_detail.png"], "image_sub": "is_2_sub.png", "image_' \
                  'thumbnail": "is_2_thumbnail.png", "description": ["The restaurant buchun is based on the city in ' \
                  'hanging.", "They has changed the culture of food with local citizen.", "All effort to make better' \
                  ' dining is very fascinated in Korea and In Situ2"], "image_package": "phase2_pic_menu_' \
                  'package-26eff4.png", "prep_tips": {"type": 0, "title": "MICROWAVE OVEN(700W)", "sub_title": ' \
                  '"Tear corner of the plastic package before heating.", "description": ["Grain Porridge : 1min ' \
                  '30sec", "Grilled Pork Loin : 1min", "Stir-Fried Vegetable and Pork Belly : 1min 30sec", "Sweet and' \
                  ' Sour Mint Sauce : 30sec", "Mint : No Microwave"]}, "prep_plating_thumbnail": "", "prep_plating_' \
                  'url": "https://youtu.be/oyTvZn1rJzE", "ingredients": [{"name": "Poato", "quantity": "200g"}, ' \
                  '{"name": "Pork meat", "quantity": "250g"}, {"name": "white source", "quantity": "10g"}],' \
                  '"nutrition": [{"name": "Calories", "quantity": "670Kcal"}, {"name": "Total Fat",' \
                  '"quantity": "43g"},{"name": "Saturated Fat", "quantity": "19g"}, {"name": "Trans Fat",' \
                  '"quantity": "0g"}, {"name": "Polyunsaturated Fat", "quantity": "6g"}, {"name": ' \
                  '"Monounsaturated Fat", "quantity": "9g"}, {"name": "Colesterol", "quantity": "210mg"},' \
                  ' {"name": "Sodium", "quantity": "720mg"}, {"name": "Total Cabs", "quantity": "22g"}, {"name":' \
                  ' "Dietary Fiber", "quantity": "10g"}, {"name": "Sugar", "quantity": "12g"}, {"name": "Protein",' \
                  ' "quantity": "19g"}], "restaurant": 1}'


class ProductManagerTest(TestCase):

    hub_id = 1
    time_type = 3

    def setUp(self):
        self.dummy_meta = {'HTTP_ACCEPT_LANGUAGE': 'en'}

    def test_language_info(self):
        language_info = header_parser.parse_language(self.dummy_meta)
        self.assertEqual(language_info[0], False)
        self.assertEqual(language_info[1], 'default')

        self.dummy_meta = {'HTTP_ACCEPT_LANGUAGE': 'zh'}
        language_info = header_parser.parse_language(self.dummy_meta)
        self.assertEqual(language_info[0], True)
        self.assertEqual(language_info[1], 'aries_cn')

    def test_date_info(self):
        date_info = product_util.get_date_information(1, 'lunch')
        self.assertEqual(date_info[0], 1)
        self.assertEqual(date_info[1], 2)


class AdminManagerTest(TransactionTestCase):

    def setUp(self):
        Restaurant.objects.create(
            name='ViaStelle',
            email='Viastelle.com',
            account='admin',
            password='administrator',
            chef='ImChef',
            country='country',
            contract_complete=0
        )

    def test_get_menu(self):
        menu_en = json.loads(menu_dummy_data)
        menu_en['description'] = json.dumps(menu_en['description'])
        menu_en['prep_tips'] = json.dumps(menu_en['prep_tips'])
        menu_en['ingredients'] = json.dumps(menu_en['ingredients'])
        menu_en['nutrition'] = json.dumps(menu_en['nutrition'])

        restaurant = Restaurant.objects.get(id=menu_en['restaurant'])
        menu_en['restaurant'] = restaurant
        Menu.objects.using('default').create(**menu_en)
        menu_en_count = Menu.objects.using('default').all().count()
        self.assertEqual(menu_en_count, 1)

        with transaction.atomic():
            menu_en = json.loads(menu_dummy_data)
            menu_en['description'] = json.dumps(menu_en['description'])
            menu_en['prep_tips'] = json.dumps(menu_en['prep_tips'])
            menu_en['ingredients'] = json.dumps(menu_en['ingredients'])
            menu_en['nutrition'] = json.dumps(menu_en['nutrition'])
            menu_en['restaurant'] = restaurant

            Menu.objects.using('default').create(**menu_en)
            menu_en_count = Menu.objects.using('default').all().count()
            self.assertEqual(menu_en_count, 2)

            try:
                menu_en['id'] = 1
                Menu.objects.using('default').create(**menu_en)
            except Exception as e:
                str(e)

        menu_en_count = Menu.objects.using('default').all().count()
        self.assertEqual(menu_en_count, 1)

        menu = Menu.objects.all()[0]
        menu = Menu.objects.get(id=menu.id)
        menu.delete()

        menu_en_count = Menu.objects.using('default').all().count()
        self.assertEqual(menu_en_count, 0)
