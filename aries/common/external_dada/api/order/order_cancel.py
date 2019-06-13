# -*- encoding: utf8 -*-
from aries.common.external_dada.api.base import ApiBaseClass
from aries.common.external_dada.api.urls import ORDER_CANCEL_URI

__all__ = [
    "OrderCancelClass"
]


class OrderCancelClass(ApiBaseClass):

    uri = ORDER_CANCEL_URI

    def __init__(self, model=None):
        """
        :return:
        """
        super(OrderCancelClass, self).__init__()
        self._model = model
