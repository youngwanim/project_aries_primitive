import calendar
import json
import time
import requests

from django.conf import settings

from aries.common import urlmapper
from aries.common.exceptions.exceptions import DataValidationError
from aries.common.external_dada.api.order.order import OrderAddClass
from aries.common.external_dada.api.order.order_add_after_query import OrderAddAfterQueryClass
from aries.common.external_dada.api.order.order_deliver_fee import OrderDeliverFeeClass
from aries.common.external_dada.api.order.reorder import ReOrderAddClass
from aries.common.external_dada.dada_client import DadaApiClient
from aries.common.external_dada.dada_config import QAConfig, ReleaseConfig, StageConfig
from aries.common.external_dada.model.order.order import OrderModel
from aries.common.external_dada.model.order.order_add_after_query import OrderAddAfterQuery
from aries.common.external_dada.model.order.order_deliver_fee import OrderDeliverFeeModel
from aries.common.external_dada.model.order.reorder import ReOrderModel


def get_dada_client():
    if settings.DEBUG:
        dada_client = DadaApiClient(QAConfig)
    elif settings.STAGE:
        dada_client = DadaApiClient(StageConfig)
    else:
        dada_client = DadaApiClient(ReleaseConfig)
    return dada_client


def get_dada_shop_no():
    if settings.DEBUG:
        shop_no = '11047059'
    elif settings.STAGE:
        shop_no = '11047059'
    else:
        shop_no = '6318255'
    return shop_no


def get_dada_callback_url():
    if settings.DEBUG:
        callback_url = 'http://139.196.123.42:8080/purchases/callback/dada'
    elif settings.STAGE:
        callback_url = 'https://stg-api.viastelle.com/purchases/callback/dada'
    else:
        callback_url = 'https://api.viastelle.com/purchases/callback/dada'
    return callback_url


def dada_new_order_validation(request_data):
    if 'order_id' not in request_data:
        raise DataValidationError('Request data invalid', None)
    if 'cargo_weight' not in request_data or 'tips' not in request_data:
        raise DataValidationError('Request data invalid', None)
    if 'is_use_insurance' not in request_data or 'info' not in request_data:
        raise DataValidationError('Request data invalid', None)
    if 'receiver_address' not in request_data:
        raise DataValidationError('Request data invalid', None)
    if 'receiver_lat' not in request_data or 'receiver_lng' not in request_data:
        raise DataValidationError('Request data invalid', None)


def dada_cancel_order_validation(request_data):
    if 'order_id' not in request_data:
        raise DataValidationError('Request data invalid', None)
    if 'cancel_reason_id' not in request_data:
        raise DataValidationError('Request data invalid', None)


def dada_order_add_tip_validation(request_data):
    if 'order_id' not in request_data:
        raise DataValidationError('Request data invalid', None)
    if 'tips' not in request_data or 'tips' not in request_data:
        raise DataValidationError('Request data invalid', None)
    if 'city_code' not in request_data or 'info' not in request_data:
        raise DataValidationError('Request data invalid', None)


def dada_order_add_after_query_validation(request_data):
    if 'deliveryNo' not in request_data:
        raise DataValidationError('Request data invalid', None)


def dada_query_validation(request_data):
    if 'order_id' not in request_data:
        raise DataValidationError('Request data invalid', None)


def make_new_order(is_reorder, order_instance, purchase_order, request_data):
    shop_no = get_dada_shop_no()
    prepay_setting = 0
    city_code_shanghai = '021'

    order_id = request_data['order_id']

    cargo_price = purchase_order.price_sub_total - purchase_order.price_discount
    city_code = city_code_shanghai
    is_prepay = prepay_setting

    # Receiver name check
    receiver_name = order_instance.delivery_recipient_name
    receiver_phone = order_instance.delivery_recipient_mdn

    if len(receiver_name) <= 0 and len(receiver_phone) <= 0:
        receiver_name = order_instance.user_name
        receiver_phone = order_instance.user_telephone

    # Get required params to receiver address
    receiver_address = request_data['receiver_address']
    receiver_lat = request_data['receiver_lat']
    receiver_lng = request_data['receiver_lng']

    # Get optional params
    cargo_weight = request_data['cargo_weight']
    tips = request_data['tips']
    is_use_insurance = request_data['is_use_insurance']
    info = request_data['info']

    # make dada order model and api model
    if is_reorder:
        order_model = ReOrderModel()
    else:
        order_model = OrderModel()

    order_model.shop_no = shop_no
    order_model.origin_id = order_id
    order_model.cargo_price = cargo_price
    order_model.city_code = city_code
    order_model.is_prepay = is_prepay
    order_model.receiver_name = receiver_name
    order_model.receiver_address = receiver_address
    order_model.receiver_lat = receiver_lat
    order_model.receiver_lng = receiver_lng
    order_model.receiver_phone = receiver_phone
    order_model.callback = get_dada_callback_url()

    # Optional data
    order_model.cargo_weight = cargo_weight
    order_model.tips = tips
    order_model.is_use_insurance = is_use_insurance
    order_model.info = info

    print(order_model.to_dict())

    if is_reorder:
        order_add_api = ReOrderAddClass(model=order_model)
    else:
        order_add_api = OrderAddClass(model=order_model)

    return order_add_api


def make_query_fee(order_instance, purchase_order, request_data):
    shop_no = get_dada_shop_no()
    prepay_setting = 0
    city_code_shanghai = '021'

    order_id = request_data['order_id']

    cargo_price = purchase_order.price_sub_total - purchase_order.price_discount
    city_code = city_code_shanghai
    is_prepay = prepay_setting

    # Receiver name check
    receiver_name = order_instance.delivery_recipient_name
    receiver_phone = order_instance.delivery_recipient_mdn

    if len(receiver_name) <= 0 and len(receiver_phone) <= 0:
        receiver_name = order_instance.user_name
        receiver_phone = order_instance.user_telephone

    # Get required params to receiver address
    receiver_address = request_data['receiver_address']
    receiver_lat = request_data['receiver_lat']
    receiver_lng = request_data['receiver_lng']

    # Get optional params
    cargo_weight = request_data['cargo_weight']
    tips = request_data['tips']
    is_use_insurance = request_data['is_use_insurance']
    info = request_data['info']

    # make dada order model and api model
    order_model = OrderDeliverFeeModel()

    order_model.shop_no = shop_no
    order_model.origin_id = order_id
    order_model.cargo_price = cargo_price
    order_model.city_code = city_code
    order_model.is_prepay = is_prepay
    order_model.receiver_name = receiver_name
    order_model.receiver_address = receiver_address
    order_model.receiver_lat = receiver_lat
    order_model.receiver_lng = receiver_lng
    order_model.receiver_phone = receiver_phone
    order_model.callback = get_dada_callback_url()

    # Optional data
    order_model.cargo_weight = cargo_weight
    order_model.tips = tips
    order_model.is_use_insurance = is_use_insurance
    order_model.info = info

    print(order_model.to_dict())

    order_query_fee_api = OrderDeliverFeeClass(model=order_model)

    return order_query_fee_api


def make_order_add_after_query(delivery_no):
    order_model = OrderAddAfterQuery()
    order_model.deliveryNo = delivery_no
    print(order_model.to_dict())

    order_add_after_query = OrderAddAfterQueryClass(model=order_model)

    return order_add_after_query


def dada_message_to_operation(dada_message):
    ts = calendar.timegm(time.gmtime())
    message = {
        'type': 'notification',
        'domain': 'dada_callback',
        'timestamp': str(ts),
        'payload': json.dumps(
            {'shipping_order_detail': dada_message}
        )
    }

    url = urlmapper.get_url('OPERATION_MESSAGE')

    requests.post(url, json=message)
