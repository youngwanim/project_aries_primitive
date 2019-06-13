from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.external_dada.api.order.order_add_tip import OrderAddTipClass
from aries.common.external_dada.api.order.order_cancel import OrderCancelClass
from aries.common.external_dada.api.order.order_details import OrderDetailClass
from aries.common.external_dada.model.order.order_add_tip import OrderAddTipModel
from aries.common.external_dada.model.order.order_cancel import OrderCancelModel
from aries.common.external_dada.model.order.order_details import OrderDetailModel
from aries.purchases.common.dada_func import make_new_order, get_dada_client, get_dada_shop_no, make_query_fee, \
    make_order_add_after_query
from aries.purchases.service.dada_service import DadaService
from aries.purchases.service.order_service import OrderService


class DadaManager:

    SHOP_NO = '000000001'
    PREPAY_SETTING = 0
    CITY_CODE_SHANGHAI = '021'

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.dada_service = DadaService(logger_info, logger_error)
        self.order_service = OrderService(logger_info, logger_error)

        self.dada_client = get_dada_client()
        self.SHOP_NO = get_dada_shop_no()

    def add_order(self, request_data):
        # Get request params
        order_id = request_data['order_id']

        # Get order instance
        order_instance = self.order_service.get_order_instance(order_id)
        purchase_order = order_instance.purchase_order

        order_add_api = make_new_order(False, order_instance, purchase_order, request_data)

        # Call dada API
        dada_result = self.dada_client.do_rpc(api=order_add_api)
        print(dada_result.to_string())
        dada_dict_result = dada_result.to_dict()

        if dada_dict_result['status'] != 'success':
            raise BusinessLogicError('API connect failed', None, None)

        add_order_result = dada_dict_result['result']

        # Create dada order object
        self.dada_service.create_dada_order_req(order_add_api._model, add_order_result)

    def re_add_order(self, request_data):
        # Get request params
        order_id = request_data['order_id']

        # Get order instance
        order_instance = self.order_service.get_order_instance(order_id)
        purchase_order = order_instance.purchase_order

        order_add_api = make_new_order(True, order_instance, purchase_order, request_data)

        # Call dada API
        dada_result = self.dada_client.do_rpc(api=order_add_api)
        print(dada_result.to_string())
        dada_dict_result = dada_result.to_dict()

        if dada_dict_result['status'] != 'success':
            raise BusinessLogicError('API connect failed', None, None)

        add_order_result = dada_dict_result['result']

        # Create dada order object
        self.dada_service.create_dada_order_req(order_add_api._model, add_order_result)

    def add_order_detail(self, order_id, receiver_address, receiver_lat, receiver_lng):
        # make dada order model and api model
        order_detail_model = OrderDetailModel()
        order_detail_model.order_id = order_id
        order_detail_api = OrderDetailClass(model=order_detail_model)

        # Call dada api
        self.logger_info.info(order_detail_model)
        dada_result = self.dada_client.do_rpc(api=order_detail_api)
        self.logger_info.info(dada_result.to_string())
        dada_dict_result = dada_result.to_dict()

        if dada_dict_result['status'] != 'success':
            raise BusinessLogicError('API connect failed', None, None)

        order_detail_result = dada_dict_result['result']

        # Receiver information add
        order_detail_result['receiver_address'] = receiver_address
        order_detail_result['receiver_lat'] = receiver_lat
        order_detail_result['receiver_lng'] = receiver_lng

        # Create dada detail
        self.dada_service.create_dada_order_detail(order_detail_result)

    def read_order_detail(self, order_id):
        return self.dada_service.read_dada_order_detail(order_id)

    def update_order_detail(self, order_id):
        # make dada order model and api model
        order_detail_model = OrderDetailModel()
        order_detail_model.order_id = order_id
        order_detail_api = OrderDetailClass(model=order_detail_model)

        # Call dada api
        self.logger_info.info(order_detail_model)
        dada_result = self.dada_client.do_rpc(api=order_detail_api)
        self.logger_info.info(dada_result.to_string())
        dada_dict_result = dada_result.to_dict()

        if dada_dict_result['status'] != 'success':
            raise BusinessLogicError('API connect failed', None, None)

        order_detail_result = dada_dict_result['result']

        return self.dada_service.update_dada_order_detail(order_id, order_detail_result)

    def cancel_order(self, order_id, cancel_reason_id):
        # make dada order cancel model and api model
        order_cancel_model = OrderCancelModel()
        order_cancel_model.order_id = order_id
        order_cancel_model.cancel_reason_id = cancel_reason_id
        order_cancel_api = OrderCancelClass(model=order_cancel_model)

        # Call dada api
        self.logger_info.info(order_cancel_model)
        dada_result = self.dada_client.do_rpc(api=order_cancel_api)
        self.logger_info.info(dada_result.to_string())
        dada_dict_result = dada_result.to_dict()

        if dada_dict_result['status'] != 'success':
            raise BusinessLogicError('API connect failed', None, None)

        order_cancel_result = dada_dict_result['result']

        return order_cancel_result

    def add_tip(self, order_id, tips, city_code, info):
        # add tips for order
        order_add_tip_model = OrderAddTipModel()
        order_add_tip_model.order_id = order_id
        order_add_tip_model.tips = tips
        order_add_tip_model.city_code = city_code
        order_add_tip_model.info = info
        order_add_tip_api = OrderAddTipClass(model=order_add_tip_model)

        # Call dada api
        self.logger_info.info(order_add_tip_model)
        dada_result = self.dada_client.do_rpc(api=order_add_tip_api)
        self.logger_info.info(dada_result.to_string())
        dada_dict_result = dada_result.to_dict()

        if dada_dict_result['status'] != 'success':
            raise BusinessLogicError('API connect failed', None, None)

        order_add_tip_result = dada_dict_result['result']

        return order_add_tip_result

    def query_delivery_fee(self, request_data):
        # Get request params
        order_id = request_data['order_id']

        # Get order instance
        order_instance = self.order_service.get_order_instance(order_id)
        purchase_order = order_instance.purchase_order

        query_order_fee = make_query_fee(order_instance, purchase_order, request_data)

        # Call dada API
        dada_result = self.dada_client.do_rpc(api=query_order_fee)
        print(dada_result.to_string())
        dada_dict_result = dada_result.to_dict()

        if dada_dict_result['status'] != 'success':
            raise BusinessLogicError('API connect failed', None, None)

        query_order_fee_result = dada_dict_result['result']

        return query_order_fee_result

    def order_add_after_query(self, request_data):
        # Get request params
        delivery_no = request_data['deliveryNo']

        order_add_after_query = make_order_add_after_query(delivery_no)

        # Call dada API
        dada_result = self.dada_client.do_rpc(api=order_add_after_query)
        print(dada_result.to_string())
        dada_dict_result = dada_result.to_dict()

        if dada_dict_result['status'] != 'success':
            raise BusinessLogicError('API connect failed', None, None)

        query_order_fee_result = dada_dict_result['result']

        return query_order_fee_result

    def order_location_query(self, request_data):
        # Get request params
        order_id = request_data['order_id']

        # make dada order model and api model
        order_detail_model = OrderDetailModel()
        order_detail_model.order_id = order_id
        order_detail_api = OrderDetailClass(model=order_detail_model)

        # Call dada api
        self.logger_info.info(order_detail_model)
        dada_result = self.dada_client.do_rpc(api=order_detail_api)
        self.logger_info.info(dada_result.to_string())
        dada_dict_result = dada_result.to_dict()

        if dada_dict_result['status'] != 'success':
            raise BusinessLogicError('API connect failed', None, None)

        order_detail_result = dada_dict_result['result']

        return order_detail_result
