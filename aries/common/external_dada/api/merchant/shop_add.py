# -*- encoding: utf8 -*-
from aries.common.external_dada.api.base import ApiBaseClass
from aries.common.external_dada.api.urls import MERCHANT_ADD_SHOP_URI

__author__ = 'wan'


import json


class ShopAddApiClass(ApiBaseClass):

    uri = MERCHANT_ADD_SHOP_URI

    def __init__(self, model=None):
        super(ShopAddApiClass, self).__init__()
        self._model = model

    def get_business_params(self):
        """
        shopadd是一个批量添加的接口
        :return:
        """
        single_data = self._model.to_dict()
        return json.dumps([single_data])
