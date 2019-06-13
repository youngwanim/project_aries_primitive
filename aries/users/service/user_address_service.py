from aries.users.models import UserAddressInfo
from aries.users.serializers import UserAddressManagerSerializer, UserAddressInformationSerializer


class UserAddressService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def create_address(self, user_instance, address_data):
        """
        Create a new address
        :param user_instance: User object
        :param address_data: Address data
        :return: User address json data
        """
        try:
            address_data['user'] = user_instance

            # Check recipient name and mdn, fill it automatically
            if 'recipient_name' not in address_data:
                address_data['recipient_name'] = ''

            if 'recipient_mdn' not in address_data:
                address_data['recipient_mdn'] = ''

            if len(address_data['recipient_name']) == 0:
                address_data['recipient_name'] = user_instance.name

            if len(address_data['recipient_mdn']) == 0 and user_instance.mdn_verification:
                address_data['recipient_mdn'] = user_instance.mdn

            # Check overwrite user name field and delete
            if address_data['overwrite_user_name']:
                user_instance.name = address_data['recipient_name']
                user_instance.save()

            del address_data['overwrite_user_name']

            # Create user address object
            user_address = UserAddressInfo.objects.create(**address_data)

            if address_data['delivery_area']:
                user_address.selected_address = True
                user_address.save()
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = UserAddressManagerSerializer(user_address).data

        return self.result

    def read_address(self, user_instance, address_id):
        """
        Get address json object
        :param user_instance: User object
        :param address_id: Address id
        :return: Address json object
        """
        try:
            user_address = UserAddressInfo.objects.get(user=user_instance, id=address_id)
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = UserAddressManagerSerializer(user_address).data

        return self.result

    def read_address_list(self, user_instance):
        """
        Get address list from user object
        :param user_instance: User object
        :return: Address json object list
        """
        try:
            user_address_qs = UserAddressInfo.objects.filter(user=user_instance).order_by(
                '-delivery_area', '-selected_address', '-id')
            address_serializer = UserAddressManagerSerializer(user_address_qs, many=True)
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = address_serializer.data

        return self.result

    def read_address_count(self, user_instance):
        """
        Get user's address count
        :param user_instance: User object
        :return: The number of user's address count
        """
        try:
            self.result = UserAddressInfo.objects.filter(user=user_instance).count()
        except Exception as e:
            self.logger_info.info(str(e))

        return self.result

    def read_latest_possible_adr(self, user_instance):
        """
        Get user's latest possible address id
        :param user_instance:
        :return:
        """
        try:
            count = UserAddressInfo.objects.filter(user=user_instance, delivery_area=True).count()

            if count == 0:
                self.result = 0
            else:
                user_address = UserAddressInfo.objects.filter(user=user_instance, delivery_area=True).latest('id')
                self.result = user_address.id
        except Exception as e:
            self.logger_info.info(str(e))

        return self.result

    def update_address(self, user_instance, address_id, address_data):
        """
        Update user's address detail
        :param user_instance: User object
        :param address_id: Address id
        :param address_data: Updated data
        :return: Updated address data
        """
        try:
            # Check overwrite user name field and delete
            if address_data['overwrite_user_name']:
                user_instance.name = address_data['recipient_name']
                user_instance.save()

            del address_data['overwrite_user_name']

            user_address = UserAddressInfo.objects.get(user=user_instance, id=address_id)
            address_serializer = UserAddressInformationSerializer(user_address, data=address_data, partial=True)

            if not address_serializer.is_valid():
                raise Exception(address_serializer.errors)

            address_serializer.save()
            updated_address_data = address_serializer.data
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = updated_address_data

        return self.result

    def select_address(self, user_instance, address_id):
        """
        Select selected address
        :param user_instance: User object
        :param address_id: Address id
        :return: None
        """
        try:
            user_address = UserAddressInfo.objects.get(user=user_instance, id=address_id)
            user_address.selected_address = True
            user_address.save()
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = True

        return self.result

    def deselect_address(self, user_instance):
        """
        Deselect selected address
        :param user_instance: User object
        :return: None
        """
        try:
            # Deselect all address to none selected status
            user_address_qs = UserAddressInfo.objects.filter(user=user_instance, selected_address=True)

            for user_adr in user_address_qs:
                user_adr.selected_address = False
                user_adr.save()
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = True

        return self.result

    def delete_old_address(self, user_instance):
        """
        Delete old address with non-selected address
        :param user_instance: User object
        :return: None
        """
        try:
            user_address = UserAddressInfo.objects.filter(user=user_instance, selected_address=False).latest('-id')
            user_address.delete()
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = True

        return self.result

    def delete_address(self, user_instance, address_id):
        """
        Delete address
        :param user_instance: User object
        :param address_id: Address id
        :return: Newly selected user address data
        """
        try:
            user_address = UserAddressInfo.objects.get(user=user_instance, id=address_id)
            is_selected_address = user_address.selected_address
            user_address.delete()

            # If a deleted address was selected, latest address select
            if is_selected_address:
                address_count = UserAddressInfo.objects.filter(
                    user=user_instance, selected_address=False, delivery_area=True).count()

                if address_count >= 1:
                    user_adr = UserAddressInfo.objects.filter(
                        user=user_instance, selected_address=False, delivery_area=True).latest('-id')
                    user_adr.selected_address = True
                    user_adr.save()
                    user_address_data = UserAddressInformationSerializer(user_adr).data
                else:
                    user_instance.current_delivery_type = -1
                    user_instance.default_address_id = 0
                    user_instance.default_address = ''
                    user_instance.default_recipient_name = ''
                    user_instance.default_recipient_mdn = ''
                    user_instance.default_hub_id = 1
                    user_instance.save()
                    user_address_data = None
            else:
                user_address_data = None

        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_address_data

        return self.result
