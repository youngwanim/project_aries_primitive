from datetime import datetime
import time


def get_timestamp():
    return int(time.time())


def get_yyyymmdd_now():
    current_date = datetime.strptime((str(datetime.now())[:-10]), '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %I:%M %p')
    split_date = current_date.split(' ')
    date = split_date[0]
    time = split_date[1]
    time_detail = split_date[2]

    date_split = date.split('-')
    if date_split[1][0] == '0':
        date_split[1] = date_split[1][1:]
    if date_split[2][0] == '0':
        date_split[2] = date_split[2][1:]

    date = date_split[0] + '. ' + date_split[1] + '. ' + date_split[2]

    if time[0] == '0':
        time = time[1:]

    return date + ' ' + time + ' ' + time_detail


def get_yymmdd_time(current_datetime):
    split_date = current_datetime.split(' ')
    date = split_date[0]
    time = split_date[1]
    time_detail = split_date[2]

    time_split = time.split(':')
    if time_split[0][0] == '0':
        time_split[0] = time_split[0][1:]

    time_merge = time_split[0] + ':' + time_split[1]

    return date.replace('-', '.') + ' ' + time_merge + ' ' + time_detail


def get_yymmdd_with_ampm(current_datetime):
    split_data = current_datetime.split('T')
    ymd = split_data[0]
    hour = split_data[1]

    ymd = ymd.replace('-', '.') + ', '
    hour = int(hour[:2])

    if hour > 12:
        hour -= 12
        new_hour = str(hour) + 'PM'
    else:
        new_hour = str(hour) + 'AM'

    ymd += new_hour

    return ymd


def get_ordering_date_fmt():
    current_date = datetime.strptime((str(datetime.now())[:-10]), '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %I:%M %p')
    split_date = current_date.split(' ')
    date = split_date[0]
    time = split_date[1]
    time_detail = split_date[2]

    date_split = date.split('-')
    if date_split[1][0] == '0':
        date_split[1] = date_split[1][1:]
    if date_split[2][0] == '0':
        date_split[2] = date_split[2][1:]

    date = date_split[0] + '. ' + date_split[1] + '. ' + date_split[2]

    if time[0] == '0':
        time = time[1:]

    return date + ' ' + time + ' ' + time_detail


def get_ordering_complete_date_fmt(date_time):
    current_date = str(date_time)
    return current_date


def get_yyyy_mm_dd_now():
    current_date = datetime.now()
    return str(current_date)[:10]


def get_order_status_history(status):
    history = {'status': status, 'datetime': get_ordering_date_fmt()}
    return history


def str_to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()
