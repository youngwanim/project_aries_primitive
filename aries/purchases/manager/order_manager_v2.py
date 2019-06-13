import datetime

from aries.common.product_util import get_phase_next_day
from aries.purchases.service.order_service import OrderService


class OrderManagerV2:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.order_service = OrderService(self.logger_info, self.logger_error)

    def get_daily_order_index(self):
        target_date = datetime.datetime.today()
        if get_phase_next_day():
            target_date = target_date + datetime.timedelta(days=1)
        return self.order_service.get_today_order_index(target_date)
