from aries.common import code
from aries.common.code_msg import get_msg
from aries.products.models import Product, Menu


class PurchaseOrderValidator:

    def __init__(self, product_list, cn_header, target_db):
        self.product_list = product_list
        self.cn_header = cn_header
        self.target_db = target_db

    def product_validate(self, product):

        try:
            product_instance = Product.objects.get(id=product['product_id'])
            menu_instance = Menu.objects.using(self.target_db).get(id=product_instance.menu.id)
        except Exception as e:
            print(e)
            result = (False, None)
            return result

        # Product quantity
        order_quantity = product['quantity']
        stock = product_instance.stock

        if stock < order_quantity:
            error_message = get_msg(code.ERROR_3001_PRODUCT_ALREADY_SOLD, self.cn_header)
            error_message = error_message + ' [' + menu_instance.name + ']'

            result = (False, error_message)
            return result
