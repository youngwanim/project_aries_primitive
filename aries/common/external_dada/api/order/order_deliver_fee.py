# -*- encoding: utf8 -*-
from aries.common.external_dada.api.base import ApiBaseClass
from aries.common.external_dada.api.urls import ORDER_QUERY_DELIVER_FEE_URI

__all__ = [
    "OrderDeliverFeeClass"
]


class OrderDeliverFeeClass(ApiBaseClass):

    uri = ORDER_QUERY_DELIVER_FEE_URI

    def __init__(self, model=None):
        """
        :return:
        """
        super(OrderDeliverFeeClass, self).__init__()
        self._model = model
