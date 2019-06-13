from aries.common.exceptions.exceptions import BusinessLogicError
from aries.products.models import MenuReviewStatics, Menu, HubStock
from aries.products.serializers import MenuReviewStaticsSerializer, MenuListInfoSerializer


class MenuService:

    def __init__(self, logger_info, logger_error, target_db='default'):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.target_db = target_db
        self.result = None

    def read_menu_data_with_id(self, menu_id):
        try:
            menu_instance = Menu.objects.using(self.target_db).get(id=menu_id)
            menu_data = MenuListInfoSerializer(menu_instance).data
        except Exception as e:
            msg = '[MenuService][read_menu_instance][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return menu_data

    def read_menu_instance(self, menu_id):
        try:
            menu_instance = Menu.objects.using(self.target_db).get(id=menu_id)
        except Exception as e:
            msg = '[MenuService][read_menu_instance][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return menu_instance

    def read_menu_data(self, menu_instance):
        try:
            menu_data = MenuListInfoSerializer(menu_instance).data
        except Exception as e:
            msg = '[MenuService][read_menu_data][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return menu_data

    def read_menu_statics_data(self, menu_data):
        statics_data = {
            'average_point': 0.0,
            'review_count': 0,
            'review_count_postfix': ''
        }

        try:
            statics_count = MenuReviewStatics.objects.filter(menu=menu_data['id']).count()

            if statics_count == 1:
                statics = MenuReviewStatics.objects.get(menu=menu_data['id'])
                statics_data = MenuReviewStaticsSerializer(statics).data
        except Exception as e:
            msg = '[MenuService][read_menu_statics_data][' + str(e) + ']'
            self.logger_error.error(msg)

        result = statics_data

        return result

    def read_hub_stock_instance(self, hub_instance, menu_instance):
        try:
            hub_stock_instance = HubStock.objects.get(hub=hub_instance, menu=menu_instance)
        except Exception as e:
            msg = '[MenuService][read_hub_stock_instance][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return hub_stock_instance

    def read_menu_statics(self, menu_id):
        try:
            statics_count = MenuReviewStatics.objects.filter(menu=menu_id).count()
            if statics_count >= 1:
                statics = MenuReviewStatics.objects.get(menu=menu_id)
                statics_data = MenuReviewStaticsSerializer(statics).data
                result = statics_data
            else:
                result = {
                    'average_point': 0.0,
                    'review_count': 0,
                    'review_count_postfix': ''
                }
        except Exception as e:
            msg = '[MenuService][read_menu_statics][' + str(e) + ']'
            self.logger_error.error(msg)
            raise BusinessLogicError(msg, None, None)

        return result
