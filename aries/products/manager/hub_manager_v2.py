import json

from aries.products.common.hub_func import get_hub_status_msg
from aries.products.common.product_func import get_discount_info_map, add_discount_information
from aries.products.service.hub_service import HubService
from aries.products.service.menu_service import MenuService
from aries.products.service.product_service import ProductService
from aries.products.service.time_bomb_service import TimeBombService


def get_json(has_product, product_id, menu_id, quantity, has_changed, prev_product_id):
    return {
        'has_product': has_product,
        'product_id': product_id,
        'menu_id': menu_id,
        'quantity': quantity,
        'has_changed': has_changed,
        'prev_product_id': prev_product_id
    }


class HubManagerV2:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

    def get_product_list(self, product_list, hub_id):
        """
        product list : [{'product_id': 24, 'quantity':3}]
        :return:
            new_product_list
        """
        another_hub_list = []
        target_hub_list = []

        product_service = ProductService(self.logger_info, self.logger_error)

        for product in product_list:
            product_id = product['product_id']
            quantity = product['quantity']
            product_qs = product_service.read_product_list_with_query({'id': product_id})

            if product_qs.count() >= 1:
                product_instance = product_service.read_product_with_id(product_id)
                product_hub_id = product_instance.hub.id
                menu_instance = product_instance.menu
                menu_id = menu_instance.id

                if product_hub_id != hub_id:
                    product_count = product_service.read_product_count_with_query({
                        'hub_id': hub_id, 'menu': menu_instance, 'status__lt': 10
                    })

                    if product_count >= 1:
                        product_data = product_service.read_product_data_with_query({
                            'hub_id': hub_id, 'menu': menu_instance, 'status__lt': 10
                        })
                        new_product_id = product_data['id']
                        new_menu_id = product_data['menu']

                        another_hub_list.append(get_json(True, new_product_id, new_menu_id, quantity, True, product_id))
                    else:
                        target_hub_list.append(get_json(False, product_id, menu_id, quantity, False, 0))
                else:
                    target_hub_list.append(get_json(True, product_id, menu_id, quantity, False, 0))

        for product in another_hub_list:
            product_id = product['product_id']
            find_result = False

            for target_product in target_hub_list:
                if product_id == target_product['product_id']:
                    target_product['quantity'] += product['quantity']
                    target_product['has_changed'] = True
                    find_result = True

            if not find_result:
                target_hub_list.append(product)

        return target_hub_list

    def get_stock_list(self, hub_id, product_list, target_db, os_type):
        """
        :return:
            tuple(stock_list)
        """
        cn_header = False if target_db == 'default' else True
        stock_list = []

        # Product service
        product_service = ProductService(self.logger_info, self.logger_error)
        menu_service = MenuService(self.logger_info, self.logger_error, target_db)

        # Time bomb service
        time_bomb_service = TimeBombService(self.logger_info, self.logger_error)
        time_bomb_id = time_bomb_service.get_current_time_bomb_id(hub_id, os_type)
        discount_info = {}

        if time_bomb_id is not None:
            discount_list = product_service.read_product_discount_info_with_id(time_bomb_id)
            discount_info.update(get_discount_info_map(discount_list, cn_header))

        for product in product_list:
            if product['has_product']:
                product_instance = product_service.read_product_with_id(product['product_id'])
                hub_stock = menu_service.read_hub_stock_instance(product_instance.hub, product_instance.menu)

                current_stock = hub_stock.stock
                product['stock'] = current_stock
                product['price'] = product_instance.price
                # Stock
                product['has_changed'] = True

                # To delete next update
                product['sales_time_limit'] = False

                # Time bomb check and add information
                if product['product_id'] in discount_info:
                    add_discount_information(product, discount_info[product['product_id']])

                del product['has_product']

                stock_list.append(product)

        stock_result = stock_list

        return stock_result

    def get_hub_list(self, status, cn_header, target_db):
        """
        :param status: hub list json data
        :param cn_header: Language header
        :param target_db: Target db string
        :return:
            hub object list
        """
        hub_service = HubService(self.logger_info, self.logger_error)
        hub_data = hub_service.read_hub_list_with_status(status, target_db)

        hub_list = []

        for hub in hub_data:
            geo_information = json.loads(hub['geometry_information'])
            geo_info_list = list()

            features = geo_information['features']

            for feature in features:
                if feature['properties']['feature_type'] == 1:
                    geo_info = {
                        'geometry': feature['geometry'],
                        'properties': feature['properties']
                    }
                    geo_info_list.append(geo_info)

            hub_object = {
                'hub_id': hub['code'],
                'address': hub['address'],
                'location': hub['name'],
                'city_code': hub['location_type'],
                'geo_information': geo_info_list,
                'hub_name': hub['name'],
                'status': hub['status'],
                'hub_status_msg': get_hub_status_msg(hub['status'], cn_header),
                'longitude': hub['longitude'],
                'latitude': hub['latitude']
            }

            hub_list.append(hub_object)

        return hub_list

    def get_hub_detail(self, hub_id, cn_header):
        """
        :param hub_id: hub id
        :param cn_header: Language header
        :return: hub information object
        """
        hub_service = HubService(self.logger_info, self.logger_error)
        hub = hub_service.read_hub_instance_with_id(hub_id)

        geo_information = json.loads(hub.geometry_information)
        geo_info_list = list()

        loc_name = geo_information['type']
        features = geo_information['features']

        for feature in features:
            if feature['properties']['feature_type'] == 1:
                geo_info = {
                    'geometry': feature['geometry'],
                    'properties': feature['properties']
                }
                geo_info_list.append(geo_info)

        hub_information = {
            'hub_id': hub_id,
            'location': loc_name,
            'address': hub.address,
            'city_code': hub.location_type,
            'geo_information': geo_info_list,
            'hub_name': hub.name,
            'status': hub.status,
            'hub_status_msg': get_hub_status_msg(hub.status, cn_header),
            'longitude': hub.longitude,
            'latitude': hub.latitude
        }

        return hub_information

    def get_hub_delivery(self, cn_header, target_db='default'):
        """
        Get hub delivery list. Used in on site pick up.
        :param cn_header: Language header
        :param target_db: Target db
        :return: Hub information list
        """
        hub_service = HubService(self.logger_info, self.logger_error)
        hub_list = hub_service.read_hub_list(target_db)

        result_list = []

        for hub_info in hub_list:
            geo_information = json.loads(hub_info['geometry_information'])
            geo_info_list = list()

            loc_name = geo_information['type']
            features = geo_information['features']

            for feature in features:
                if feature['properties']['feature_type'] == 1:
                    geo_info = {
                        'geometry': feature['geometry'],
                        'properties': feature['properties']
                    }
                    geo_info_list.append(geo_info)

            hub = {
                'hub_id': hub_info['code'],
                'location': loc_name,
                'address': hub_info['address'],
                'city_code': hub_info['location_type'],
                'geo_information': geo_info_list,
                'hub_name': hub_info['name'],
                'status': hub_info['status'],
                'hub_status_msg': get_hub_status_msg(hub_info['status'], cn_header),
                'longitude': hub_info['longitude'],
                'latitude': hub_info['latitude']
            }

            result_list.append(hub)

        return result_list

    def get_hub_instance(self, hub_id):
        """
        Get hub delivery list. Used in on site pick up.
        :param hub_id: Target hub id
        :return: Target hub instance
        """
        hub_service = HubService(self.logger_info, self.logger_error)

        return hub_service.read_hub_instance_with_id(hub_id)
