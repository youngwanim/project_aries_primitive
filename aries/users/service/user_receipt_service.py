from aries.users.models import UserReceipt
from aries.users.serializers import UserReceiptSerializer


class UserReceiptService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def read_user_receipt_count(self, user_instance):
        """
        Read user receipt count
        :param user_instance: User instance
        :return: receipt count
        """
        try:
            receipt_count = UserReceipt.objects.filter(user=user_instance).count()
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = receipt_count

        return self.result

    def create_user_receipt(self, user_instance, user_receipt_data):
        """
        Create user receipt
        :param user_instance: User instance
        :param user_receipt_data: Receipt data to create
        :return: Created user receipt data
        """
        try:
            user_receipt_data['user'] = user_instance
            user_receipt = UserReceipt.objects.create(**user_receipt_data)
            user_receipt_data = UserReceiptSerializer(user_receipt).data
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_receipt_data

        return self.result

    def read_user_receipt(self, user_instance, cn_header=True):
        """
        Read user receipt
        :param user_instance: User object
        :param cn_header: Default is true
        :return: User receipt json object
        """
        try:
            user_receipt_qs = UserReceipt.objects.filter(user=user_instance)
            user_receipt_list = UserReceiptSerializer(user_receipt_qs, many=True).data

            company_type = 0

            if cn_header:
                personal = '个人'
            else:
                personal = 'PERSONAL'

            for receipt in user_receipt_list:
                del receipt['user']

                if receipt['type'] == company_type:
                    receipt['formatted_name'] = receipt['name'] + ' / ' + receipt['tax_id_number']
                else:
                    if len(receipt['name']) == 0:
                        receipt['formatted_name'] = personal
                    else:
                        receipt['formatted_name'] = personal + ' / ' + receipt['name']

        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_receipt_list

        return self.result

    def update_user_receipt(self, user_instance, user_receipt_id, user_receipt_data):
        """
        Update user receipt object.
        :param user_instance: User object
        :param user_receipt_id: User receipt id
        :param user_receipt_data: Update content
        :return: Updated receipt data
        """
        try:
            user_receipt = UserReceipt.objects.get(id=user_receipt_id, user=user_instance)
            receipt_serializer = UserReceiptSerializer(user_receipt, data=user_receipt_data, partial=True)

            if not receipt_serializer.is_valid():
                raise Exception(receipt_serializer.errors)

            receipt_serializer.save()
            update_receipt_data = receipt_serializer.data
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = update_receipt_data

        return self.result

    def delete_user_receipt(self, user_instance, user_receipt_id):
        """
        Delete User receipt object.
        :param user_instance: User instance
        :param user_receipt_id: The number of user receipt id to delete
        :return: Deleted receipt id.
        """
        try:
            user_receipt = UserReceipt.objects.get(id=user_receipt_id, user=user_instance)

            if user_receipt.selected:
                user_instance.default_receipt_id = 0
                user_instance.save()

            user_receipt.delete()
        except Exception as e:
            self.logger_info.info(str(e))
        else:
            self.result = user_receipt_id

        return self.result

    def select_receipt(self, user_instance, receipt_id):
        """
        Select receipt id. If receipt id is 0, deselect all receipt.
        :param user_instance: User instance
        :param receipt_id: The number of select receipt
        :return: selected receipt id
        """
        try:
            receipt_qs = UserReceipt.objects.filter(user=user_instance)
            for receipt in receipt_qs:
                receipt.selected = False
                receipt.save()

            if receipt_id == 0:
                user_instance.default_receipt_id = 0
                user_instance.default_receipt = ''
                user_instance.save()

                receipt_id = 0
            else:
                receipt = UserReceipt.objects.get(user=user_instance, id=receipt_id)
                receipt.selected = True
                receipt.save()

                user_instance.default_receipt_id = receipt_id

                name = receipt.name
                tax_num = receipt.tax_id_number

                if len(tax_num) <= 0:
                    default_receipt = name
                else:
                    default_receipt = name + ' / ' + tax_num

                user_instance.default_receipt = default_receipt
                user_instance.save()
        except Exception as e:
            print(str(e))
            self.logger_info.info(str(e))
        else:
            self.result = receipt_id

        return self.result
