# -*- encoding: utf8 -*-
from aries.common.external_dada.api.base import ApiBaseClass
from aries.common.external_dada.api.urls import ORDER_DETAIL_QUERY_URI

__all__ = [
    "OrderDetailClass"
]


class OrderDetailClass(ApiBaseClass):

    uri = ORDER_DETAIL_QUERY_URI

    def __init__(self, model=None):
        """
        :return:
        """
        super(OrderDetailClass, self).__init__()
        self._model = model
