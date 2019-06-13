# -*- encoding: utf8 -*-
from aries.common.external_dada.api.base import ApiBaseClass
from aries.common.external_dada.api.urls import MERCHANT_REGISTER_URI

__author__ = 'wan'


class MerchantAddApiClass(ApiBaseClass):

    uri = MERCHANT_REGISTER_URI

    def __init__(self, model=None):
        super(MerchantAddApiClass, self).__init__()
        self._model = model
