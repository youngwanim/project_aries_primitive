from aries.products.models import ProductType
from aries.products.serializers import ProductTypeSerializer


class ProductTypeService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def create_product_type(self):
        pass

    def read_product_type(self, cn_header=False):
        language_type = 1 if cn_header else 0

        try:
            product_type_list = []
            product_type_qs = ProductType.objects.filter(language_type=language_type)
            print(product_type_qs)
            for product_type in product_type_qs:
                product_type_instance = ProductType.objects.get(id=product_type.id)
                product_type_list.append(ProductTypeSerializer(product_type_instance).data)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = product_type_list

        return self.result

    def update_product_type(self):
        pass

    def delete_product_type(self):
        pass
