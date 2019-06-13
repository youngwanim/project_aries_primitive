import json

from aries.users.common.address_func import get_pickup_hub
from aries.users.models import UserLoginInfo, User, UserInfo, UserNotifyInfo, ShoppingBag
from aries.users.serializers import UserSerializer, UserAccountSerializer, UserShoppingBagSerializer


class UserService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def get_login_info_with_key_value(self, login_key, login_value):
        try:
            login_info = UserLoginInfo.objects.get(login_key=login_key, login_value=login_value)
            if login_info.count() == 0:
                raise Exception
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = login_info

        return self.result

    def get_login_info_with_sns_open_id(self, login_sns_open_id):
        try:
            login_info = UserLoginInfo.objects.get(login_sns_open_id=login_sns_open_id)
            if login_info.count() == 0:
                raise Exception
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = login_info

        return self.result

    def get_login_info_with_mdn(self, mdn):
        try:
            login_info = UserLoginInfo.objects.get(mdn=mdn)
            if login_info.count() == 0:
                raise Exception
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = login_info

        return self.result

    def get_user_instance(self, open_id):
        try:
            user_qs = User.objects.filter(open_id=open_id)
            if user_qs.count() == 1:
                user_instance = User.objects.get(open_id=open_id)
            else:
                user_instance = None
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_instance
        return self.result

    def get_user_data_with_ins(self, user_instance):
        try:
            user_data = UserSerializer(user_instance).data
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_data

        return self.result

    def get_user_info_with_ins(self, user_instance):
        try:
            user_info = UserInfo.objects.get(user=user_instance)
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_info

        return self.result

    def get_user_notify_info(self, user_instance):
        try:
            user_notify_info = UserNotifyInfo.objects.get(user=user_instance)
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_notify_info

        return self.result

    def get_user_cart_info(self, user_instance):
        try:
            cart_info = ShoppingBag.objects.get(user=user_instance)
            cart_info_data = UserShoppingBagSerializer(cart_info).data
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = cart_info_data

        return self.result

    def set_delivery_address(self, user_instance, hub_id, address_id, user_address):
        try:
            user_address_detail = user_address['detail']

            if len(user_address_detail) == 0:
                address_detail = user_address['name']
            else:
                address_detail = user_address['name'] + ' - ' + user_address_detail

            default_address = address_detail
            default_recipient_name = user_address['recipient_name']
            default_recipient_mdn = user_address['recipient_mdn']

            # Delivery setting
            user_instance.current_delivery_type = 0
            user_instance.default_hub_id = hub_id
            user_instance.default_address_id = address_id
            user_instance.default_address = default_address
            user_instance.default_recipient_name = default_recipient_name
            user_instance.default_recipient_mdn = default_recipient_mdn

            # Pickup hub setting
            user_instance.default_pickup_hub_id = 0
            user_instance.default_pickup_hub = ''

            # Save user instance
            user_instance.save()

            user_data = UserAccountSerializer(user_instance).data
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_data

        return self.result

    def set_delivery_pick_up(self, user_instance, cn_header, hub_id):
        try:
            # Delivery setting
            user_instance.current_delivery_type = 1
            user_instance.default_hub_id = hub_id
            user_instance.default_address_id = 0
            user_instance.default_address = ''
            user_instance.default_recipient_name = ''
            user_instance.default_recipient_mdn = ''

            # Pickup hub setting
            user_instance.default_pickup_hub_id = hub_id
            user_instance.default_pickup_hub = get_pickup_hub(cn_header, hub_id)

            # Save user instance
            user_instance.save()
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = True

        return self.result

    def set_delivery_none(self, user_instance):
        try:
            # Delivery setting
            user_instance.current_delivery_type = 1
            user_instance.default_address_id = 0
            user_instance.default_address = ''
            user_instance.default_recipient_name = ''
            user_instance.default_recipient_mdn = ''

            # Save user instance
            user_instance.save()
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = True

        return self.result

    def set_user_cart_info(self, user_cart_info, include_cutlery, special_inst=None):
        try:
            cart_info = ShoppingBag.objects.get(id=user_cart_info['id'])
            cart_info.include_cutlery = include_cutlery

            if special_inst is not None:
                inst_list = [item for item in user_cart_info['instruction_history']]

                if len(inst_list) >= 3:
                    inst_list[2] = inst_list[1]
                    inst_list[1] = inst_list[0]
                    inst_list[0] = special_inst
                else:
                    inst_list.insert(0, special_inst)

                cart_info.instruction_history = json.dumps(inst_list)

            cart_info.save()
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = True

        return self.result
