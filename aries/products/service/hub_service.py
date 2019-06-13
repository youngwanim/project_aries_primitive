from aries.common.exceptions.exceptions import BusinessLogicError
from aries.products.models import Hub
from aries.products.serializers import HubSerializer


class HubService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def read_hub_instance_with_id(self, hub_id):
        try:
            hub = Hub.objects.get(code=hub_id)
        except Exception as e:
            msg = '[HubService][read_hub_instance_with_id][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return hub

    def read_hub_list_with_status(self, status, target_db='default'):
        try:
            hubs = Hub.objects.using(target_db).filter(status=status)
            hub_data = HubSerializer(hubs, many=True).data
        except Exception as e:
            msg = '[HubService][read_hub_list_with_status][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return hub_data

    def read_hub_list(self, target_db='default'):
        try:
            hubs = Hub.objects.using(target_db).filter(status__lte=1).order_by('id', '-status')
            hub_data = HubSerializer(hubs, many=True).data
        except Exception as e:
            msg = '[HubService][read_hub_list][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return hub_data
