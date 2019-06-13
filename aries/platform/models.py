from django.db import models


# Auth platform domain
class AuthToken(models.Model):
    access_token = models.CharField(max_length=64, null=False, unique=True)
    access_token_state = models.IntegerField(null=False, default=0)
    user_open_id = models.CharField(max_length=64, null=False, unique=True)
    user_account = models.CharField(max_length=64, null=False)
    scope = models.TextField(blank=False)

    def __str__(self):
        return str(self.user_account)

    class Meta:
        ordering = ('id',)


# Scope domain
class AuthScope(models.Model):
    scope_id = models.CharField(max_length=32, null=False, unique=True)
    scope = models.TextField(blank=True)

    def __str__(self):
        return str(self.scope_id)

    class Meta:
        ordering = ('id',)


# Operation domain
class OperationStatus(models.Model):
    OPERATION_STATUS = (
        (0, 'Operation normal'),
        (1, 'Period maintenance'),
        (2, 'Emergency maintenance')
    )

    status = models.IntegerField(null=False, choices=OPERATION_STATUS)
    popup_count = models.IntegerField(default=1, null=True, blank=True)
    application_version = models.FloatField(null=False)
    application_version_name = models.CharField(max_length=10, null=True)
    # latest field
    android_min_version_code = models.IntegerField(null=True)
    android_latest_version_code = models.IntegerField(null=True)
    android_latest_version_name = models.CharField(max_length=10, null=True)
    # latest field
    ios_min_version_code = models.CharField(max_length=10, null=True)
    ios_latest_version_code = models.CharField(max_length=10, null=True)
    ios_latest_version_name = models.CharField(max_length=10, null=True)
    web_version = models.FloatField(null=False)
    web_version_code = models.CharField(max_length=10, null=True)
    force_update = models.BooleanField(default=False, null=False)
    current_status_comment = models.TextField(blank=True)
    registered_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "[version and/ios/web]:" + str(self.status) + "/" + str(self.web_version)

    class Meta:
        ordering = ('-id',)


class OperationPopup(models.Model):
    status = models.IntegerField(null=False)
    main_image = models.CharField(max_length=128, null=False, blank=False)
    main_title = models.CharField(max_length=100, null=False, blank=False)
    main_image_cn = models.CharField(max_length=128, null=False, blank=False)
    main_title_cn = models.CharField(max_length=100, null=False, blank=False)
    content = models.TextField(null=True, blank=True)
    content_cn = models.TextField(null=True, blank=True)
    share_image = models.CharField(max_length=128, null=True, blank=True)
    share_image_cn = models.CharField(max_length=128, null=True, blank=True)
    has_button = models.BooleanField(default=False, null=False, blank=False)
    button_type = models.IntegerField(default=0, null=True, blank=True)
    button_text = models.CharField(default='', max_length=20, null=True, blank=True)
    button_text_cn = models.CharField(default='', max_length=20, null=True, blank=True)
    button_action_type = models.IntegerField(default=0, null=False, blank=False)
    button_action_detail = models.TextField(default='', null=True, blank=True)
    target_type = models.IntegerField(default=0, null=False, blank=True)
    target_detail = models.TextField(default='', null=True, blank=True)
    target_extra = models.TextField(default='', null=True, blank=True)

    def __str__(self):
        return str(self.main_title)

    class Meta:
        ordering = ('-id',)


class HubOperationStatus(models.Model):
    status = models.IntegerField(null=False)
    current_status_comment = models.TextField(blank=True)
    registered_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.status)

    class Meta:
        ordering = ('-id',)


class Operator(models.Model):
    ACCOUNT_LEVEL = (
        ('hub', 'HUB'),
        ('kitchen', 'KITCHEN'),
        ('admin', 'ADMIN')
    )

    HUB_ID = (
        (0, 'HUB_001_SHANGHAI'),
        (1, 'HUB_002_SHANGHAI'),
    )

    account = models.CharField(max_length=30, null=False, blank=False)
    password = models.CharField(max_length=200, null=False, blank=False)
    scope = models.CharField(default='operator', max_length=10, choices=ACCOUNT_LEVEL)
    hub_id = models.IntegerField(default=1)
    name = models.CharField(max_length=30, null=True, blank=True)
    employee_id = models.CharField(max_length=20, null=False, blank=False)
    employee_telephone = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.account)

    class Meta:
        ordering = ('-id',)
