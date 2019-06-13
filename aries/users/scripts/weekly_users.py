import datetime
import json

from aries.users.models import UserInfo, User

"""
Weekly user statics
"""
first_time = datetime.datetime(2017, 9, 1, 0, 0)
user_count_list = []

for index in range(13):
    second_time = first_time + datetime.timedelta(days=7) - datetime.timedelta(minutes=1)
    user_count = UserInfo.objects.filter(date_of_register__gte=str(first_time)[:10], date_of_register__lte=str(second_time)[:10]).count()
    user_count_list.append(str(first_time)[:10] + ' ~ ' + str(second_time)[:10] + ' : ' + str(user_count))
    first_time = second_time + datetime.timedelta(minutes=1)


"""

"""
file = open('back_to_office.txt', 'w')
all_user_qs = User.objects.all()
for user in all_user_qs:
    file.write(user.open_id + '\n')
file.close()

"""
User information
"""
file = open('attend_coupon.txt', 'r')
information_file = open('user_information.txt', 'w')

for count in range(10):
    read_line = file.readline()
    split_str = read_line.split(',')
    open_id = split_str[0]

    user = User.objects.get(open_id=open_id)
    user_data = {'open_id': open_id, 'mdn': user.mdn, 'mdn_verification': user.mdn_verification}
    information_file.write(json.dumps(user_data) + '\n')


"""
User information for sms
"""
read_file = open('mdn_list_0504.csv', 'r')
write_file = open('user_os_info.txt', 'w')

while True:
    line = read_file.readline()
    if not line:
        break
    split_line = line.split(',')
    open_id = split_line[0]
    mdn = split_line[1].replace('\n', '')
    user = User.objects.get(open_id=open_id)
    user_info = UserInfo.objects.get(user=user)
    if user_info.os_type == -1:
        os_type = 'wechat_public'
    elif user_info.os_type == 0:
        os_type = 'android'
    elif user_info.os_type == 1:
        os_type = 'ios'
    else:
        os_type = 'unknown'
    write_file.write(open_id + ',' + mdn + ',' + os_type + '\n')

read_file.close()
write_file.close()
