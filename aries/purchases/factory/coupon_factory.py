from decimal import Decimal, ROUND_HALF_UP

from aries.common import hub_data

CASH_POINT = 0
CASH_PERCENT = 1
FREE_MEAL = 2
ONE_PLUS_ONE = 3
DELIVERY = 4
GIFT = 5


class CouponInstance(object):
    coupon_data = ''
    discount_price = 0.0
    coupon_rule_result = True

    def __init__(self, coupon, target_id, product_list):
        self.coupon = coupon
        self.target_id = target_id
        self.product_list = product_list

    def factory(coupon_type, coupon, target_id, product_list):
        if coupon_type == CASH_POINT:
            return CashPoint(coupon, target_id, product_list)
        if coupon_type == CASH_PERCENT:
            return CashPercent(coupon, target_id, product_list)
        if coupon_type == FREE_MEAL:
            return FreeMeal(coupon, target_id, product_list)
        if coupon_type == ONE_PLUS_ONE:
            return OnePlusOne(coupon, target_id, product_list)
        if coupon_type == DELIVERY:
            return DeliveryCoupon(coupon, target_id, product_list)
        if coupon_type == GIFT:
            return Gift(coupon, target_id, product_list)

    factory = staticmethod(factory)


class CashPoint(CouponInstance):
    def check_coupon_rule(self):
        target_type = self.coupon['target_type']

        product_ids = set()
        products_price = 0
        products_quantity = 0

        if len(self.product_list) == 1 and self.product_list[0]['event_product']:
            return False

        for product in self.product_list:
            if not product['event_product']:
                product_ids.add(product['id'])
                products_price += product['price'] * product['quantity']
                products_quantity += product['quantity']

        # Check general rules
        if self.coupon['cash_minimum'] != 0 and self.coupon['cash_minimum'] > products_price:
            return False

        if self.coupon['target_min'] != 0 and self.coupon['target_min'] > products_quantity:
            return False

        if target_type == 100:
            target_ids = self.coupon['target_product_ids']
            has_product = False

            for product_id in target_ids:
                if product_id in product_ids:
                    has_product = True
                    break

            if not has_product:
                return False

        return self.coupon_rule_result

    def get_discount_price(self):
        cash_maximum = self.coupon['cash_maximum']

        if cash_maximum == 0:
            self.discount_price = self.coupon['cash_discount']
        else:
            if self.coupon['cash_discount'] > cash_maximum:
                self.discount_price = cash_maximum
            else:
                self.discount_price = self.coupon['cash_discount']

        return self.discount_price


class CashPercent(CouponInstance):
    def check_coupon_rule(self):
        target_type = self.coupon['target_type']

        product_ids = set()
        products_price = 0
        products_quantity = 0

        if len(self.product_list) == 1 and self.product_list[0]['event_product']:
            return False

        for product in self.product_list:
            if not product['event_product']:
                product_ids.add(product['id'])
                products_price += product['price']
                products_quantity += product['quantity']

        # Check general rules
        if self.coupon['cash_minimum'] != 0 and self.coupon['cash_minimum'] > products_price:
            return False

        if self.coupon['target_min'] != 0 and self.coupon['target_min'] > products_quantity:
            return False

        if target_type == 100:
            target_ids = self.coupon['target_product_ids']
            has_product = False

            for product_id in target_ids:
                if product_id in product_ids:
                    has_product = True
                    break

            if not has_product:
                return False

        return self.coupon_rule_result

    def get_discount_price(self):
        products_price = 0
        cash_maximum = self.coupon['cash_maximum']
        target_ids = self.coupon['target_product_ids']
        product_ids = set()

        for product in self.product_list:
            if not product['event_product']:
                product_ids.add(product['id'])
                if product['price_discount_event']:
                    products_price += (product['price_discount']*product['quantity'])
                else:
                    products_price += (product['price']*product['quantity'])

        discount_percent = self.coupon['cash_discount']/100

        target_type = self.coupon['target_type']
        exp = Decimal('.00')

        if target_type == 200:
            price_decimal = Decimal(products_price * discount_percent)
            self.discount_price = float(price_decimal.quantize(exp, rounding=ROUND_HALF_UP))
        else:
            if len(target_ids) == 0:
                price_decimal = Decimal(products_price * discount_percent)
                self.discount_price = float(price_decimal.quantize(exp, rounding=ROUND_HALF_UP))
            else:
                new_products_price = 0
                for product in self.product_list:
                    if product['id'] in target_ids:
                        new_products_price += (product['price']*product['quantity'])
                price_decimal = Decimal(new_products_price * discount_percent)
                self.discount_price = float(price_decimal.quantize(exp, rounding=ROUND_HALF_UP))

        if cash_maximum != 0 and cash_maximum < self.discount_price:
            self.discount_price = cash_maximum

        return self.discount_price


class FreeMeal(CouponInstance):
    def check_coupon_rule(self):
        target_type = self.coupon['target_type']

        product_ids = set()
        products_price = 0
        products_quantity = 0

        if len(self.product_list) == 1 and self.product_list[0]['event_product']:
            return False

        for product in self.product_list:
            if not product['event_product']:
                product_ids.add(product['id'])
                products_price += product['price']
                products_quantity += product['products_quantity']

        # Check general rules
        if self.coupon['cash_minimum'] != 0 and self.coupon['cash_minimum'] > products_price:
            return False

        if self.coupon['target_min'] != 0 and self.coupon['target_min'] > products_quantity:
            return False

        if target_type == 100:
            target_ids = self.coupon['target_product_ids']
            has_product = False
            for product_id in target_ids:
                if product_id in product_ids:
                    has_product = True
                    break
            if not has_product:
                return False

        return True

    def get_discount_price(self):
        cash_maximum = self.coupon['cash_maximum']
        product_price = 0

        for product in self.product_list:
            if product['id'] == self.target_id:
                product_price = product['price']
                break

        if product_price > cash_maximum:
            return round(float(cash_maximum), 3)
        else:
            return round(float(product_price), 3)


class OnePlusOne(CouponInstance):
    def check_coupon_rule(self):
        target_type = self.coupon['target_type']

        product_ids = set()
        products_price = 0
        products_quantity = 0

        if len(self.product_list) == 1 and self.product_list[0]['event_product']:
            return False

        for product in self.product_list:
            if not product['event_product']:
                product_ids.add(product['id'])
                products_price += product['price']
                products_quantity += product['products_quantity']

        # Check general rules
        if self.coupon['cash_minimum'] != 0 and self.coupon['cash_minimum'] > products_price:
            return False

        if self.coupon['target_min'] != 0 and self.coupon['target_min'] > products_quantity:
            return False

        if target_type == 100:
            target_ids = self.coupon['target_product_ids']
            has_product = False
            for product_id in target_ids:
                if product_id in product_ids:
                    has_product = True
                    break
            if not has_product:
                return False

        return True

    def get_discount_price(self):
        cash_maximum = self.coupon['cash_maximum']
        product_price = 0

        for product in self.product_list:
            if product['id'] == self.target_id:
                product_price = product['price']
                break

        if product_price > cash_maximum:
            return round(float(cash_maximum), 3)
        else:
            return round(float(product_price), 3)


class DeliveryCoupon(CouponInstance):
    def check_coupon_rule(self):
        return self.coupon_rule_result

    def get_discount_price(self):
        return hub_data.get_shipping_cost(self.coupon['delivery_detail'])


class Gift(CouponInstance):
    def check_coupon_rule(self):
        target_type = self.coupon['target_type']

        product_ids = set()
        products_price = 0
        products_quantity = 0

        for product in self.product_list:
            product_ids.add(product['id'])
            products_price += product['price']
            products_quantity += product['quantity']

        # Check general rules
        if self.coupon['cash_minimum'] != 0 and self.coupon['cash_minimum'] > products_price:
            return False

        if self.coupon['target_min'] != 0 and self.coupon['target_min'] > products_quantity:
            return False

        if target_type == 100:
            target_ids = self.coupon['target_product_ids']
            has_product = False
            for product_id in target_ids:
                if product_id in product_ids:
                    has_product = True
                    break
            if not has_product:
                return False

        return True

    def get_discount_price(self):
        return self.discount_price
