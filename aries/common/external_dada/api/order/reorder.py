# -*- encoding: utf8 -*-
from aries.common.external_dada.api.base import ApiBaseClass
from aries.common.external_dada.api.urls import ORDER_RE_ADD_URI

__all__ = [
    "ReOrderAddClass"
]


class ReOrderAddClass(ApiBaseClass):

    uri = ORDER_RE_ADD_URI

    def __init__(self, model=None):
        """
        :return:
        """
        super(ReOrderAddClass, self).__init__()
        self._model = model
