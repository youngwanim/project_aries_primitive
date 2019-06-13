# -*- encoding: utf8 -*-
from aries.common.external_dada.model.base import BaseModel

__author__ = 'wan'


class MerchantAddModel(BaseModel):

    def __init__(self):
        """
        注册商户
        :return:
        """
        self.mobile = None
        self.city_name = None
        self.enterprise_name = None
        self.enterprise_address = None
        self.contact_name = None
        self.contact_phone = None
        self.email = None

    def field_check(self):
        """
        校验必填参数
        :return:
        """
        for key, value in self.__dict__.items():
            if value is None:
                raise TypeError("%s value can not be null" % key)

        return True
