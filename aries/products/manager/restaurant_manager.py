import json

from aries.products.service.restaurant_service import RestaurantService


class RestaurantManager:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

    def get_restaurant_data(self, restaurant_id, target_db='default'):
        restaurant_service = RestaurantService(self.logger_info, self.logger_error, target_db)
        restaurant_data = restaurant_service.read_restaurant_with_id(restaurant_id)
        return restaurant_data

    def get_brand(self, target_db, restaurant_id):
        restaurant_service = RestaurantService(self.logger_info, self.logger_error, target_db)
        brand_data = restaurant_service.read_brand_info_with_id(restaurant_id)

        brand_data['award_content'] = json.loads(brand_data['award_content'])
        brand_data['restaurant_content'] = json.loads(brand_data['restaurant_content'])
        if brand_data.get('chef_content') and len(brand_data.get('chef_content')) > 10:
            brand_data['chef_content'] = json.loads(brand_data['chef_content'])
        else:
            del brand_data['chef_content']

        if brand_data.get('interview_content') and len(brand_data.get('interview_content')) > 10:
            brand_data['interview_content'] = json.loads(brand_data['interview_content'])
        else:
            del brand_data['interview_content']

        return brand_data
