import json

import requests

from aries.common import urlmapper
from aries.common.http_utils import api_request_util
from aries.products.models import ExpertReview, MenuReviewStatics
from aries.products.serializers import ExpertReviewSerializer


class ReviewManager:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.review_items = []

    def get_expert_review(self, target_db, menu_id):
        expert_review_list = ExpertReview.objects.using(target_db).filter(menu=int(menu_id))

        if expert_review_list.count() >= 1:
            expert_serializer = ExpertReviewSerializer(expert_review_list, many=True)
            expert_data = expert_serializer.data
            expert_list = list()

            for expert in expert_data:
                date_str = expert['created_date']
                expert['created_date'] = date_str[:10]
                expert['expert_comment'] = json.loads(expert['expert_comment'])
                expert_list.append(expert)

            return expert_list
        else:
            return []

    def get_product_review(self, accept_lang, product_id):
        page = 1
        limit = 5

        headers = {'accept-language': accept_lang}
        response = requests.get(urlmapper.get_review_url(
            product_id, page, limit
        ), headers=headers)

        if response.status_code == 200:
            review_json = response.json()
            result = (review_json['total_count'], review_json['page_size'], review_json['customer_reviews'])
        else:
            result = (0, 0, [])
        return result

    def get_personal_review(self, accept_lang, open_id, order_id, product):
        product_id = product['id']
        menu_id = product['menu']['id']
        headers = {'accept-language': accept_lang}
        payload = {'open_id': open_id, 'menu_id': menu_id, 'product_id': product_id, 'order_id': order_id}
        response = api_request_util.get_review_item(headers, payload)
        self.review_items = response['review_items']
        result = {'product': product, 'review_detail': response['review_detail']}
        return result

    def create_review(self, menu_id, menu_rate, menu_prev_rate, has_reviewed):
        try:
            menu_statics = MenuReviewStatics.objects.get(menu=menu_id)

            original_rate = menu_statics.review_count * menu_statics.average_point

            if menu_statics.review_count == 0:
                review_count = 1
            else:
                review_count = menu_statics.review_count

            if has_reviewed:
                original_rate -= menu_prev_rate
                original_rate += menu_rate
                new_rate = round(original_rate / review_count, 1)
            else:
                original_rate += menu_rate
                new_rate = round(original_rate / (review_count + 1), 1)
                menu_statics.review_count += 1

            menu_statics.average_point = new_rate
            menu_statics.save()
            return True
        except Exception as e:
            self.logger_error.error(str(e))
            return False

    def update_review(self, menu_id, menu_rate, prev_rate):
        try:
            menu_statics = MenuReviewStatics.objects.get(menu=menu_id)

            # Calculate rate
            original_rate = menu_statics.review_count * menu_statics.average_point
            original_rate -= prev_rate
            original_rate += menu_rate
            new_rate = round((original_rate/menu_statics.review_count), 1)

            # Save data
            menu_statics.average_point = new_rate
            menu_statics.save()
            return True
        except Exception as e:
            self.logger_info.info(str(e))
            return False
