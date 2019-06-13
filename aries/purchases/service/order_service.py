from aries.purchases.models import Order


class OrderService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def get_today_order_index(self, target_date):
        order_count = Order.objects.filter(delivery_date=target_date).count()
        self.logger_info.info('[OrderService][get_today_order_index][' + str(order_count) + ']')
        return order_count + 1

    def get_order_instance(self, order_id):
        self.logger_info.info('[OrderService][get_order_instance][' + str(order_id) + ']')
        order_instance = Order.objects.get(order_id=order_id)
        return order_instance
