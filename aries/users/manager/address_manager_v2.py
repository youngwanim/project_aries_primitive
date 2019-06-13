from aries.users.service.user_address_service import UserAddressService
from aries.users.service.user_service import UserService


class AddressManagerV2:
    ADDRESS_LIMIT = 7

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

    def create_address(self, open_id, address_data):
        user_service = UserService(self.logger_info, self.logger_error)
        user_instance = user_service.get_user_instance(open_id)

        address_service = UserAddressService(self.logger_info, self.logger_error)

        if address_data['delivery_area']:
            address_service.deselect_address(user_instance)

        user_address_data = address_service.create_address(user_instance, address_data)

        # Address count check and delete address
        address_count = address_service.read_address_count(user_instance)

        if address_count > self.ADDRESS_LIMIT:
            address_service.delete_old_address(user_instance)

        # If address can delivery, address setting
        if user_address_data['delivery_area']:
            hub_id = user_address_data['hub_id']
            address_id = user_address_data['id']

            user_service.set_delivery_address(user_instance, hub_id, address_id, user_address_data)

        return user_address_data

    def get_address(self, open_id, address_id):
        user_service = UserService(self.logger_info, self.logger_error)
        user_instance = user_service.get_user_instance(open_id)

        address_service = UserAddressService(self.logger_info, self.logger_error)
        address = address_service.read_address(user_instance, address_id)

        return address

    def get_address_list(self, open_id):
        user_service = UserService(self.logger_info, self.logger_error)
        user_instance = user_service.get_user_instance(open_id)

        address_service = UserAddressService(self.logger_info, self.logger_error)
        address_list = address_service.read_address_list(user_instance)

        return address_list

    def update_address(self, open_id, address_id, address_data):
        user_service = UserService(self.logger_info, self.logger_error)
        user_instance = user_service.get_user_instance(open_id)

        # Check delivery area
        if 'delivery_area' in address_data:
            adr_delivery_area = address_data['delivery_area']
        else:
            adr_delivery_area = False

        # Update address and select check
        if 'selected_address' in address_data:
            selected_address = address_data['selected_address']
            del address_data['selected_address']
        else:
            selected_address = False

        # User information overwrite check
        if 'overwrite_user_name' not in address_data:
            address_data['overwrite_user_name'] = False

        address_service = UserAddressService(self.logger_info, self.logger_error)
        updated_address = address_service.update_address(user_instance, int(address_id), address_data)

        # After update address, select address id
        if selected_address and adr_delivery_area:
            address_service.deselect_address(user_instance)
            address_service.select_address(user_instance, address_id)
            user_service.set_delivery_address(user_instance, updated_address['hub_id'], address_id, updated_address)

        # If not delivery area, select next address or None selected
        if selected_address and not adr_delivery_area:
            address_service.deselect_address(user_instance)
            next_address_id = address_service.read_latest_possible_adr(user_instance)

            if next_address_id != 0:
                address_service.select_address(user_instance, next_address_id)
            else:
                user_service.set_delivery_none(user_instance)

        return updated_address

    def delete_address(self, open_id, address_id):
        user_service = UserService(self.logger_info, self.logger_error)
        user_instance = user_service.get_user_instance(open_id)

        address_service = UserAddressService(self.logger_info, self.logger_error)
        user_address_data = address_service.delete_address(user_instance, int(address_id))

        # If address has changed
        if user_address_data is not None:
            hub_id = user_address_data['hub_id']
            address_id = user_address_data['id']

            user_data = user_service.set_delivery_address(user_instance, hub_id, address_id, user_address_data)

            current_delivery_type = user_data['current_delivery_type']
            default_address = user_data['default_address']
            default_address_id = user_data['default_address_id']
            default_recipient_name = user_data['default_recipient_name']
            default_recipient_mdn = user_data['default_recipient_mdn']
        else:
            # If user address data is none, get a new user instance
            user_instance = user_service.get_user_instance(open_id)
            current_delivery_type = user_instance.current_delivery_type
            default_address = user_instance.default_address
            default_address_id = user_instance.default_address_id
            default_recipient_name = user_instance.default_recipient_name
            default_recipient_mdn = user_instance.default_recipient_mdn

        result = {
            'current_delivery_type': current_delivery_type,
            'default_address': default_address,
            'default_address_id': default_address_id,
            'default_recipient_name': default_recipient_name,
            'default_recipient_mdn': default_recipient_mdn
        }

        return result

    def select_address(self, open_id, address_id):
        user_service = UserService(self.logger_info, self.logger_error)
        user_instance = user_service.get_user_instance(open_id)

        address_service = UserAddressService(self.logger_info, self.logger_error)

        # Deselect address
        address_service.deselect_address(user_instance)

        # Select delivery address
        address_service.select_address(user_instance, address_id)
        user_address_data = address_service.read_address(user_instance, address_id)
        hub_id = user_address_data['hub_id']
        user_service.set_delivery_address(user_instance, hub_id, address_id, user_address_data)

        address_list = address_service.read_address_list(user_instance)

        return address_list

    def select_hub(self, open_id, cn_header, hub_id):
        user_service = UserService(self.logger_info, self.logger_error)
        user_instance = user_service.get_user_instance(open_id)

        address_service = UserAddressService(self.logger_info, self.logger_error)

        # Deselect addresses
        address_service.deselect_address(user_instance)

        # Select on site pickup
        user_service.set_delivery_pick_up(user_instance, cn_header, hub_id)

        address_list = address_service.read_address_list(user_instance)

        return address_list
