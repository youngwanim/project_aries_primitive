from aries.common.exceptions.exceptions import BusinessLogicError
from aries.purchases.models import DadaOrderRequest, DadaOrderDetail
from aries.purchases.serializers import DadaOrderDetailSerializer


class DadaService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def create_dada_order_req(self, order_model, dada_result):
        try:
            dada_order_req = {}

            order_model_dict = order_model.__dict__

            for key, value in order_model_dict.items():
                dada_order_req[key] = value

            for key, value in dada_result.items():
                dada_order_req['res_' + key] = value

            self.logger_info.info(dada_order_req)
            dada_order_req_ins = DadaOrderRequest.objects.create(**dada_order_req)
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e), None, None)
        else:
            self.result = dada_order_req_ins

        return self.result

    def create_dada_order_detail(self, dada_result):
        try:
            dada_order_detail_dict = {}

            for key, value in dada_result.items():
                dada_order_detail_dict[key] = value

            self.logger_info.info(dada_order_detail_dict)
            dada_order_detail = DadaOrderDetail.objects.create(**dada_order_detail_dict)
        except Exception as e:
            self.logger_error.error(str(e))
            raise BusinessLogicError(str(e), None, None)
        else:
            self.result = dada_order_detail

        return self.result

    def read_dada_order_detail(self, order_id):
        try:
            dada_order_count = DadaOrderDetail.objects.filter(orderId=order_id).count()

            if dada_order_count >= 1:
                dada_order_detail = DadaOrderDetail.objects.get(orderId=order_id)
                order_detail_data = DadaOrderDetailSerializer(dada_order_detail).data
            else:
                order_detail_data = {}
        except Exception as e:
            self.logger_error.error(str(e))
            order_detail_data = {}

        self.result = order_detail_data
        return self.result

    def update_dada_order_detail(self, order_id, detail_data):
        try:
            if DadaOrderDetail.objects.filter(orderId=order_id).count() == 0:
                self.create_dada_order_detail(detail_data)

            dada_order_detail = DadaOrderDetail.objects.get(orderId=order_id)
            detail_serializer = DadaOrderDetailSerializer(dada_order_detail, data=detail_data, partial=True)

            if not detail_serializer.is_valid():
                raise Exception(detail_serializer.errors)

            detail_serializer.save()
            order_detail_data = detail_serializer.data
        except Exception as e:
            self.logger_error.error(str(e))
            order_detail_data = {}

        self.result = order_detail_data
        return self.result

