import json

from aries.purchases.models import Order, PurchaseOrder
from aries.purchases.serializers import OrderSerializer, PurchaseOrderSerializer

payment_dict = {}


def get_order_data(order):
    open_id = order['open_id']
    payment_data_list = payment_dict.get(open_id, [])
    order_id = order['order_id']
    purchase_order = PurchaseOrder.objects.get(id=order['purchase_order'])
    price_sub_total = purchase_order.price_sub_total
    price_delivery_fee = purchase_order.price_delivery_fee
    price_discount = purchase_order.price_discount
    price_total = purchase_order.price_total
    purchase_data = [
        order_id,
        str(purchase_order.delivery_date)[:10],
        price_sub_total,
        price_delivery_fee,
        price_discount,
        price_total
    ]
    payment_data_list.append(purchase_data)
    payment_dict[open_id] = payment_data_list
    return True


order_list = Order.objects.filter(order_status=10).order_by('id')
order_data = OrderSerializer(order_list, many=True).data

new_list = [get_order_data(order) for order in order_data]

print(len(order_data))

all_count = 0

file = open('purchase_info.txt', 'w')
for result in payment_dict.keys():
    target_list = payment_dict.get(result)
    purchase_count = str(len(target_list))
    all_count += int(purchase_count)
    for pay in target_list:
        file.write('{0},{1},{2},{3},{4},{5},{6}'.format(
            result, pay[0], pay[1], pay[2], pay[3], pay[4],  pay[5],
        ))
        file.write('\n')

file.close()


order_list = Order.objects.filter(order_status__lte=10).order_by('id')
purchase_order_list = list()
selling_count = 0

for order in order_list:
    if order.delivery_on_site:
        purchase_order_list.append(order.purchase_order)
for purchase_order in purchase_order_list:
    purchase_data = PurchaseOrderSerializer(purchase_order).data
    product_list = json.loads(purchase_data['product_list'])
    for product in product_list:
        product_id = product['product_id']
        if product_id == 45 or product_id == 46 or product_id == 124 or product_id == 125:
            selling_count += 1
print(selling_count)


file = open('purchase_info.txt', 'w')
start_date = '2018-04-01'
end_date = '2018-07-31'
status_list = [10, 11]
order_list_complete = Order.objects.filter(order_status__in=status_list, order_start_date__gte=start_date, order_start_date__lte=end_date).order_by('id')

for order in order_list_complete:
    purchase_order = PurchaseOrder.objects.get(order=order)
    price_sub_total = purchase_order.price_sub_total
    price_delivery_fee = purchase_order.price_delivery_fee
    price_discount = purchase_order.price_discount
    price_total = purchase_order.price_total
    delivery_split = order.delivery_time.split(',')
    delivery_date = delivery_split[0]
    delivery_time = delivery_split[1]
    delivery_address = order.delivery_address.replace(',', '.')
    write_str = '{},{},{},{},{},{},{},{},{},{},{}\n'.format(
        order.order_id,
        order.order_status,
        order.user_telephone,
        delivery_address,
        order.delivery_date,
        order.delivery_schedule,
        order.delivery_time,
        price_sub_total,
        price_delivery_fee,
        price_discount,
        price_total
    )
    file.write(write_str)
file.close()


"""
Purchase status 

상해 요청사항:
1~3 월 재구매율 vs 4~6월 재구매율
(월별) 총 구매건수 중에서 첫구매가 아닌 것들 / 총구매 건수
"""
import json
import datetime
from aries.purchases.models import Order, PurchaseOrder

lunching_date = datetime.date(2017, 9, 6)

start_date = datetime.date(2018, 6, 1)
end_date = datetime.date(2018, 6, 30)
target_order_list = Order.objects.filter(order_status=10, order_start_date__gte=start_date, order_start_date__lte=end_date).order_by('id')
all_order_count = target_order_list.count()
first_order_list = []
already_order_list = []
first_order_price = 0
already_order_price = 0
for order in target_order_list:
    open_id = order.open_id
    price_total = order.purchase_order.price_total
    check_order_qs = Order.objects.filter(order_status=10, order_start_date__lte=start_date, open_id=open_id)
    if check_order_qs.count() == 0:
        first_order_list.append(order)
        first_order_price += price_total
    else:
        already_order_list.append(order)
        already_order_price += price_total

first_order_price = round(first_order_price)
already_order_price = round(already_order_price)
first_order_count = len(first_order_list)
already_order_count = len(already_order_list)
first_order_ratio = round(first_order_count / all_order_count * 100, 2)
already_order_ratio = round(already_order_count / all_order_count * 100, 2)
all_order_price = round(first_order_price + already_order_price)
first_average_price = round(first_order_price/first_order_count)
already_average_price = round(already_order_price/already_order_count)
print(all_order_count, first_order_count, already_order_count, first_order_ratio, already_order_ratio)
print(all_order_price, first_order_price, first_average_price, already_order_price, already_average_price)
