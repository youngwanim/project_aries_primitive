from aries.common import code
from aries.common.exceptions.exceptions import BusinessLogicError
from aries.common.message_utils import message_mapper

from aries.users.service.user_receipt_service import UserReceiptService
from aries.users.service.user_service import UserService


class ReceiptManager:

    SIGN_UP_MSG_EN = 'You have got good friends who got you {} coupon just now!'
    SIGN_UP_MSG_CN = '你的好友刚刚为你赢得{}张优惠礼券！'

    REF_TARGET = 101

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.user_service = UserService(self.logger_info, self.logger_error)
        self.receipt_service = UserReceiptService(self.logger_info, self.logger_error)

    def create_user_receipt(self, user_open_id, user_receipt_data, cn_header):
        """
        Create user receipt
        :param user_open_id: User open id
        :param user_receipt_data: User receipt data to create
        :param cn_header: Language data
        :return: Created user and user receipt list json object
        """
        user_instance = self.user_service.get_user_instance(user_open_id)
        receipt_count = self.receipt_service.read_user_receipt_count(user_instance)

        if receipt_count >= 5:
            err_code = code.ERROR_1201_RECEIPT_LIMIT_ERROR
            err_msg = message_mapper.get(err_code, cn_header)
            raise BusinessLogicError(err_msg, err_code, None)

        receipt_data = self.receipt_service.create_user_receipt(user_instance, user_receipt_data)
        receipt_id = receipt_data['id']
        self.receipt_service.select_receipt(user_instance, receipt_id)
        return self.receipt_service.read_user_receipt(user_instance, cn_header)

    def read_user_receipt(self, user_open_id, cn_header=True):
        """
        Read user's receipt list
        :param user_open_id: User open id
        :param cn_header: User language header
        :return: User's receipt list json object
        """
        user_instance = self.user_service.get_user_instance(user_open_id)
        return self.receipt_service.read_user_receipt(user_instance, cn_header)

    def update_user_receipt(self, user_open_id, user_receipt_id, user_receipt_data, cn_header):
        """
        Update user's receipt data
        :param user_open_id: User open id
        :param user_receipt_id: Receipt id
        :param user_receipt_data: Receipt data for update
        :param cn_header: Language header info
        :return: Updated receipt json object
        """
        user_instance = self.user_service.get_user_instance(user_open_id)
        self.receipt_service.update_user_receipt(user_instance, user_receipt_id, user_receipt_data)

        return self.receipt_service.read_user_receipt(user_instance, cn_header)

    def delete_user_receipt(self, user_open_id, user_receipt_id, cn_header):
        """
        Delete user's receipt
        :param user_open_id: User open id
        :param user_receipt_id: User receipt id
        :param cn_header: Language header
        :return: Deleted number. Please check user's selected receipt issue
        """
        user_instance = self.user_service.get_user_instance(user_open_id)
        self.receipt_service.delete_user_receipt(user_instance, user_receipt_id)

        return self.receipt_service.read_user_receipt(user_instance, cn_header)

    def select_user_receipt(self, user_open_id, user_receipt_id):
        """
        Select user receipt
        :param user_open_id: User open id
        :param user_receipt_id: User receipt id
        :return: Selected receipt data
        """
        user_instance = self.user_service.get_user_instance(user_open_id)
        selected_id = self.receipt_service.select_receipt(user_instance, user_receipt_id)

        return selected_id
