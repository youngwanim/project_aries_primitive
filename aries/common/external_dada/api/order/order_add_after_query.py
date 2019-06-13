# -*- encoding: utf8 -*-
from aries.common.external_dada.api.base import ApiBaseClass
from aries.common.external_dada.api.urls import ORDER_ADD_AFTER_QUERY_FEE_URI

__all__ = [
    "OrderAddAfterQueryClass"
]


class OrderAddAfterQueryClass(ApiBaseClass):

    uri = ORDER_ADD_AFTER_QUERY_FEE_URI

    def __init__(self, model=None):
        """
        :return:
        """
        super(OrderAddAfterQueryClass, self).__init__()
        self._model = model
