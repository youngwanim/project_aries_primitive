# -*- encoding: utf8 -*-
from aries.common.external_dada.model.base import BaseModel


class OrderAddAfterQuery(BaseModel):

    def __init__(self):
        """
        业务参数
        :return:
        """
        self.deliveryNo = None

    def field_check(self):
        """
        :return:
        """
        for key, value in self.__dict__.items():
            if value is None:
                raise TypeError("%s value can not be null" % key)

        return True
