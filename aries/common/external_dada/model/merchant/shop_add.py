# -*- encoding: utf8 -*-
from aries.common.external_dada.model.base import BaseModel

__author__ = 'wan'


class ShopAddModel(BaseModel):

    def __init__(self):
        """
        新增门店接口
        :return:
        """
        self.station_name = None
        self.business = None
        self.city_name = None
        self.area_name = None
        self.station_address = None
        self.lng = None
        self.lat = None
        self.contact_name = None
        self.phone = None

    def field_check(self):
        """
        校验必填参数
        :return:
        """
        for key, value in self.__dict__.items():
            if value is None:
                raise TypeError("%s value can not be null" % key)

        return True
