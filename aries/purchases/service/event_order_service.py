import datetime

from aries.common.exceptions.exceptions import BusinessLogicError
from aries.purchases.models import EventOrderHistory


class EventOrderService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def create_event_order(self, event_type, hub_id, open_id, order_id):
        try:
            self.logger_info.info('[event_order_service][EventOrderService][create_event_order][' + order_id + ']')
            event_order = EventOrderHistory.objects.create(
                event_type=event_type,
                event_target=True,
                event_description='first_purchase',
                hub_id=hub_id,
                open_id=open_id,
                order_id=order_id,
                register_date=datetime.datetime.today().date()
            )
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e), None, None)
        else:
            self.result = event_order

        return self.result
