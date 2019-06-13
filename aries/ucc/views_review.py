import json

import logging
import requests
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.views import APIView

from aries.common import code
from aries.common import urlmapper
from aries.common.code_msg import get_msg
from aries.common.models import ResultResponse
from .models import CustomerReview, ReviewItem
from .serializers import CustomerReviewSerializer, ReviewItemSerializer

logger_info = logging.getLogger('ucc_info')
logger_error = logging.getLogger('ucc_error')


# For customer API
class CustomerReviewDetailNew(APIView):

    def get(self, request, product_id):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        has_open_id = False

        # Get page and limit information
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 5))

        open_id = request.META.get('HTTP_OPEN_ID', None)
        if open_id is not None:
            has_open_id = True

        try:
            url = urlmapper.get_url('PRODUCT') + '/' + str(product_id)
            response = requests.get(url)
            response_json = response.json()

            product = response_json['product']
            menu = product['menu']

            # Menu type check
            menu_type = product['type']
            menu_id = menu['id']

            if menu_type > 10:
                result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Product index invalid')
                return Response(result.get_response(), result.get_code())

            review_lists = list()

            review_list = CustomerReview.objects.filter(menu=menu_id, visible=True)
            review_total_count = review_list.count()
            paginator = Paginator(review_list, limit)

            review_objects = paginator.page(page).object_list
            serializer = CustomerReviewSerializer(review_objects, many=True)
            review_objects_data = serializer.data

            for review in review_objects_data:
                date_str = review['created_date']
                review['created_date'] = date_str[:10]

                if has_open_id and open_id == review['open_id']:
                    review['editable'] = True
                else:
                    review['editable'] = False

                del review['menu']
                del review['open_id']
                del review['visible']

                review_lists.append(review)

            result.set('total_count', review_total_count)
            result.set('page_size', limit)
            result.set('customer_reviews', review_lists)

        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_500_INTERNAL_SERVER_ERROR, 'Paging error')
            return Response(result.get_response(), code.ARIES_500_INTERNAL_SERVER_ERROR)

        return Response(result.get_response(), result.get_code())


class CustomerReviews(APIView):

    def get(self, request):
        result = ResultResponse(code.ARIES_200_SUCCESS, 'Success')

        cn_header = False

        if request.META.get('HTTP_ACCEPT_LANGUAGE'):
            accept_lang = request.META['HTTP_ACCEPT_LANGUAGE']
            if 'zh' in accept_lang:
                cn_header = True

        # Get request params
        try:
            open_id = request.GET.get('open_id')
            order_id = request.GET.get('order_id')
            product_id = int(request.GET.get('product_id'))
            menu_id = int(request.GET.get('menu_id'))
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Get customer object
        try:
            review_count = CustomerReview.objects.filter(open_id=open_id, menu=menu_id, order_id=order_id).count()
            review_json = {'product_id': product_id}

            if review_count >= 1:
                review = CustomerReview.objects.get(open_id=open_id, menu=menu_id, order_id=order_id)
                review_json['id'] = review.id
                review_json['has_reviewed'] = review.has_reviewed
                review_json['menu_rate'] = review.menu_rate
                review_json['special_feedback'] = review.special_feedback
                review_json['feedback_type'] = review.feedback_type
                review_json['comment'] = review.comment

                if open_id == review.open_id:
                    review_json['editable'] = True
                else:
                    review_json['editable'] = False
            else:
                review_json['id'] = -1
                review_json['has_reviewed'] = False
                review_json['menu_rate'] = 0
                review_json['special_feedback'] = False
                review_json['feedback_type'] = -1
                review_json['comment'] = ''
                review_json['editable'] = False

            result.set('review_detail', review_json)
        except Exception as e:
            logger_info.info(str(e))
            result.set('review_detail', json.loads('[]'))

        # Get Review item
        try:
            review_item_qs = ReviewItem.objects.filter(status=0)
            item_list = list()

            for review in review_item_qs:
                item_serializer = ReviewItemSerializer(review)
                item = item_serializer.data

                if cn_header:
                    item['name'] = item['name_cn']

                del item['name_cn']
                item_list.append(item)

            result.set('review_items', item_list)
        except Exception as e:
            logger_info.info(str(e))
            result.set('review_items', json.loads('[]'))

        return Response(result.get_response(), result.get_code())

    def post(self, request):
        request_data = request.data
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')
        logger_info.info(request_data)

        # Get access token
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]
        except Exception as e:
            logger_error.error(str(e))
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, 'Token or user not found')
            return Response(result.get_response(), result.get_code())

        # Request data parsing
        try:
            product_id = request_data['product_id']
            order_id = request_data['order_id']

            headers = {'open-id': open_id, 'AUTHORIZATION': 'bearer ' + access_token}
            response = requests.get(urlmapper.get_url('PRODUCT') + '/' + str(product_id), headers=headers)
            response_json = response.json()

            product = response_json['product']
            menu = product['menu']
            menu_id = menu['id']

            if request_data['menu_rate'] == 0:
                request_data['menu_rate'] = 5

            request_data['open_id'] = open_id
            request_data['product_id'] = product_id
            request_data['menu'] = menu_id
            request_data['has_reviewed'] = True

            # Check selective review object
            comment = request_data['comment']

            if len(comment) <= 1:
                request_data['visible'] = False
            else:
                request_data['visible'] = True

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        # Check if review exists
        try:
            review_count = CustomerReview.objects.filter(
                open_id=open_id, product_id=product_id, order_id=order_id
            ).count()

            # Not exists review
            if review_count <= 0:
                serializer = CustomerReviewSerializer(data=request_data)

                if serializer.is_valid():
                    serializer.save()
                    review_data = serializer.data

                    if open_id == review_data['open_id']:
                        review_data['editable'] = True
                    else:
                        review_data['editable'] = False

                    del review_data['created_date']
                    del review_data['menu']
                    del review_data['open_id']

                    # If review article saved, send Review Detail
                    result.set('review_detail', review_data)

                    # Statics information apply
                    payload = {'menu_id': menu_id, 'menu_rate': request_data['menu_rate'],
                               'has_reviewed': False, 'menu_prev_rate': 0.0}
                    statics_result = requests.post(urlmapper.get_url('MENU_STATICS'), json=payload)
                    logger_info.info(statics_result.text)
                else:
                    logger_info.info(serializer.errors)
                    result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
                    return Response(result.get_response(), result.get_code())
            else:
                review = CustomerReview.objects.get(open_id=open_id, product_id=product_id, order_id=order_id)
                prev_rate = review.menu_rate

                serializer = CustomerReviewSerializer(review, data=request_data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    review_data = serializer.data

                    if open_id == review_data['open_id']:
                        review_data['editable'] = True
                    else:
                        review_data['editable'] = False

                    del review_data['created_date']
                    del review_data['menu']
                    del review_data['open_id']
                    result.set('review_detail', review_data)

                    # Statics information apply
                    payload = {'menu_id': menu_id, 'menu_rate': request_data['menu_rate'],
                               'has_reviewed': True, 'menu_prev_rate': prev_rate}
                    statics_result = requests.post(urlmapper.get_url('MENU_STATICS'), json=payload)
                    logger_info.info(statics_result.text)
                else:
                    logger_info.info(serializer.errors)
                    result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
                    return Response(result.get_response(), result.get_code())

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())

    def put(self, request):
        request_data = request.data
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        logger_info.info(request_data)
        # AUthorization check
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]

            url = urlmapper.get_url('TOKEN_VALIDATE')
            headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise Exception
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, get_msg(code.ARIES_401_UNAUTHORIZED))
            return Response(result.get_response(), result.get_code())

        # Request data parsing
        try:
            # Check selective review object
            product_id = request_data['product_id']
            comment = request_data['comment']
            if len(comment) <= 0:
                request_data['visible'] = False
            else:
                request_data['visible'] = True

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        review = CustomerReview.objects.get(open_id=open_id, product_id=product_id)
        serializer = CustomerReviewSerializer(review, data=request_data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Statics information apply
            payload = {'menu_id': review.menu, 'prev_rate': review.menu_rate,
                       'menu_rate': request_data['menu_rate']}
            statics_result = requests.put(urlmapper.get_url('MENU_STATICS'), json=payload)
            logger_info.info(statics_result.text)
        else:
            logger_info.info(serializer.errors)
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())

        return Response(result.get_response(), result.get_code())

    def delete(self, request):
        request_data = request.data
        result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

        logger_info.info(request_data)

        # AUthorization check
        try:
            open_id = request.META['HTTP_OPEN_ID']
            access_token = str(request.META['HTTP_AUTHORIZATION']).split(' ')[1]

            url = urlmapper.get_url('TOKEN_VALIDATE')
            headers = {'open-id': open_id, 'authorization': 'bearer ' + access_token}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise Exception
        except Exception as e:
            print(e)
            result = ResultResponse(code.ARIES_401_UNAUTHORIZED, get_msg(code.ARIES_401_UNAUTHORIZED))
            return Response(result.get_response(), result.get_code())

        # Request data parsing
        try:
            product_id = request_data['product_id']
            order_id = request_data['order_id']

            review = CustomerReview.objects.get(open_id=open_id, product_id=product_id, order_id=order_id)

            # Statics information apply
            payload = {'menu_id': review.menu, 'prev_rate': review.menu_rate}
            statics_result = requests.delete(urlmapper.get_url('MENU_STATICS'), json=payload)
            logger_info.info(statics_result.text)

            review.delete()
            return Response(result.get_response(), result.get_code())

        except Exception as e:
            logger_info.info(str(e))
            result = ResultResponse(code.ARIES_400_BAD_REQUEST, 'Request data invalid')
            return Response(result.get_response(), result.get_code())
