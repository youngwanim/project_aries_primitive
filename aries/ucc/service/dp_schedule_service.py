from aries.ucc.models import DisplaySchedule
from aries.ucc.serializers import DisplayScheduleSerializer


class DisplayScheduleService:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.result = None

    def create_dp_schedule(self, dp_schedule_data):
        try:
            schedule_instance = DisplaySchedule.objects.create(**dp_schedule_data)
            schedule_data = DisplayScheduleSerializer(schedule_instance).data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = schedule_data

        return self.result

    def read_dp_schedule(self, schedule_id):
        try:
            schedule_instance = DisplaySchedule.objects.get(id=schedule_id)
            schedule_data = DisplayScheduleSerializer(schedule_instance).data
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = schedule_data

        return self.result

    def update_dp_schedule(self, schedule_id, dp_schedule_data):
        try:
            schedule_instance = DisplaySchedule.objects.get(id=schedule_id)
            serializer = DisplayScheduleSerializer()
            serializer.update(schedule_instance, dp_schedule_data)
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = serializer.data

        return self.result

    def delete_dp_schedule(self, schedule_id):
        try:
            schedule_instance = DisplaySchedule.objects.get(id=schedule_id)
            schedule_instance.delete()
        except Exception as e:
            self.logger_error.error(str(e))
        else:
            self.result = True

        return self.result
