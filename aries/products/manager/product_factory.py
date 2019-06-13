from django.db.models import Q

from aries.products.models import Product, RestaurantBrandInfo, Menu, MenuPairingInformation
from aries.products.serializers import ProductListInfoSerializer, MenuSerializer, MenuPairingSerializer

PRODUCT_LIST = 0
PRODUCT_DETAIL = 1
PRODUCT_GENERAL = 2
PRODUCT_SINGLE = 3
BRAND_LIST = 4
PAIRING_LIST = 5

MENU_TYPE_THRESH_HOLDER = 10
MENU_TYPE_SET = 0
MENU_TYPE_SUBSCRIPTION = 8
MENU_TYPE_LIMIT = 10

ALL_DAY_TIME = 0


class ProductsInstance(object):

    def factory(products_type, date_info):
        if products_type == PRODUCT_LIST:
            return ProductsList(date_info)
        elif products_type == BRAND_LIST:
            return ProductsBrand(date_info)
        elif products_type == PRODUCT_DETAIL:
            return ProductsDetail(date_info)
        elif products_type == PRODUCT_GENERAL:
            return ProductsGeneral(date_info)
        elif products_type == PRODUCT_SINGLE:
            return ProductSingle(date_info)
        else:
            return ProductsList(date_info)

    factory = staticmethod(factory)


class BaseProduct(ProductsInstance):

    def __init__(self, date_info):
        self.date_info = date_info
        self.hub_id = date_info[0]
        self.time_type = date_info[1]
        self.phase_next_day = date_info[2]
        self.current_date = date_info[3]
        self.lunch_time = date_info[4]

    def get_product_queryset(self, kvp):
        return Product.objects.using('default').filter(**kvp)

    def get_detail_recommend_queryset(self, selected_time, menu_id):
        product_queryset = Product.objects.using('default').filter(
            hub=self.hub_id,
            type__lt=MENU_TYPE_SUBSCRIPTION,
            status=1
        ).exclude(menu=menu_id).order_by('?')[:2]
        return product_queryset

    def get_general_recommend_queryset(self, selected_time):
        product_queryset = Product.objects.using('default').filter(
            hub=self.hub_id,
            type__lt=MENU_TYPE_SUBSCRIPTION,
            status=1
        ).order_by('?')[:2]
        return product_queryset


class ProductsList(BaseProduct):

    def get_products_data(self):
        product_queryset = Product.objects.using('default').filter(
            Q(hub=self.hub_id,
              type__lt=MENU_TYPE_LIMIT,
              sales_time=self.time_type,
              start_date__lte=self.current_date,
              end_date__gte=self.current_date) |
            Q(hub=self.hub_id,
              type__lt=MENU_TYPE_LIMIT,
              sales_time=ALL_DAY_TIME,
              start_date__lte=self.current_date,
              end_date__gte=self.current_date)
        ).order_by('list_index')
        products_data = ProductListInfoSerializer(product_queryset, many=True).data
        return products_data


class ProductsBrand(BaseProduct):

    def get_products_data(self, brand_info, selected_time):
        print(selected_time)
        restaurant_brand = RestaurantBrandInfo.objects.get(id=brand_info)
        restaurant = restaurant_brand.restaurant

        menus = Menu.objects.filter(restaurant=restaurant)
        menu_data = MenuSerializer(menus, many=True).data

        product_list = []
        for menu in menu_data:
            result = self.get_product_from_menu(menu['id'])
            if result[0]:
                product_list.append(result[1])

        product_queryset = Product.objects.using('default').filter(
            id__in=product_list,
            status=1
        ).order_by('list_index')
        products_data = ProductListInfoSerializer(product_queryset, many=True).data
        return products_data

    def get_product_from_menu(self, menu_id):
        products = Product.objects.filter(hub=self.hub_id, menu=menu_id, status__lte=1, type__lte=7)

        if products.count() == 1:
            product = Product.objects.get(hub=self.hub_id, menu=menu_id, status__lte=1, type__lte=7)
        else:
            product = None

        if product is None:
            result = (False, None)
        else:
            result = (True, product.id)
        return result


class ProductsDetail(BaseProduct):

    def get_products_data(self, selected_time, product):
        menu_id = product['menu']['id']
        hub_id = product['hub']

        pairing_info = MenuPairingInformation.objects.filter(menu=menu_id)
        pairing_count = pairing_info.count()

        if pairing_count >= 1:
            pairing_data = MenuPairingSerializer(pairing_info, many=True)
            pairing_menu = [pairing_info['pairing_menu'] for pairing_info in pairing_data.data]
            product_queryset = self.get_product_queryset({
                'hub': hub_id,
                'menu__in': pairing_menu,
                'sales_time': selected_time,
                'type__lt': MENU_TYPE_LIMIT,
                'status': 1
            })
            if product_queryset.count() == 0:
                product_queryset = self.get_detail_recommend_queryset(selected_time, menu_id)
        else:
            product_queryset = self.get_detail_recommend_queryset(selected_time, menu_id)

        products_data = ProductListInfoSerializer(product_queryset, many=True).data
        return products_data


class ProductsGeneral(BaseProduct):

    def get_products_data(self, selected_time):
        product_queryset = self.get_general_recommend_queryset(selected_time)
        products_data = ProductListInfoSerializer(product_queryset, many=True).data

        menu_id_list = [product['menu'] for product in products_data]
        menus = Menu.objects.filter(id__in=menu_id_list)
        menu_data = MenuSerializer(menus, many=True).data

        product_list = [self.get_product_from_menu(menu['id'], selected_time) for menu in menu_data]
        product_queryset = Product.objects.using('default').filter(
            hub=self.hub_id,
            id__in=product_list
        ).order_by('?')

        products_data = ProductListInfoSerializer(product_queryset[:2], many=True).data

        return products_data

    def get_product_from_menu(self, menu_id, selected_time):
        products = Product.objects.filter(hub=self.hub_id, menu=menu_id)

        if products.count() >= 2:
            product = Product.objects.get(hub=self.hub_id, menu=menu_id, sales_time=selected_time)
        else:
            product = Product.objects.get(hub=self.hub_id, menu=menu_id)

        return product.id


class ProductSingle(BaseProduct):

    def get_products_data(self, product_id):
        product = Product.objects.get(id=product_id)
        product_data = ProductListInfoSerializer(product).data
        return product_data
