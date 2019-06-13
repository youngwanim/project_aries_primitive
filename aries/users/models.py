from django.db import models


# User domain
class User(models.Model):
    open_id = models.CharField(max_length=128)
    gender = models.CharField(max_length=1, null=True, blank=True)
    name = models.CharField(max_length=32, blank=True, default='')
    email = models.CharField(max_length=64, blank=True, default='')
    current_delivery_type = models.IntegerField(default=0, null=True, blank=True)
    default_address_id = models.IntegerField(default=0, null=True)
    default_address = models.CharField(default='', max_length=300, null=True, blank=True)
    default_recipient_name = models.CharField(default='', max_length=30, null=True, blank=True)
    default_recipient_mdn = models.CharField(default='', max_length=20, null=True, blank=True)
    default_hub_id = models.IntegerField(default=1, null=True)
    default_pickup_hub_id = models.IntegerField(default=1, null=True)
    default_pickup_hub = models.CharField(default='', max_length=200, blank=True)
    default_receipt_id = models.IntegerField(default=0, null=True, blank=True)
    default_receipt = models.CharField(default='', max_length=100, blank=True)
    parent_type = models.IntegerField(default=0, null=True, blank=True)
    mdn = models.CharField(default='', max_length=32, null=True, blank=True)
    mdn_verification = models.BooleanField(default=False)
    push_agreement = models.CharField(max_length=1, default='Y', null=True)
    locale = models.CharField(max_length=5, default='en', null=True)
    profile_image = models.CharField(max_length=64, blank=True, default='')
    access_token = models.CharField(max_length=64, null=True, blank=True)
    connection_count = models.IntegerField(default=0, null=True, blank=True)
    connection_account = models.TextField(default='[]', max_length=200, blank=True)
    has_upcoming_order = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return str(self.open_id) + ' : ' + str(self.mdn)

    class Meta:
        ordering = ('-id',)


class UserLoginInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_type = models.IntegerField()  # mobile/web = 0, QQ= 1, WE_CHAT = 2
    login_key = models.CharField(max_length=64, null=True, blank=True)
    login_value = models.CharField(max_length=64, null=True, blank=True)
    login_sns_open_id = models.CharField(max_length=64, null=True, blank=True)
    login_sns_access_token = models.CharField(max_length=128, null=True, blank=True)
    login_sns_refresh_token = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.user.open_id) + ' : ' + str(self.login_type) + ' : ' + str(self.login_key)

    class Meta:
        ordering = ('id',)


class UserAddressInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    recipient_name = models.CharField(default='', max_length=30, null=True, blank=True)
    recipient_mdn = models.CharField(default='', max_length=20, null=True, blank=True)
    has_pending = models.BooleanField(default=False, blank=True)
    delivery_area = models.BooleanField(default=False, null=False)
    selected_address = models.BooleanField(default=False, null=False)
    hub_id = models.IntegerField(default=1, null=False, blank=False)
    city = models.CharField(max_length=30, null=True, blank=True)
    city_code = models.CharField(max_length=20, null=False)
    ad_code = models.CharField(max_length=50, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)
    format_address = models.CharField(default='', max_length=300, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    township = models.CharField(max_length=100, null=True, blank=True)
    towncode = models.CharField(max_length=100, null=True, blank=True)
    building = models.CharField(max_length=100, null=True, blank=True)
    neighborhood = models.CharField(max_length=100, null=True, blank=True)
    street = models.CharField(default='', max_length=100, null=True, blank=True)
    street_number = models.CharField(default='', max_length=100, null=True, blank=True)
    detail = models.CharField(default='', max_length=200, null=True, blank=True)
    latitude = models.FloatField(default=0.0, null=True)
    longitude = models.FloatField(default=0.0, null=True)
    modified_date = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.user.open_id + " : " + self.name)

    class Meta:
        ordering = ('-id',)


class UserNotifyInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_new_coupon = models.BooleanField(default=False, blank=True)
    coupon_count = models.IntegerField(default=0, null=True, blank=True)
    has_upcoming_order = models.BooleanField(default=False, blank=True)
    upcoming_order_count = models.IntegerField(default=0, null=True, blank=True)
    has_news = models.BooleanField(default=False, blank=True)
    news_count = models.IntegerField(default=0, null=True, blank=True)
    has_promotion = models.BooleanField(default=False, blank=True)
    has_event = models.BooleanField(default=False, blank=True)
    has_referral_event = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return str(self.user.open_id + " : " + self.user.name)

    class Meta:
        ordering = ('id',)


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    os_type = models.IntegerField(default=-1, null=True, blank=True)
    latest_payment_method = models.IntegerField(default=-1, null=True, blank=True)
    latest_shipping_method = models.IntegerField(default=0, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    last_logon = models.DateTimeField(auto_now=True, null=True, blank=True)
    date_of_register = models.DateField(auto_now_add=True, null=True, blank=True)
    number_of_logon = models.IntegerField(null=True, blank=True)
    date_account_last_modified = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.user.open_id)

    class Meta:
        ordering = ('id',)


class UserGrade(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.IntegerField()
    extra_meal_point = models.IntegerField()
    extra_meal_point_ratio = models.IntegerField(default=3)
    upgrade_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.user.open_id)

    class Meta:
        ordering = ('id',)


class ShoppingBag(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    product_list = models.TextField(default='[]', blank=True)
    instruction_history = models.TextField(default='[]', blank=True)
    include_cutlery = models.BooleanField(default=True, blank=True)
    last_modified_date = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.user.open_id)

    class Meta:
        ordering = ('id',)


class UserNews(models.Model):
    NEWS_TYPE = (
        (0, 'PROMOTION'),
        (1, 'COUPON'),
        (2, 'ORDER_COMPLETE'),
        (3, 'ORDER_CANCELED'),
        (4, 'DELIVERY_STARTED'),
        (5, 'DELIVERY_COMPLETE'),
        (6, 'REVIEW_REQUEST'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.IntegerField(default=0, choices=NEWS_TYPE)
    title = models.CharField(max_length=50, null=False, blank=False)
    title_cn = models.CharField(default='', max_length=50, null=True, blank=True)
    content = models.TextField(null=False, blank=False)
    content_cn = models.TextField(default='', null=True, blank=True)
    # content is json object
    has_read = models.BooleanField(default=False, blank=True)
    detail = models.CharField(max_length=150)
    detail_cn = models.CharField(max_length=150)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.open_id)

    class Meta:
        ordering = ('-id',)


class UserReceipt(models.Model):
    RECEIPT_TYPE = (
        (0, 'COMPANY'),
        (1, 'PERSONAL')
    )

    """
    타입, 명칭(개인의 이름이 될 수도 있고 회사 이름이 될 수도 있음), 납세번호(택스넘버), 주소, 전화번호, 은행명
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected = models.BooleanField(default=False, blank=True)
    type = models.IntegerField(default=0, choices=RECEIPT_TYPE)
    name = models.CharField(default='', max_length=30, null=True, blank=True)
    tax_id_number = models.CharField(default='', max_length=30, null=True, blank=True)

    def __str__(self):
        return str(self.user.open_id)

    class Meta:
        ordering = ('-id',)


class SmsAuthHistory(models.Model):
    date = models.DateField()
    target_mdn = models.CharField(max_length=32, null=False, blank=False)
    verification_code = models.CharField(max_length=32, null=False, blank=False)
    has_verified = models.BooleanField(default=False)
    verification_count = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return str(self.target_mdn)

    class Meta:
        ordering = ('-id',)


class UserReferralInformation(models.Model):
    user_open_id = models.CharField(max_length=128)
    user_mdn = models.CharField(max_length=32, null=True, blank=True)
    referrer_open_id = models.CharField(max_length=128)
    referrer_share_id = models.CharField(max_length=8, blank=True)
    referrer_mdn = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return '{} from {}'.format(self.user_open_id, self.referrer_share_id)

    class Meta:
        ordering = ('-id',)
