from aries.common import code
from aries.common.models import ResultResponse
from aries.products.service.time_bomb_service import TimeBombService


class TimeBombManager:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

        self.result = ResultResponse(code.ARIES_200_SUCCESS, 'success')

    def get_time_bomb(self, time_bomb_id, lang_type, os_type):
        """
        Get time bomb data
        :param time_bomb_id: time bomb id
        :param lang_type: Language type. 0 - English, 1 - Chinese
        :param os_type: Language type. 0 - android, 1 - iOS, 2 - mobile web
        :return: time bomb json object data
        """
        time_bomb_service = TimeBombService(self.logger_info, self.logger_error)
        time_bomb = time_bomb_service.read_time_bomb_with_id(time_bomb_id, lang_type, os_type)

        return time_bomb

    def get_time_bomb_now(self, hub_id, os_type, has_after=True):
        """
        Check the current time bomb
        :param hub_id: target hub id
        :param os_type: os type
        :param has_after: default true, get time bomb after 30 minute
        :return: True if there is the time bomb, or False
        """
        time_bomb_service = TimeBombService(self.logger_info, self.logger_error)

        return time_bomb_service.get_current_time_bomb_after(hub_id, os_type, has_after)

    def get_time_bomb_list(self, hub_id):
        """
        Get the time bomb list
        :param hub_id: target hub id
        :return: time bomb list
        """
        time_bomb_service = TimeBombService(self.logger_info, self.logger_error)

        return time_bomb_service.read_time_bomb_list(hub_id)

    def get_time_bomb_with_id(self, time_bomb_id):
        """
        Get the time bomb detail
        :param time_bomb_id: target time bomb id
        :return: time bomb json object
        """
        time_bomb_service = TimeBombService(self.logger_info, self.logger_error)

        return time_bomb_service.read_time_bomb_with_id_admin(time_bomb_id)

    def set_time_bomb_activate_with_id(self, time_bomb_id, activate):
        """
        Set the time bomb to available
        :param time_bomb_id: target time bomb id
        :param activate: activation boolean value
        :return: result boolean value
        """
        time_bomb_service = TimeBombService(self.logger_info, self.logger_error)

        return time_bomb_service.set_time_bomb_activate(time_bomb_id, activate)

    def create_time_bomb(self, time_bomb, time_bomb_content_en, time_bomb_content_cn, discount_info):
        """
        Create a new time bomb
        :param time_bomb: time bomb json object data
        :param time_bomb_content_en: time bomb content english data
        :param time_bomb_content_cn: time bomb content chinese data
        :param discount_info: product discount info
        :return: time bomb json object
        """
        time_bomb_service = TimeBombService(self.logger_info, self.logger_error)

        return time_bomb_service.create_time_bomb(time_bomb, time_bomb_content_en,
                                                  time_bomb_content_cn, discount_info)

    def update_time_bomb(self, time_bomb_id, time_bomb, time_bomb_content_en, time_bomb_content_cn, discount_info):
        """
        Update a time bomb
        :param time_bomb_id: time bomb id
        :param time_bomb: time bomb json object data
        :param time_bomb_content_en: time bomb content english data
        :param time_bomb_content_cn: time bomb content chinese data
        :param discount_info: product discount info
        :return: time bomb json object
        """
        time_bomb_service = TimeBombService(self.logger_info, self.logger_error)

        return time_bomb_service.update_time_bomb(time_bomb_id, time_bomb, time_bomb_content_en,
                                                  time_bomb_content_cn, discount_info)

    def delete_time_bomb(self, time_bomb_id):
        """
        Delete a time bomb
        :param time_bomb_id: target time bomb id
        :return: true or false
        """
        time_bomb_service = TimeBombService(self.logger_info, self.logger_error)

        return time_bomb_service.delete_time_bomb(time_bomb_id)

    def check_time_bomb_exists(self, time_bomb_id):
        """
        Check time bomb exists
        :param time_bomb_id: target time bomb id
        :return: true or false
        """
        time_bomb_service = TimeBombService(self.logger_info, self.logger_error)

        return time_bomb_service.check_time_bomb_with_id(time_bomb_id)
