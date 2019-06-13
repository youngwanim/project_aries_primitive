from django.db import models


MENU_TYPE = (
    (0, 'Set menu'),
    (1, 'Main dish'),
    (2, 'Side dish'),
    (3, 'Dessert'),
    (4, 'Drink'),
    (5, 'Wine'),
    (6, 'Salad'),
    (7, 'ChopSalad'),
    (8, 'Subscription'),
    (10, 'Event'),
    (20, 'Promotion'),
)

ICON_TYPE = (
    (0, 'No Icon'),
    (1, 'Microwave Icon')
)


class Restaurant(models.Model):
    name = models.CharField(max_length=32, null=True)
    email = models.CharField(max_length=64, null=True)
    account = models.CharField(max_length=32, unique=True, null=True)
    password = models.CharField(max_length=32, null=True)
    bank_name = models.CharField(max_length=32, null=True, blank=True)
    bank_account = models.CharField(max_length=32, null=True, blank=True)
    introduce_image = models.CharField(max_length=128, null=True, blank=True)
    chef = models.CharField(max_length=32, null=True)
    award_info = models.TextField(default='[]', null=True, blank=True)
    cuisine_info = models.TextField(default='[]', null=True, blank=True)
    address = models.CharField(max_length=32, null=True, blank=True)
    longitude = models.FloatField(null=True, default=0.0)
    latitude = models.FloatField(null=True, default=0.0)
    country = models.CharField(max_length=32, null=True)
    contract_complete = models.IntegerField(default=0, null=True)
    agreement_terms = models.TextField(default='', null=True, blank=True)
    privacy_policy = models.TextField(default='', null=True, blank=True)
    menu_count = models.IntegerField(default=0, null=True, blank=True)
    keyword = models.TextField(default='', null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('-id',)


class RestaurantBrandInfo(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE)
    restaurant_logo = models.CharField(max_length=128, null=False)
    restaurant_region = models.CharField(max_length=20, null=True, blank=True)
    chef_name = models.CharField(max_length=30, null=False)
    chef_image = models.CharField(max_length=128, null=False)
    chef_content = models.TextField(null=True, blank=True)
    award_image = models.CharField(max_length=128, null=False)
    award_content = models.TextField(null=True, blank=True)
    restaurant_content = models.TextField(null=True, blank=True)
    interview_content = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.restaurant.name

    class Meta:
        ordering = ('id',)


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, null=False)
    cooking_materials = models.CharField(default='', max_length=128, null=True, blank=True)
    type = models.IntegerField(null=True, blank=True, choices=MENU_TYPE)
    icon_type = models.IntegerField(default=0, null=True, blank=True, choices=ICON_TYPE)
    image_main = models.CharField(max_length=128, null=True, blank=True)
    image_detail = models.TextField(default='', null=True, blank=True)
    image_sub = models.CharField(max_length=128, null=True, blank=True)
    image_thumbnail = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image_package = models.CharField(max_length=128, null=True, blank=True)
    prep_tips = models.TextField(null=True, blank=True)
    prep_plating_thumbnail = models.CharField(max_length=128, null=True, blank=True)
    prep_plating_url = models.CharField(default='', max_length=128, null=True, blank=True)
    ingredients = models.TextField(default='[]', null=True, blank=True)
    nutrition = models.TextField(default='[]', null=True, blank=True)
    notices = models.TextField(default='[]', null=True, blank=True)
    subs_contents = models.TextField(default='[]', null=True, blank=True)
    media_contents = models.TextField(default='[]', null=True, blank=True)
    has_popup_contents = models.BooleanField(default=False, blank=True)
    popup_contents = models.TextField(default='{"title":"","description":""}', blank=True)
    keyword = models.TextField(default='', null=True, blank=True)

    def __str__(self):
        return self.restaurant.name + ":" + self.name

    class Meta:
        ordering = ('-id',)


class MenuReviewStatics(models.Model):
    menu = models.OneToOneField(Menu, on_delete=models.CASCADE)
    average_point = models.FloatField(null=False)
    review_count = models.IntegerField(default=0, null=True, blank=True)
    review_count_postfix = models.CharField(default='', max_length=5, null=True, blank=True)

    def __str__(self):
        return str(self.menu)

    class Meta:
        ordering = ('id',)


class Hub(models.Model):
    LOCATION_TYPE = (
        ('000', 'DEFAULT'),
        ('021', 'SHANGHAI'),
    )

    HUB_STATUS = {
        (0, 'OPEN SOON'),
        (1, 'CURRENT AVAILABLE')
    }

    code = models.IntegerField(default=1)
    name = models.CharField(max_length=32)
    status = models.IntegerField(default=1)
    location = models.CharField(max_length=100)
    location_type = models.CharField(default='021', max_length=10, choices=LOCATION_TYPE)
    address = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.FloatField(default=0, null=True, blank=True)
    latitude = models.FloatField(default=0, null=True, blank=True)
    manager_name = models.CharField(max_length=30, null=True, blank=True)
    telephone = models.CharField(max_length=30, null=True, blank=True)
    geometry_information = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name + '-' + str(self.code)

    class Meta:
        ordering = ('-id', 'location_type',)


class Product(models.Model):
    STATUS_TYPE = (
        (0, 'SOLD OUT'),
        (1, 'NOW SALE'),
        (2, 'UNTIL LUNCH'),
        (3, 'UNTIL DINNER'),
        (4, 'COMING SOON'),
        (5, 'MORNING ONLY'),
        (6, 'LUNCH ONLY'),
        (7, 'DINNER ONLY'),
    )

    PRODUCT_TYPE = (
        (0, 'Set menu'),
        (1, 'Main dish'),
        (2, 'Side dish'),
        (3, 'Dessert'),
        (4, 'Drink'),
        (5, 'Wine'),
        (6, 'Salad'),
        (7, 'ChopSalad'),
        (8, 'Subscription'),
        (10, 'Event'),
        (20, 'Promotion')
    )

    SALES_TIME = (
        (0, 'ALL DAY'),
        (1, 'ONLY MORNING'),
        (2, 'ONLY LUNCH'),
        (3, 'ONLY DINNER')
    )

    PROD_DESC_TYPE = (
        (0, 'LUNCH_ONLY'),
        (1, 'DINNER_ONLY'),
        (2, 'SUBSCRIPTION_PROD'),
        (3, 'EVENT_PROD'),
    )

    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    list_index = models.IntegerField()
    type = models.IntegerField(default=0, choices=PRODUCT_TYPE)
    price = models.FloatField(default=0.0)
    price_unit = models.IntegerField(default=0)
    price_discount = models.FloatField(default=0.0)
    price_discount_event = models.BooleanField(default=False)
    price_discount_schedule = models.TextField(default='[]', null=True, blank=True)
    badge_en = models.TextField(default='[]', null=True, blank=True)
    badge_cn = models.TextField(default='[]', null=True, blank=True)
    category = models.TextField(default='[]', null=True, blank=True)
    status = models.IntegerField(default=0, choices=STATUS_TYPE)
    sales_time = models.IntegerField(default=0, choices=SALES_TIME)
    has_description = models.BooleanField(default=False, blank=True)
    description_type = models.IntegerField(default=0, null=True, blank=True, choices=PROD_DESC_TYPE)
    has_sales_schedule = models.BooleanField(default=False, blank=True)
    sales_schedule = models.TextField(default='[]', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    event_product = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.get_sales_str() + ' | ' + self.hub.name + " : " + str(self.list_index) + " / (" \
               + str(self.start_date) + ") ~ (" + str(self.end_date) + ") " + str(self.menu.name) \
               + ' | [' + str(self.price) + '/Discount:' + str(self.price_discount_event) + '/' \
               + str(self.price_discount) + ']'

    def get_sales_str(self):
        if self.sales_time == 0:
            result = 'ALL DAY'
        elif self.sales_time == 1:
            result = 'Morning'
        elif self.sales_time == 2:
            result = 'Lunch'
        else:
            result = 'Dinner'
        return result

    class Meta:
        ordering = ('-hub', 'list_index',)


class MenuPairingInformation(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    pairing_menu = models.IntegerField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.menu.name

    class Meta:
        ordering = ('-id',)


class HubStock(models.Model):
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    production_amount = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)

    def __str__(self):
        return self.hub.name + ' : ' + str(self.menu.name) + ' / stock : ' \
               + str(self.stock) + ', sold : ' + str(self.sold)

    class Meta:
        ordering = ('-id',)


class ProductType(models.Model):
    PRODUCT_TYPE = (
        (0, 'Set menu'),
        (1, 'Main dish'),
        (2, 'Side dish'),
        (3, 'Dessert'),
        (4, 'Drink'),
        (5, 'Wine'),
        (6, 'Salad'),
        (10, 'Event'),
        (20, 'Promotion')
    )

    list_index = models.IntegerField(default=0)
    language_type = models.IntegerField(default=0)
    type = models.IntegerField(default=0, choices=PRODUCT_TYPE)
    type_name = models.CharField(default='', max_length=50)

    def __str__(self):
        return str(self.language_type) + ' ' + str(self.type_name)

    class Meta:
        ordering = ('list_index', 'language_type')


class ExpertReview(models.Model):
    menu = models.IntegerField(null=False)
    created_date = models.DateTimeField(auto_now=True)
    expert_job = models.CharField(max_length=50, null=False, blank=False)
    expert_name = models.CharField(max_length=32, null=False, blank=False)
    expert_image = models.CharField(max_length=128, null=False, blank=False)
    expert_comment = models.TextField()

    def __str__(self):
        return str(self.expert_name)

    class Meta:
        ordering = ('id',)


class TimeBomb(models.Model):
    TIME_BOMB_STATUS = (
        (0, 'CREATED'),
        (1, 'ACTIVATED'),
        (2, 'SOLD_OUT_FINISH'),
        (3, 'TIME_EXPIRED'),
    )

    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    status = models.IntegerField(default=0, null=False, choices=TIME_BOMB_STATUS, blank=True)
    target_android = models.BooleanField(default=True)
    target_ios = models.BooleanField(default=True)
    target_mobile_web = models.BooleanField(default=True)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=False)

    def __str__(self):
        return str(self.hub.name)

    class Meta:
        ordering = ('-id',)


class TimeBombContent(models.Model):
    time_bomb = models.ForeignKey(TimeBomb, on_delete=models.CASCADE)
    language_type = models.IntegerField(default=0)
    main_content = models.TextField(default='', max_length=300, blank=True)
    guide_content = models.TextField(default='[]', max_length=1500, blank=True)
    sold_out_message = models.CharField(default='', max_length=200, blank=True)
    expired_message = models.CharField(default='', max_length=200, blank=True)
    discount_message = models.CharField(default='', max_length=30, blank=True)
    start_main_image = models.CharField(default='', max_length=100, blank=True)
    end_main_image = models.CharField(default='', max_length=100, blank=True)
    start_banner_image = models.CharField(default='', max_length=100, blank=True)
    end_banner_image = models.CharField(default='', max_length=100, blank=True)
    popup_image = models.CharField(default='', max_length=100, blank=True)

    def __str__(self):
        return str(self.language_type)

    class Meta:
        ordering = ('-id',)


class TimeBombDiscountInfo(models.Model):
    time_bomb = models.ForeignKey(TimeBomb, on_delete=models.CASCADE)
    product_id = models.IntegerField(default=0, null=False, blank=False)
    discount_type = models.IntegerField(default=0, null=False)
    discount_rate = models.IntegerField(default=0, null=False, blank=False)
    discount_desc_en = models.CharField(default='', max_length=5, null=True)
    discount_desc_cn = models.CharField(default='', max_length=5, null=True)
    set_event_product = models.BooleanField(default=True)

    def __str__(self):
        return str(self.product_id)

    class Meta:
        ordering = ('-id',)
