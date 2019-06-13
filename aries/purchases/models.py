from django.db import models

PURCHASE_ORDER_STATUS_TYPE = (
    (0, 'Creation complete'),
    (1, 'Order complete(Sync)'),
    (2, 'Order complete(Async)'),
    (3, 'Order complete(sync/async)'),
    (5, 'Canceled (refund success)'),
    (6, 'Canceled (refund failure)'),
    (7, 'Order expired'),
)


ORDER_STATUS_TYPE = (
    (0, 'Complete order'),
    (1, 'Preparing food'),
    (2, 'On delivering'),
    (10, 'Delivery complete'),
    (11, 'Order canceled(User)'),
    (12, 'Order canceled(Server)'),
)

OPERATION_STATUS_TYPE = (
    (0, 'Start preparing'),
    (1, 'Start packaging'),
    (2, 'Packaging done'),
    (3, 'Delivery waiting'),
    (4, 'Delivery taken'),
    (5, 'Delivering'),
    (6, 'Delivery complete'),
    (10, 'Canceled'),
)

PAYMENT_TYPE = (
    (0, 'ALIPAY App'),
    (1, 'WECHAT App'),
    (2, 'ALIPAY Mobile'),
    (3, 'WECHAT Mobile'),
)

SHIPPING_METHOD = (
    (0, 'VIASTELLE SHIPPING'),
    (1, 'DADA'),
)

CustomerCouponType = {
    (0, 'Not used'),
    (1, 'Used'),
    (2, 'Expired')
}

PromotionStatus = {
    (0, 'Stop'),
    (1, 'On going'),
    (2, 'Period expired')
}

PROMOTION_EVENT_TYPE = {
    (0, 'ONLY ONE ISSUE'),
    (1, 'INFINITE ISSUE'),
    (2, 'LIMITATION ISSUE')
}

AUTOMATIC_COUPON_ISSUE_TYPE = {
    (0, 'ALL MEMBER'),
    (1, 'EVENT CONDITION'),
}


# Orders domain
class PurchaseOrder(models.Model):
    created_date = models.DateTimeField(null=False)
    status = models.IntegerField(default=0, null=True, choices=PURCHASE_ORDER_STATUS_TYPE)
    order_id = models.CharField(max_length=200, null=False)
    order_hash = models.CharField(max_length=256, null=False)
    hub_id = models.IntegerField(null=False)
    phase_next_day = models.BooleanField(default=False, null=False)
    sales_time = models.IntegerField(default=0, blank=True, null=True)
    open_id = models.CharField(max_length=64, null=False)
    user_name = models.CharField(max_length=32, null=False)
    user_telephone = models.CharField(max_length=32, null=False)
    user_receipt = models.CharField(default='', max_length=100, null=True, blank=True)
    # if true, user_extra_telephone data should be set, legacy field
    extra_telephone_usage = models.BooleanField(default=False)
    extra_telephone = models.CharField(max_length=32, default='', null=True, blank=True)
    # Delivery domain
    delivery_on_site = models.BooleanField(default=False, blank=True)
    delivery_address_id = models.IntegerField(null=False)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_schedule = models.IntegerField(null=False)
    delivery_as_fast = models.BooleanField(default=False)
    delivery_start_time = models.CharField(default='', max_length=20, null=False)
    delivery_end_time = models.CharField(default='', max_length=20, null=False)
    shipping_method = models.IntegerField(default=0, null=True, blank=True)
    shipping_detail = models.TextField(default='', null=True, blank=True)
    shipping_name = models.CharField(max_length=32, null=True, blank=True)
    shipping_cost = models.FloatField(default=0.0, null=False)
    # Payment domain
    payment_type = models.IntegerField(null=False, choices=PAYMENT_TYPE)
    product_title = models.CharField(max_length=100, null=True, blank=True)
    product_sub = models.CharField(max_length=50, null=True, blank=True)
    # contains product id, name, count, price
    product_list = models.TextField(null=False)
    order_details = models.TextField(null=False)
    # contains related-specific customer coupon id
    coupon_list = models.TextField(null=False, blank=True)
    price_unit = models.IntegerField(default=0, null=False)
    price_sub_total = models.FloatField(null=False)
    price_delivery_fee = models.FloatField(null=False)
    price_discount = models.FloatField(null=False)
    price_total = models.FloatField(null=False)
    # Misc domain
    special_instruction = models.CharField(max_length=200, default='', null=True, blank=True)
    include_cutlery = models.BooleanField(default=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order_id) + ' - ' + str(self.product_title)

    class Meta:
        ordering = ('-id',)


class Order(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    open_id = models.CharField(max_length=64, null=False)
    hub_id = models.IntegerField(null=False)
    order_id = models.CharField(max_length=200, null=False, unique=True)
    order_status = models.IntegerField(null=False, choices=ORDER_STATUS_TYPE)
    order_status_history = models.TextField(null=True, blank=True)
    operation_status = models.IntegerField(default=0, null=True, blank=True, choices=OPERATION_STATUS_TYPE)
    operation_status_history = models.TextField(default='[]', null=True, blank=True)
    order_start_date = models.DateTimeField(auto_now_add=True)
    order_finish_date = models.DateTimeField(null=True, blank=True)
    order_cancel_date = models.DateTimeField(null=True, blank=True)
    order_modified_date = models.DateTimeField(auto_now=True)
    order_daily_index = models.IntegerField(default=0, null=True, blank=True)
    user_name = models.CharField(default='', max_length=32, null=False, blank=True)
    user_telephone = models.CharField(default='', max_length=32, null=False, blank=True)
    user_receipt = models.CharField(default='', max_length=100, null=True, blank=True)
    delivery_on_site = models.BooleanField(default=False, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_schedule = models.IntegerField(null=True, blank=True)
    delivery_as_fast = models.BooleanField(default=False)
    delivery_customer_name = models.CharField(max_length=64, null=False)
    delivery_recipient_name = models.CharField(default='', max_length=30, null=True, blank=True)
    delivery_recipient_mdn = models.CharField(default='', max_length=20, null=True, blank=True)
    delivery_address = models.CharField(default='0', max_length=300, null=False)
    delivery_address_lat = models.FloatField(default=0.0, null=True, blank=True)
    delivery_address_lng = models.FloatField(default=0.0, null=True, blank=True)
    delivery_time = models.CharField(max_length=100, null=False)
    shipping_method = models.IntegerField(null=False)
    shipping_status = models.IntegerField(default=0)
    shipping_number = models.CharField(default='', max_length=64, null=True, blank=True)
    shipping_rider_id = models.CharField(default='', max_length=64, null=True, blank=True)
    shipping_rider_telephone = models.CharField(default='', max_length=32, null=True, blank=True)
    comments = models.TextField(default='', max_length=500, null=True, blank=True)

    def __str__(self):
        return str(self.order_id) + ' : ' + str(self.open_id)

    class Meta:
        ordering = ('-id', 'delivery_date')


# Coupon domain
class Coupon(models.Model):
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(default='[]', null=True, blank=True)
    condition_desc = models.TextField(default='', max_length=100, null=True, blank=True)
    is_primary_coupon = models.BooleanField(default=True)
    is_time_coupon = models.BooleanField(default=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    image = models.CharField(max_length=64)
    status = models.IntegerField(null=False)
    # 0: Available coupon 1: Used coupon 2: expired coupon
    coupon_type = models.IntegerField(null=False)
    # 0: 정액, 1: 정률, 2: free meal, 3: 메뉴 1+1, 4: 배송비 5: 사은품
    cash_type = models.IntegerField(default=0, blank=True)
    # 금액 할인 화폐 단위 0: RMB, 1: USD
    cash_discount = models.FloatField(default=0.0, blank=True)
    cash_minimum = models.FloatField(default=0.0, blank=True)
    cash_maximum = models.FloatField(default=0.0, blank=True)
    # 총 주문금액(배송비 제외)이 이 금액을 넘어야 사용 가능
    target_type = models.IntegerField(default=0, blank=True)
    # 100: 전체 음식, 200: 결제 총액, 300: 메뉴 갯수, 400:
    target_product_ids = models.TextField(default='[]', null=True, blank=True)
    target_detail = models.CharField(default='', max_length=32, blank=True)
    target_min = models.IntegerField(default=0, blank=True)
    target_max = models.IntegerField(default=0, blank=True)
    delivery_detail = models.IntegerField(default=0, blank=True)
    # coupon_type이 4인 경우에만 사용, 0: viastelle 무료 배달, 1: 일반 무료 배달
    period_type = models.IntegerField(default=1)
    # 0: 영구적인 기간, 1: static period, 2: dynamic period - 발급 시 기간 할당
    period_day = models.IntegerField(default=0, null=True, blank=True)
    period_start_date = models.DateField(null=True, blank=True)
    period_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('-id',)


class EventCoupon(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    event_type = models.IntegerField(default=0, null=False, blank=False)
    coupon_id = models.IntegerField(default=0, null=False, blank=False)
    coupon_count = models.IntegerField(default=1, null=True, blank=True)
    has_coupon_pack = models.BooleanField(default=False, blank=True)
    coupon_pack = models.TextField(default='[]', null=True, blank=True)
    coupon_code = models.CharField(default='', max_length=50, null=True, blank=True)
    serial_number = models.CharField(max_length=20, null=False, blank=False, db_index=True)
    issued = models.BooleanField(default=False, null=False, blank=False)
    issued_count = models.IntegerField(default=0, null=True, blank=True)
    issued_limitation = models.IntegerField(default=0, null=True, blank=True)
    issued_date = models.DateField(null=True, blank=True)
    issued_user_open_id = models.CharField(max_length=50, null=True, blank=True)
    issued_customer_coupon_id = models.TextField(default='[]', null=True, blank=True)

    def __str__(self):
        return str(self.name) + ' : ' + str(self.serial_number)

    class Meta:
        ordering = ('-id',)


class CustomerCoupon(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    coupon_code = models.CharField(default='', max_length=50, null=True, blank=True)
    coupon_reward = models.BooleanField(default=False, blank=True)
    open_id = models.CharField(max_length=32)
    issue_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    sender_id = models.CharField(max_length=64)
    status = models.IntegerField(default=0)
    used_date = models.DateTimeField(null=True, blank=True)
    target_id = models.IntegerField(default=0, null=True, blank=True)
    context = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.open_id) + ' : ' + str(self.coupon.name)

    class Meta:
        ordering = ('-id',)


class AutomaticIssueCoupon(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    coupon_code = models.CharField(default='', max_length=50, null=True, blank=True)
    status = models.IntegerField(default=0)
    issue_start_date = models.DateField()
    issue_end_date = models.DateField()
    sender_id = models.CharField(max_length=64)
    issue_condition_type = models.IntegerField(default=0, choices=AUTOMATIC_COUPON_ISSUE_TYPE)

    def __str__(self):
        return str(self.coupon.name)

    class Meta:
        ordering = ('-id',)


class AutomaticIssueResult(models.Model):
    open_id = models.CharField(max_length=32)
    automatic_issue_coupon = models.ForeignKey(AutomaticIssueCoupon, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.open_id)

    class Meta:
        ordering = ('-id',)


class Promotion(models.Model):
    status = models.IntegerField(default=0, null=False, blank=True)
    hub_id = models.IntegerField(default=1, null=False, blank=True)
    type = models.IntegerField(null=False, blank=True)
    has_display_group = models.BooleanField(default=False, blank=True)
    # 0: mobile web, 1: android, 2: ios
    android_display = models.BooleanField(default=False, blank=True)
    ios_display = models.BooleanField(default=False, blank=True)
    web_display = models.BooleanField(default=False, blank=True)
    main_image = models.CharField(max_length=100, null=False, blank=True)
    main_list_image = models.CharField(max_length=100, null=False, blank=True)
    promotion_list_image = models.CharField(max_length=100, null=False, blank=True)
    image_detail = models.TextField(default='', null=True, blank=True)
    main_title = models.CharField(max_length=50, null=False, blank=True)
    content = models.TextField(default='', null=False, blank=True)
    share_image = models.CharField(max_length=128, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    promotion_url = models.CharField(max_length=100, null=False, blank=False)
    product_list_index = models.IntegerField(default=1, null=True, blank=True)
    has_button = models.BooleanField(default=False, null=False, blank=False)
    button_type = models.IntegerField(default=0, null=True, blank=True)
    button_text = models.CharField(default='', max_length=20, null=True, blank=True)
    button_action_type = models.IntegerField(default=0, null=False, blank=False)
    button_action_detail = models.TextField(default='', null=True, blank=True)
    target_type = models.IntegerField(default=0, null=False, blank=True)
    target_detail = models.TextField(default='', null=True, blank=True)
    target_extra = models.TextField(default='', null=True, blank=True)

    def __str__(self):
        return str(self.main_title)

    class Meta:
        ordering = ('-id',)


class MemberPromotion(models.Model):
    COUPON_PROMOTION_TYPE = (
        (0, 'SIGN UP PROMOTION'),
    )

    status = models.IntegerField(default=1, null=False, blank=False)
    type = models.IntegerField(default=0, null=False, blank=False)
    language_type = models.IntegerField(default=0, null=False, blank=False)
    coupon_id = models.IntegerField(default=0, null=True, blank=True)
    coupon_days = models.IntegerField(default=14, null=True, blank=True)
    coupon_code = models.CharField(default='', max_length=50)
    sender_id = models.CharField(default='', max_length=50)
    has_popup = models.BooleanField(default=True, blank=True)
    title = models.CharField(default='', max_length=50, null=True, blank=True)
    sub_title = models.CharField(default='', max_length=50, null=True, blank=True)
    has_coupon_image = models.BooleanField(default=True)
    coupon_image = models.CharField(default='', max_length=200, null=True, blank=True)
    description = models.TextField(default='[]', null=True, blank=True)

    def __str__(self):
        return str(self.type) + ' / ' + str(self.title)

    class Meta:
        ordering = ('-id',)


# First order history
class EventOrderHistory(models.Model):
    EVENT_TYPE = (
        (0, 'REFERRAL FIRST PURCHASE'),
    )

    event_type = models.IntegerField(default=0, null=False, blank=False)
    event_target = models.BooleanField(default=False, blank=True)
    event_reward = models.BooleanField(default=False, blank=True)
    event_batch_check = models.BooleanField(default=False, blank=True)
    event_description = models.CharField(max_length=200, null=True, blank=True)
    register_date = models.DateField(null=True, blank=True)
    hub_id = models.IntegerField(null=False)
    open_id = models.CharField(max_length=64, null=False)
    order_id = models.CharField(max_length=200, null=False, unique=True)

    def __str__(self):
        return str(self.event_type) + ' / ' + str(self.order_id)

    class Meta:
        ordering = ('-id',)


class DadaOrderRequest(models.Model):
    # Original purchase domain
    purchase_order_id = models.CharField(max_length=200, null=False)
    purchase_order_id_index = models.IntegerField(default=1, null=False)
    # Dada order domain must use
    shop_no = models.CharField(null=False, max_length=30)
    origin_id = models.CharField(null=False, max_length=30)
    city_code = models.CharField(null=False, max_length=10)
    cargo_price = models.FloatField(default=0, null=False)
    is_prepay = models.IntegerField(default=0, null=False)
    receiver_name = models.CharField(null=False, max_length=20)
    receiver_address = models.CharField(null=False, max_length=200)
    receiver_lat = models.FloatField(default=0, null=False)
    receiver_lng = models.FloatField(default=0, null=False)
    callback = models.CharField(default='', null=False, max_length=100)
    # Dada order domain optional use
    receiver_phone = models.CharField(default='', null=True, blank=True, max_length=20)
    receiver_tel = models.CharField(default='', null=True, blank=True, max_length=20)
    tips = models.FloatField(default=0, blank=True)
    info = models.CharField(blank=True, max_length=200)
    cargo_type = models.IntegerField(default=1, blank=True)
    cargo_weight = models.FloatField(default=0, blank=True)
    delay_publish_time = models.IntegerField(default=0, blank=True)
    is_direct_delivery = models.IntegerField(default=0, blank=True)
    is_use_insurance = models.IntegerField(default=0, blank=True)
    # Dada order result domain
    res_distance = models.FloatField(null=True, blank=True, default=0)
    res_fee = models.FloatField(null=True, blank=True, default=0)
    res_deliverFee = models.FloatField(null=True, blank=True, default=0)
    res_couponFee = models.FloatField(null=True, blank=True, default=0)
    res_tips = models.FloatField(null=True, blank=True, default=0)
    res_insuranceFee = models.FloatField(null=True, blank=True, default=0)

    def __str__(self):
        return str(self.origin_id)

    class Meta:
        ordering = ('-id',)


class DadaOrderDetail(models.Model):
    DADA_ORDER_STATUS = (
        (0, 'NONE STATE'),
        (1, 'PENDING ORDER'),
        (2, 'TO PICK UP'),
        (3, 'IN THE DELIVERY'),
        (4, 'COMPLETED'),
        (5, 'CANCELLED'),
        (7, 'EXPIRED'),
        (8, 'ASSIGNED ORDER'),
        (9, 'Items that are properly thrown abnormally returned'),
        (10, 'Items that are properly thrown are returned to completion'),
        (1000, 'System failure order release failure')
    )

    orderId = models.CharField(null=False, max_length=30, unique=True)
    statusCode = models.IntegerField(default=1, choices=DADA_ORDER_STATUS)
    statusMsg = models.CharField(default='', max_length=100, blank=True)
    transporterName = models.CharField(default='', max_length=30, blank=True)
    transporterPhone = models.CharField(default='', max_length=20, blank=True)
    transporterLng = models.CharField(default='', max_length=20, blank=True)
    transporterLat = models.CharField(default='', max_length=20, blank=True)
    deliveryFee = models.FloatField(default=0, blank=True)
    tips = models.FloatField(default=0, blank=True)
    couponFee = models.FloatField(default=0, blank=True)
    insuranceFee = models.FloatField(default=0, blank=True)
    actualFee = models.FloatField(default=0, blank=True)
    distance = models.FloatField(default=0, blank=True)
    createTime = models.CharField(default='', max_length=20, blank=True)
    acceptTime = models.CharField(default='', max_length=20, blank=True)
    fetchTime = models.CharField(default='', max_length=20, blank=True)
    finishTime = models.CharField(default='', max_length=20, blank=True)
    cancelTime = models.CharField(default='', max_length=20, blank=True)
    orderFinishCode = models.CharField(default='', max_length=20, blank=True)
    receiptUrl = models.CharField(default='', max_length=100, blank=True)
    supplierName = models.CharField(default='', max_length=20, blank=True)
    supplierAddress = models.CharField(default='', max_length=50, blank=True)
    supplierPhone = models.CharField(default='', max_length=20, blank=True)
    supplierLat = models.CharField(default='', max_length=20, blank=True)
    supplierLng = models.CharField(default='', max_length=20, blank=True)
    receiver_address = models.CharField(default='', null=True, max_length=200, blank=True)
    receiver_lat = models.FloatField(default=0, null=True, blank=True)
    receiver_lng = models.FloatField(default=0, null=True, blank=True)

    def __str__(self):
        return str(self.orderId)

    class Meta:
        ordering = ('-id',)


class DadaCallback(models.Model):
    DADA_ORDER_STATUS = (
        (0, 'NONE STATE'),
        (1, 'PENDING ORDER'),
        (2, 'TO PICK UP'),
        (3, 'IN THE DELIVERY'),
        (4, 'COMPLETED'),
        (5, 'CANCELLED'),
        (7, 'EXPIRED'),
        (8, 'ASSIGNED ORDER'),
        (9, 'Items that are properly thrown abnormally returned'),
        (10, 'Items that are properly thrown are returned to completion'),
        (1000, 'System failure order release failure')
    )

    client_id = models.CharField(null=False, max_length=100)
    order_id = models.CharField(null=False, max_length=50)
    order_status = models.IntegerField(null=False, default=0, choices=DADA_ORDER_STATUS)
    cancel_reason = models.CharField(null=False, max_length=100)
    cancel_from = models.IntegerField(null=False, default=0)
    update_time = models.CharField(null=False, max_length=50)
    signature = models.CharField(null=False, max_length=50)
    dm_id = models.IntegerField(null=True, blank=True, default=0)
    dm_name = models.CharField(null=True, blank=True, max_length=20)
    dm_mobile = models.CharField(null=True, blank=True, max_length=20)
    sign_verification = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return str(self.order_id)

    class Meta:
        ordering = ('-id',)
