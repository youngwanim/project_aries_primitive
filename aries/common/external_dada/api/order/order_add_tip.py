# -*- encoding: utf8 -*-
from aries.common.external_dada.api.base import ApiBaseClass
from aries.common.external_dada.api.urls import ORDER_ADD_TIP_URI

__all__ = [
    "OrderAddTipClass"
]


class OrderAddTipClass(ApiBaseClass):

    uri = ORDER_ADD_TIP_URI

    def __init__(self, model=None):
        """
        :return:
        """
        super(OrderAddTipClass, self).__init__()
        self._model = model
