from datetime import datetime


class DateUtils:
    @staticmethod
    def str_to_timestamp(time_str, format_str="%Y-%m-%d %H:%M:%S"):
        date_object = datetime.strptime(time_str, format_str)
        return int(date_object.timestamp())
