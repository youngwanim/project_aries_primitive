# -*- encoding: utf8 -*-
from aries.common.external_dada.api.merchant.merchant_add import MerchantAddApiClass
from aries.common.external_dada.api.merchant.shop_add import ShopAddApiClass
from aries.common.external_dada.api.order.order import OrderAddClass
from aries.common.external_dada.dada_client import DadaApiClient
from aries.common.external_dada.dada_config import QAConfig
from aries.common.external_dada.model.merchant.merchant_add import MerchantAddModel
from aries.common.external_dada.model.merchant.shop_add import ShopAddModel
from aries.common.external_dada.model.order.order import OrderModel

__author__ = 'wan'

import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


def shop_add_example():
    """
    添加门店的示例
    :return:
    """
    # 1.初始化客户端
    dada_client = DadaApiClient(QAConfig)

    # 2.选择一个api类,同时初始化api参数model
    shop_model = ShopAddModel()
    shop_model.area_name = "浦东新区"
    shop_model.business = 1
    shop_model.city_name = "上海"
    shop_model.contact_name = "达达"
    shop_model.lat = 31.228623
    shop_model.lng = 121.587172
    shop_model.phone = "13809126789"
    shop_model.station_address = "隆宇大厦"
    shop_model.station_name = "测试sdk"
    shop_add_api = ShopAddApiClass(model=shop_model)

    # 3.rpc请求
    result = dada_client.do_rpc(api=shop_add_api)
    print(result.to_string())


def add_order_example():
    """
    添加订单示例
    :return:
    """
    # 1.初始化客户端
    dada_client = DadaApiClient(QAConfig)

    # 2.选择一个api类,同时初始化api参数model
    order_model = OrderModel()
    order_model.shop_no = "11047059"
    order_model.origin_id = "test0000000002"
    order_model.cargo_price = 11
    order_model.city_code = "021"
    order_model.is_prepay = 0
    order_model.receiver_name = "测试达达"
    order_model.receiver_address = "虹口足球场"
    order_model.receiver_lat = 31.228623
    order_model.receiver_lng = 121.587172
    order_model.receiver_phone = "13798061234"
    order_model.callback = "http://139.196.123.42:8080/purchases/callback/dada"

    """
        tips = None
        info = None
        cargo_type = 1
        cargo_weight = None
        delay_publish_time = None
        is_direct_delivery = None    
    """

    order_add_api = OrderAddClass(model=order_model)
    # 3.rpc请求
    result = dada_client.do_rpc(api=order_add_api)
    print(result.to_string())


def merchant_add_example():
    """
    注册商户示例
    :return:
    """
    # 1.初始化客户端,注册商户的时候不需要source_id
    dada_client = DadaApiClient(QAConfig, is_user_source_id=False)

    # 2.选择一个api类,同时初始化api参数model
    merchant_add = MerchantAddModel()
    merchant_add.city_name = "上海"
    merchant_add.enterprise_address = "上海隆宇大厦"
    merchant_add.enterprise_name = "测试上海sdk"
    merchant_add.contact_name = "测试达达"
    merchant_add.contact_phone = "13798061234"
    merchant_add.mobile = "13798061234"
    merchant_add.email = "13798061234@qq.com"

    merchant_add_api = MerchantAddApiClass(model=merchant_add)
    # 3.rpc请求
    result = dada_client.do_rpc(api=merchant_add_api)
    print(result.to_string())


if __name__ == '__main__':
    add_order_example()
