from django.db import models


# Payments domain
ALIPAY_TRANSACTION_STATUS = (
    ('WAIT_BUYER_PAY', 'WAIT_BUYER_PAY'),
    ('TRADE_CLOSED', 'TRADE_CLOSED'),
    ('TRADE_SUCCESS', 'TRADE_SUCCESS'),
    ('TRADE_FINISHED', 'TRADE_FINISHED'),
)

PAYMENT_STATUS = (
    (0, 'Payment complete'),
    (1, 'Query and verify complete'),
    (3, 'Verification failed'),
    (4, 'Payment is not complete'),
    (5, 'Payment canceled with refund'),
    (6, 'Payment canceled without refund'),
    (7, 'Payment canceled operating refund')
)


class Payment(models.Model):
    created_date = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=100, null=False, blank=True)
    open_id = models.CharField(max_length=64, null=False)
    order_id = models.CharField(max_length=200, null=False, unique=True)
    payment_status = models.IntegerField(null=False, choices=PAYMENT_STATUS)
    payment_type = models.IntegerField(null=False)
    payment_raw_data = models.TextField(null=False)
    price_unit = models.IntegerField(default=0, null=False)
    price_total = models.FloatField(null=False)

    def __str__(self):
        return str(self.order_id)

    class Meta:
        ordering = ('-id',)


class AlipayPaymentTransaction(models.Model):
    alipay_trade_validation = models.BooleanField(default=False)
    # Alipay sync specification
    out_trade_no = models.CharField(max_length=64, null=False, blank=False)
    trade_no = models.CharField(max_length=64, null=False, blank=False)
    app_id = models.CharField(max_length=32, null=False, blank=False)
    total_amount = models.FloatField(max_length=9, null=False, blank=False)
    seller_id = models.CharField(max_length=16, null=False, blank=False)
    msg = models.CharField(max_length=16, null=False, blank=False)
    charset = models.CharField(max_length=16, null=False, blank=False)
    timestamp = models.CharField(max_length=32, null=False, blank=False)
    code = models.CharField(max_length=16, null=False, blank=False)

    def __str__(self):
        return str(self.out_trade_no)

    class Meta:
        ordering = ('-id',)


class AlipayQueryTransaction(models.Model):
    order_id = models.CharField(max_length=200, null=False, unique=True)
    alipay_query_validation = models.BooleanField(default=False, blank=True)
    # Common response parameters
    code = models.CharField(max_length=20, null=False, blank=False)
    msg = models.CharField(max_length=100, null=False, blank=False)
    sub_code = models.CharField(max_length=20, null=True, blank=True)
    sub_msg = models.CharField(max_length=100, null=True, blank=True)
    # Query response parameters
    trade_no = models.CharField(max_length=64, null=True, blank=True)
    out_trade_no = models.CharField(max_length=64, null=True, blank=True)
    buyer_logon_id = models.CharField(max_length=100, null=True, blank=True)
    trade_status = models.CharField(max_length=32, null=True, blank=True, choices=ALIPAY_TRANSACTION_STATUS)
    total_amount = models.FloatField(max_length=11, null=True, blank=True)
    receipt_amount = models.FloatField(max_length=11, null=True, blank=True)
    buyer_pay_amount = models.FloatField(max_length=11, null=True, blank=True)
    point_amount = models.FloatField(max_length=11, null=True, blank=True)
    invoice_amount = models.FloatField(max_length=11, null=True, blank=True)
    send_pay_date = models.CharField(max_length=32, null=True, blank=True)
    store_id = models.CharField(max_length=32, null=True, blank=True)
    terminal_id = models.CharField(max_length=32, null=True, blank=True)
    fund_bill_list = models.TextField(null=True, blank=True)
    store_name = models.TextField(max_length=512, null=True, blank=True)
    buyer_user_id = models.CharField(max_length=28, null=True, blank=True)

    def __str__(self):
        return str(self.order_id)

    class Meta:
        ordering = ('-id',)


class AlipayRefundTransaction(models.Model):
    order_id = models.CharField(max_length=200, null=False, unique=True)
    status = models.IntegerField(null=False)
    alipay_refund_validation = models.BooleanField(default=False)
    # 0: Refund success, 1: Refund fail
    # 2: validation failed, 3: Don't find order id

    # Common response parameters
    code = models.CharField(max_length=20, null=False, blank=False)
    msg = models.CharField(max_length=100, null=False, blank=False)
    sub_code = models.CharField(max_length=20, null=True, blank=True)
    sub_msg = models.CharField(max_length=100, null=True, blank=True)
    # Refund response parameters
    trade_no = models.CharField(max_length=64, null=True, blank=True)
    out_trade_no = models.CharField(max_length=64, null=True, blank=True)
    buyer_logon_id = models.CharField(max_length=100, null=True, blank=True)
    fund_change = models.CharField(max_length=1, null=True, blank=True)
    refund_fee = models.CharField(max_length=11, null=True, blank=True)
    send_back_fee = models.CharField(max_length=11, null=True, blank=True)
    gmt_refund_pay = models.CharField(max_length=32, null=True, blank=True)
    refund_detail_item_list = models.TextField(null=True, blank=True)
    store_name = models.TextField(max_length=512, null=True, blank=True)
    buyer_user_id = models.CharField(max_length=28, null=True, blank=True)

    def __str__(self):
        return str(self.order_id)

    class Meta:
        ordering = ('-id',)


class AlipayNotification(models.Model):
    order_id = models.CharField(max_length=200, null=False, unique=True)
    alipay_notification_validation = models.BooleanField(default=False)
    alipay_notification_history = models.TextField(default='[]', null=True, blank=True)
    # Alipay notification specification
    notify_time = models.CharField(max_length=20, null=False, blank=False)
    notify_type = models.CharField(max_length=64, null=False, blank=False)
    notify_id = models.CharField(max_length=128, null=False, blank=False)
    app_id = models.CharField(max_length=32, null=False, blank=False)
    charset = models.CharField(max_length=10, null=False, blank=False)
    version = models.CharField(max_length=3, null=False, blank=False)
    sign_type = models.CharField(max_length=10, null=False, blank=False)
    sign = models.TextField(null=False, blank=False)
    trade_no = models.CharField(max_length=64, null=False, blank=False)
    out_trade_no = models.CharField(max_length=64, null=False, blank=False)
    out_biz_no = models.CharField(max_length=64, null=True, blank=True)
    buyer_id = models.CharField(max_length=16, null=True, blank=True)
    buyer_logon_id = models.CharField(max_length=100, null=True, blank=True)
    seller_id = models.CharField(max_length=30, null=True, blank=True)
    seller_email = models.CharField(max_length=100, null=True, blank=True)
    trade_status = models.CharField(max_length=32, null=True, blank=True, choices=ALIPAY_TRANSACTION_STATUS)
    total_amount = models.FloatField(null=True, blank=True)
    receipt_amount = models.FloatField(null=True, blank=True)
    invoice_amount = models.FloatField(null=True, blank=True)
    buyer_pay_amount = models.FloatField(null=True, blank=True)
    point_amount = models.FloatField(null=True, blank=True)
    refund_fee = models.FloatField(null=True, blank=True)
    subject = models.CharField(max_length=256, null=True, blank=True)
    body = models.CharField(max_length=400, null=True, blank=True)
    gmt_create = models.CharField(max_length=30, null=True, blank=True,)
    gmt_payment = models.CharField(max_length=30, null=True, blank=True)
    gmt_refund = models.CharField(max_length=30, null=True, blank=True)
    gmt_close = models.CharField(max_length=30, null=True, blank=True)
    fund_bill_list = models.CharField(max_length=512, null=True, blank=True)
    passback_params = models.CharField(max_length=512, null=True, blank=True)
    voucher_detail_list = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.order_id)

    class Meta:
        ordering = ('-id',)


class WechatPaymentTransaction(models.Model):
    order_id = models.CharField(max_length=200, null=False, unique=True)
    price_unit = models.IntegerField(default=0, null=True, blank=True)
    payment_type = models.IntegerField(null=False, blank=False)
    price_total = models.FloatField(null=False, blank=False)
    payment_raw_data = models.TextField(null=False, blank=False)

    def __str__(self):
        return str(self.order_id)

    class Meta:
        ordering = ('-id',)


class WechatQueryTransaction(models.Model):
    order_id = models.CharField(max_length=200, null=False, unique=False)
    return_code = models.CharField(max_length=16, null=False, blank=False)
    return_msg = models.CharField(max_length=128, null=True, blank=True)
    appid = models.CharField(max_length=32, null=True, blank=True)
    mch_id = models.CharField(max_length=32, null=True, blank=True)
    nonce_str = models.CharField(max_length=32, null=True, blank=True)
    sign = models.CharField(max_length=32, null=True, blank=True)
    result_code = models.CharField(max_length=16, null=True, blank=True)
    err_code = models.CharField(max_length=32, null=True, blank=True)
    err_code_des = models.CharField(max_length=128, null=True, blank=True)
    device_info = models.CharField(max_length=32, null=True, blank=True)
    openid = models.CharField(max_length=128, null=True, blank=True)
    is_subscribe = models.CharField(max_length=1, null=True, blank=True)
    trade_type = models.CharField(max_length=16, null=True, blank=True)
    bank_type = models.CharField(max_length=16, null=True, blank=True)
    total_fee = models.IntegerField(null=True, blank=True)
    fee_type = models.CharField(max_length=8, null=True, blank=True)
    cash_fee = models.IntegerField(null=True, blank=True)
    cash_fee_type = models.CharField(max_length=16, null=True, blank=True)
    settlement_total_fee = models.IntegerField(null=True, blank=True)
    coupon_fee = models.IntegerField(null=True, blank=True)
    coupon_count = models.IntegerField(null=True, blank=True)
    coupon_id_list = models.TextField(null=True, blank=True)
    coupon_fee_list = models.TextField(null=True, blank=True)
    transaction_id = models.CharField(max_length=32, null=True, blank=True)
    out_trade_no = models.CharField(max_length=32, null=True, blank=True)
    attach = models.CharField(max_length=128, null=True, blank=True)
    time_end = models.CharField(max_length=14, null=True, blank=True)
    trade_state_desc = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return str(self.out_trade_no)

    class Meta:
        ordering = ('-id',)


class WechatRefundTransaction(models.Model):
    status = models.IntegerField(null=False)
    wechat_refund_validation = models.BooleanField(default=False)
    order_id = models.CharField(max_length=200, null=False, unique=True)
    return_code = models.CharField(max_length=16, null=False, blank=False)
    return_msg = models.CharField(max_length=128, null=True, blank=True)
    appid = models.CharField(max_length=32, null=True, blank=True)
    mch_id = models.CharField(max_length=32, null=True, blank=True)
    nonce_str = models.CharField(max_length=32, null=True, blank=True)
    sign = models.CharField(max_length=32, null=True, blank=True)
    sign_type = models.CharField(max_length=32, null=True, blank=True)
    transaction_id = models.CharField(max_length=32, null=True, blank=True)
    out_trade_no = models.CharField(max_length=32, null=True, blank=True)
    out_refund_no = models.CharField(max_length=64, null=True, blank=True)
    total_fee = models.IntegerField(null=True, blank=True)
    refund_fee = models.IntegerField(null=True, blank=True)
    refund_fee_type = models.CharField(max_length=8, null=True, blank=True)
    refund_desc = models.CharField(max_length=80, null=True, blank=True)
    refund_account = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return str(self.out_trade_no)

    class Meta:
        ordering = ('-id',)


class WechatNotification(models.Model):
    order_id = models.CharField(max_length=200, null=False)
    appid = models.CharField(max_length=32, null=False, blank=False)
    mch_id = models.CharField(max_length=32, null=False, blank=False)
    device_info = models.CharField(max_length=32, null=True, blank=True)
    nonce_str = models.CharField(max_length=32, null=False, blank=False)
    sign = models.CharField(max_length=32, null=False, blank=False)
    result_code = models.CharField(max_length=16, null=False, blank=False)
    err_code = models.CharField(max_length=32, null=True, blank=True)
    err_code_des = models.CharField(max_length=128, null=True, blank=True)
    openid = models.CharField(max_length=128, null=False, blank=False)
    is_subscribe = models.CharField(max_length=1, null=False, blank=False)
    trade_type = models.CharField(max_length=16, null=False, blank=False)
    bank_type = models.CharField(max_length=16, null=False, blank=False)
    total_fee = models.IntegerField(null=False, blank=False)
    fee_type = models.CharField(max_length=8, null=True, blank=True)
    cash_fee = models.IntegerField(null=False, blank=False)
    cash_fee_type = models.CharField(max_length=16, null=True, blank=True)
    coupon_fee = models.IntegerField(null=True, blank=True)
    coupon_count = models.IntegerField(null=True, blank=True)
    coupon_id_list = models.TextField(null=True, blank=True)
    coupon_fee_list = models.TextField(null=True, blank=True)
    transaction_id = models.CharField(max_length=32, null=False, blank=False)
    out_trade_no = models.CharField(max_length=32, null=False, blank=False)
    attach = models.CharField(max_length=128, null=True, blank=True)
    time_end = models.CharField(max_length=14, null=True, blank=True)

    def __str__(self):
        return str(self.out_trade_no)

    class Meta:
        ordering = ('-id',)
