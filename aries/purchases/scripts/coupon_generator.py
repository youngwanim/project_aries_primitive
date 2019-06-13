import uuid
from aries.purchases.models import EventCoupon, CustomerCoupon, Coupon

file = open('jd_coupon.txt', 'w')

for count in range(40):
    random = str(uuid.uuid4()).upper().replace("-", "")
    coupon_serial = random[:8]
    print(coupon_serial)
    EventCoupon.objects.create(
        name='JD FINANCE VIP COUPON',
        event_type=0,
        coupon_id=17,
        coupon_count=1,
        coupon_code='20171117_JD',
        serial_number=coupon_serial
    )
    file.write(coupon_serial + '\n')

file.close()


"""
Attendance coupon script
"""
file = open('attend_coupon.txt', 'r')

coupon_one = Coupon.objects.get(id=25)
coupon_two = Coupon.objects.get(id=26)
coupon_three = Coupon.objects.get(id=27)

for index in range(40):
    read_line = file.readline()
    split_str = read_line.split(',')

    open_id = split_str[0]
    attendance_count = int(split_str[1])

    if attendance_count == 7:
        CustomerCoupon.objects.create(coupon=coupon_three, coupon_code='ATTEND_201802', open_id=open_id, issued_date='2018-02-22', start_date='2018-02-22', end_date='2018-04-21', sender_id='VIASTELLE_ADMIN', status=0)
    elif 3 <= attendance_count <= 6:
        CustomerCoupon.objects.create(coupon=coupon_two, coupon_code='ATTEND_201802', open_id=open_id, issued_date='2018-02-22', start_date='2018-02-22', end_date='2018-04-21', sender_id='VIASTELLE_ADMIN', status=0)
    elif 1 <= attendance_count <= 2:
        CustomerCoupon.objects.create(coupon=coupon_one, coupon_code='ATTEND_201802', open_id=open_id, issued_date='2018-02-22', start_date='2018-02-22', end_date='2018-04-21', sender_id='VIASTELLE_ADMIN', status=0)


"""
Member order count script
"""
from aries.purchases.models import Order
read_file = open('user_os_info.txt', 'r')
write_file = open('user_order_info.txt', 'w')
while True:
    line = read_file.readline()
    if not line:
        break
    split_line = line.split(',')
    open_id = split_line[0]
    mdn = split_line[1]
    os_type = split_line[2].replace('\n', '')
    order_count = Order.objects.filter(open_id=open_id, order_status=10).count()
    write_file.write(open_id + ',' + mdn + ',' + os_type + ',' + str(order_count) + '\n')
read_file.close()
write_file.close()
