import abc

from aries.common.test_utils import test_data


class TestDataFactory(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def _create_data(self):
        pass


class LespalierRestaurantFactory(TestDataFactory):

    def _create_data(self):
        return test_data.restaurant


class ShanghaiHubFactory(TestDataFactory):

    def _create_data(self):
        return test_data.hub_1


class PudongHubFactory(TestDataFactory):

    def _create_data(self):
        return test_data.hub_2


class LespalierBrandFactory(TestDataFactory):

    def __init__(self, restaurant_id):
        self.restaurant_id = restaurant_id

    def _create_data(self):
        restaurant_brand = test_data.restaurant_brand
        restaurant_brand['restaurant'] = self.restaurant_id
        return restaurant_brand


class TenderLoinFactory(TestDataFactory):

    def __init__(self, restaurant_id):
        self.restaurant_id = restaurant_id

    def _create_data(self):
        menu = test_data.menu_main_tenderloin
        menu['restaurant'] = self.restaurant_id
        return menu


class WineFactory(TestDataFactory):

    def __init__(self, restaurant_id):
        self.restaurant_id = restaurant_id

    def _create_data(self):
        menu = test_data.menu_wine_casa_amada
        menu['restaurant'] = self.restaurant_id
        return menu


class ProductTenderLoinFactory(TestDataFactory):

    def __init__(self, hub_id, menu_id):
        self.hub_id = hub_id
        self.menu_id = menu_id

    def _create_data(self):
        product = test_data.product_tenderloin
        product['hub'] = self.hub_id
        product['menu'] = self.menu_id
        return product


class ProductCasaAmadaFactory(TestDataFactory):

    def __init__(self, hub_id, menu_id):
        self.hub_id = hub_id
        self.menu_id = menu_id

    def _create_data(self):
        product = test_data.product_casa_amada
        product['hub'] = self.hub_id
        product['menu'] = self.menu_id
        return product


class HubStockFactory(TestDataFactory):

    def __init__(self, hub, menu):
        self.hub = hub
        self.menu = menu

    def _create_data(self):
        hub_stock = test_data.hub_stock
        hub_stock['hub'] = self.hub
        hub_stock['menu'] = self.menu
        return test_data.hub_stock
