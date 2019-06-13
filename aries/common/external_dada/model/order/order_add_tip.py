# -*- encoding: utf8 -*-
from aries.common.external_dada.model.base import BaseModel


class OrderAddTipModel(BaseModel):

    def __init__(self):
        """
        业务参数
        :return:
        """
        self.order_id = None
        self.tips = None
        self.city_code = None
        self.info = None

    def field_check(self):
        """
        :return:
        """
        for key, value in self.__dict__.items():
            if value is None:
                raise TypeError("%s value can not be null" % key)

        return True
