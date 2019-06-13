from aries.common.exceptions.exceptions import BusinessLogicError

from aries.products.models import Restaurant, RestaurantBrandInfo
from aries.products.serializers import RestaurantInfoSerializer, RestaurantBrandInfoSerializer


class RestaurantService:

    def __init__(self, logger_info, logger_error, target_db):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None
        self.target_db = target_db

    def read_restaurant_with_id(self, restaurant_id):
        try:
            restaurant_data = RestaurantInfoSerializer(Restaurant.objects.get(id=restaurant_id)).data
        except Exception as e:
            msg = '[RestaurantService][read_restaurant_with_id][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return restaurant_data

    def read_brand_info_with_id(self, restaurant_id):
        try:
            brand = RestaurantBrandInfo.objects.using(self.target_db).get(restaurant=restaurant_id)
            brand_data = RestaurantBrandInfoSerializer(brand).data
        except Exception as e:
            msg = '[RestaurantService][read_brand_info_with_id][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return brand_data
