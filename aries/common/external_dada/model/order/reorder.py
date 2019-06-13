# -*- encoding: utf8 -*-
from aries.common.external_dada.model.base import BaseModel


class ReOrderModel(BaseModel):

    def __init__(self):
        """
        业务参数
        :return:
        """
        # Must params
        self.shop_no = None
        self.origin_id = None
        self.city_code = None
        self.cargo_price = None
        self.is_prepay = 0
        self.receiver_name = None
        self.receiver_address = None
        self.receiver_lat = None
        self.receiver_lng = None
        self.callback = None
        self.receiver_phone = None
        # Optional params
        self.cargo_weight = None
        self.tips = None
        self.is_use_insurance = None
        self.info = None

    def field_check(self):
        """
        :return:
        """
        for key, value in self.__dict__.items():
            if value is None:
                raise TypeError("%s value can not be null" % key)

        return True
