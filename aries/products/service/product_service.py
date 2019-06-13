from django.db.models import Q

from aries.common.exceptions.exceptions import BusinessLogicError
from aries.products.models import Product, TimeBombDiscountInfo
from aries.products.serializers import ProductSerializer, ProductAdminSerializer, TimeBombDiscountInfoSerializer


class ProductService:
    ALL_DAY_MENU = 0
    MENU_TYPE_LIMIT = 10

    def __init__(self, logger_info, logger_error, target_db='default'):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None
        self.target_db = target_db

    def read_product_list_v3(self, hub_id, current_date):
        try:
            products_qs = Product.objects.using('default').filter(
                Q(hub=hub_id,
                  type__lt=self.MENU_TYPE_LIMIT,
                  sales_time=self.ALL_DAY_MENU,
                  start_date__lte=current_date,
                  end_date__gte=current_date)
            ).order_by('list_index')
            products_data = ProductSerializer(products_qs, many=True).data
        except Exception as e:
            msg = '[ProductService][read_product_count_with_query][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return products_data

    def read_recommend_list(self, query_str):
        try:
            product_qs = Product.objects.filter(**query_str).order_by('?')[:2]
            products_data = ProductSerializer(product_qs, many=True).data
        except Exception as e:
            msg = '[ProductService][read_recommend_list][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return products_data

    def read_product_count_with_query(self, query_str):
        try:
            product_queryset = Product.objects.filter(**query_str)
            product_count = product_queryset.count()
        except Exception as e:
            msg = '[ProductService][read_product_count_with_query][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return product_count

    def read_product_with_id(self, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Exception as e:
            msg = '[ProductService][read_product_with_id][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return product

    def read_product_data_with_id(self, product_id):
        try:
            product = Product.objects.get(id=product_id)
            product_data = ProductSerializer(product).data
        except Exception as e:
            msg = '[ProductService][read_product_data_with_id][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return product_data

    def read_product_data_with_query(self, query_str):
        try:
            product = Product.objects.get(**query_str)
            product_data = ProductSerializer(product).data
        except Exception as e:
            msg = '[ProductService][read_product_data_with_query][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return product_data

    def read_product_with_query(self, query_str):
        try:
            product = Product.objects.get(**query_str)
            product_data = ProductSerializer(product).data
        except Exception as e:
            msg = '[ProductService][read_product_with_query][' + str(e) + ']'
            self.logger_error.error(msg)
            product_data = {}

        return product_data

    def read_product_list_with_query(self, query_str):
        try:
            product_qs = Product.objects.filter(**query_str).order_by('list_index')
        except Exception as e:
            msg = '[ProductService][read_product_list_with_query][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return product_qs

    def update_product_with_data(self, product_data):
        try:
            product_ins = Product.objects.get(id=product_data['id'])
            product_serializer = ProductAdminSerializer(product_ins, data=product_data)
            product_serializer.is_valid()
            product_serializer.save()
        except Exception as e:
            msg = '[ProductService][update_product_with_data][' + str(e) + ']'
            self.logger_error.error(msg)
        else:
            product_data = product_serializer.data

        return product_data

    def read_product_discount_info(self, time_bomb_id, product_id_list):
        discount_data = []

        try:
            discount_qs = TimeBombDiscountInfo.objects.filter(time_bomb_id=time_bomb_id,
                                                              product_id__in=product_id_list)
            discount_data = TimeBombDiscountInfoSerializer(discount_qs, many=True).data
        except Exception as e:
            msg = '[ProductService][read_product_discount_info][' + str(e) + ']'
            self.logger_error.error(msg)

        return discount_data

    def read_product_discount_info_with_id(self, time_bomb_id):
        discount_data = []

        try:
            discount_qs = TimeBombDiscountInfo.objects.filter(time_bomb_id=time_bomb_id)
            discount_data = TimeBombDiscountInfoSerializer(discount_qs, many=True).data
        except Exception as e:
            msg = '[ProductService][read_product_discount_info_with_id][' + str(e) + ']'
            self.logger_error.error(msg)

        return discount_data

    def has_product(self, product_id):
        try:
            product_qs = Product.objects.filter(id=product_id)
        except Exception as e:
            msg = '[ProductService][has_product][' + str(e) + ']'
            self.logger_error.error(msg)
            result = False
        else:
            result = product_qs.exists()

        return result
