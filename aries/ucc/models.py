from django.db import models


# Review domain
from django.utils import timezone


class CustomerReview(models.Model):
    menu = models.IntegerField(null=False)
    order_id = models.CharField(max_length=200, null=False)
    product_id = models.IntegerField(default=0, null=False)
    open_id = models.CharField(max_length=128, null=False)
    created_date = models.DateTimeField(auto_now=True)
    has_reviewed = models.BooleanField(default=False, blank=True)
    visible = models.BooleanField(default=True, blank=True)
    user_name = models.CharField(default='', max_length=32, null=True, blank=True)
    menu_rate = models.FloatField(null=False, blank=False)
    special_feedback = models.BooleanField(default=False, null=False, blank=False)
    feedback_type = models.IntegerField(default=0, null=False)
    comment = models.TextField(default='', max_length=500, null=True, blank=True)

    def __str__(self):
        return str(self.user_name)

    class Meta:
        ordering = ('-id',)


class ReviewItem(models.Model):
    status = models.IntegerField(default=0, null=False)
    type = models.IntegerField(default=0, null=False, unique=True)
    name = models.CharField(max_length=20, null=False)
    name_cn = models.CharField(max_length=20, null=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('id',)


class DisplaySchedule(models.Model):
    domain_type = models.IntegerField(default=0, null=True, blank=True)
    description = models.CharField(default='', max_length=50, null=True, blank=True)
    # FIRST: 1, SECOND: 2, THIRD: 3, FOURTH: 4
    has_week_schedule = models.BooleanField(default=False, blank=True)
    week_schedule = models.TextField(default='[]', max_length=50, null=True, blank=True)
    # MON: 0, TUE: 1, WED: 2, THU: 3, FRI: 4, SAT: 5, SUN: 6
    has_day_schedule = models.BooleanField(default=False, blank=True)
    day_schedule = models.TextField(default='[]', max_length=50, null=True, blank=True)
    # Follow to our time index
    has_time_schedule = models.BooleanField(default=False, blank=True)
    time_schedule = models.TextField(default='[]', max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.description)

    class Meta:
        ordering = ('-id',)


class CurationArticle(models.Model):
    LAYOUT_TYPE = (
        (0, 'TEXT_CATEGORY'), (1, 'GENERAL_BANNER'), (2, 'GENERAL_BANNER_SLIM'),
        (3, 'READ AND WATCH'), (4, 'LARGE_PIC_LANDSCAPE'), (5, 'MEDIUM_THUMBNAIL'),
        (6, 'SMALL_THUMBNAIL_CUBE'), (7, 'GROUP_UPPER_3')
    )

    ACTION_TYPE = (
        (0, 'Url link'), (1, 'None-click'), (2, 'External link'), (3, 'Brand detail'),
        (4, 'Product detail'), (5, 'Customer service'), (6, 'Setting'), (7, 'About viastelle'), (8, 'My coupon'),
        (9, 'Upcoming orders'), (10, 'Past orders'), (11, 'Delivery area'), (12, 'Product list'),
        (13, 'Url link with promotion'), (14, ''), (15, ''), (100, 'ROULETTE LINK'), (101, 'REFERRAL LINK')
    )

    layout_type = models.IntegerField(default=0, null=False, blank=False, choices=LAYOUT_TYPE)
    content_type = models.IntegerField(default=0, blank=True)
    action_type = models.IntegerField(default=0, null=True, blank=True, choices=ACTION_TYPE)
    action_target = models.CharField(default='', max_length=100, null=True, blank=True)
    action_extra = models.CharField(default='', max_length=300, null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    has_menu_data = models.BooleanField(default=False, blank=True)
    menu_id = models.IntegerField(default=0, null=True, blank=True)
    has_dp_schedule = models.BooleanField(default=False, blank=True)
    dp_schedule_id = models.IntegerField(default=0, null=True, blank=True)
    has_dp_status = models.BooleanField(default=False, blank=True)
    dp_status = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return 'ArticleId : {}'.format(str(self.layout_type))

    class Meta:
        ordering = ('-id',)


class CurationContent(models.Model):
    LANGUAGE_TYPE = ((0, 'ENGLISH'), (1, 'CHINESE'))

    curation_article = models.ForeignKey(CurationArticle, on_delete=models.CASCADE)
    language_type = models.IntegerField(default=0, blank=True, choices=LANGUAGE_TYPE)
    title = models.CharField(default='', max_length=100, null=True, blank=True)
    sub_title = models.CharField(default='', max_length=200, null=True, blank=True)
    content = models.CharField(default='', max_length=100, null=True, blank=True)
    sub_content = models.CharField(default='', max_length=100, null=True, blank=True)
    text_data = models.TextField(default='[]', max_length=500, null=True, blank=True)
    media_data = models.TextField(default='[]', max_length=500, null=True, blank=True)
    tag_data = models.TextField(default='[]', max_length=500, null=True, blank=True)
    award_data = models.TextField(default='[]', max_length=500, null=True, blank=True)

    def __str__(self):
        return 'Curation ID: {} / LANG: {}'.format(
            str(self.curation_article.id), str(self.language_type)
        )

    class Meta:
        ordering = ('-id',)


class CurationPage(models.Model):
    PAGE_STATUS = ((0, 'NOT VISIBLE'), (1, 'VISIBLE'))

    status = models.IntegerField(default=0, null=False, blank=False, choices=PAGE_STATUS)
    list_index = models.IntegerField(default=-1, null=False, blank=False)
    layout_type = models.IntegerField(default=0, null=False, blank=False)
    articles = models.TextField(default='[]', max_length=100, null=True, blank=True)
    article_limit = models.IntegerField(default=0, null=True, blank=True)
    start_date = models.DateField(auto_created=True, blank=True)
    end_date = models.DateField(auto_created=True, blank=True)
    has_extension_btn = models.BooleanField(default=False, blank=True)
    action_type = models.IntegerField(default=0, null=True, blank=True)
    action_target = models.CharField(default='', max_length=100, null=True, blank=True)
    action_extra = models.CharField(default='', max_length=100, null=True, blank=True)
    has_dp_schedule = models.BooleanField(default=False, blank=True)
    dp_schedule_id = models.IntegerField(default=0, null=True, blank=True)
    has_dp_status = models.BooleanField(default=False, blank=True)
    dp_status = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return 'LIST_INDEX: {}'.format(str(self.list_index))

    class Meta:
        ordering = ('list_index',)


class CurationPageContent(models.Model):
    LANGUAGE_TYPE = ((0, 'ENGLISH'), (1, 'CHINESE'))

    curation_page = models.ForeignKey(CurationPage, on_delete=models.CASCADE)
    language_type = models.IntegerField(default=0, blank=True, choices=LANGUAGE_TYPE)
    title = models.CharField(default='', max_length=100, null=True, blank=True)
    sub_title = models.CharField(default='', max_length=100, null=True, blank=True)
    has_title_img = models.BooleanField(default=False, blank=True)
    title_img = models.CharField(default='', max_length=200, null=True, blank=True)
    has_sub_title_img = models.BooleanField(default=False, blank=True)
    sub_title_img = models.CharField(default='', max_length=200, null=True, blank=True)

    def __str__(self):
        return 'CURATION PAGE: {}/ LANG: {}'.format(
            str(self.curation_page.id), str(self.language_type)
        )

    class Meta:
        ordering = ('id',)


class Event(models.Model):
    name = models.CharField(default='', max_length=100)
    event_component_count = models.IntegerField(default=1, null=True, blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    has_game_time = models.BooleanField(default=False, blank=True)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)
    need_auth = models.BooleanField(default=True, blank=True)
    limit_type = models.IntegerField(default=0)
    limit_count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('-id',)


class EventContent(models.Model):
    LANGUAGE_TYPE = ((0, 'ENGLISH'), (1, 'CHINESE'))

    language_type = models.IntegerField(default=0, blank=True, choices=LANGUAGE_TYPE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(default='', max_length=100, null=True, blank=True)
    sub_title = models.CharField(default='', max_length=100, null=True, blank=True)
    content = models.TextField(default='[]', null=True, blank=True)
    how_to_title = models.CharField(default='', max_length=100, null=True, blank=True)
    how_to_content = models.TextField(default='[]', null=True, blank=True)
    open_image = models.CharField(default='', max_length=100)
    played_image = models.CharField(default='', max_length=100)
    close_image = models.CharField(default='', max_length=100)

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ('-id',)


class Reward(models.Model):
    REWARD_TYPE = (
        (0, 'COUPON'), (1, 'POINT'), (2, 'UNKNOWN'),
    )

    LIMIT_TYPE = (
        (0, 'DAILY'), (1, 'WEEKLY'), (2, 'EVENT_PERIOD'),
    )

    name = models.CharField(default='', max_length=50)
    type = models.IntegerField(default=0, choices=REWARD_TYPE)
    target_id = models.IntegerField(default=0)
    target_point = models.IntegerField(default=0)
    limit_type = models.IntegerField(default=0)
    limit_count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('-id',)


class RewardContent(models.Model):
    LANGUAGE_TYPE = ((0, 'ENGLISH'), (1, 'CHINESE'))

    language_type = models.IntegerField(default=0, blank=True, choices=LANGUAGE_TYPE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    title = models.TextField(default='{"text":""}', max_length=100, )
    sub_title = models.CharField(default='', max_length=100, blank=True)
    content = models.CharField(default='', max_length=100, blank=True)
    type_name = models.CharField(default='', max_length=100)
    color = models.CharField(default='#AABBCC', max_length=10)

    def __str__(self):
        return str(self.title) + ' : ' + str(self.language_type)

    class Meta:
        ordering = ('-id',)


class EventInformation(models.Model):
    LANGUAGE_TYPE = ((0, 'ENGLISH'), (1, 'CHINESE'))
    language_type = models.IntegerField(default=0, blank=True, choices=LANGUAGE_TYPE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.IntegerField(default=0, null=False, blank=True)
    hub_id = models.IntegerField(default=1, null=False, blank=True)
    type = models.IntegerField(null=False, blank=True)
    main_image = models.CharField(default='', max_length=100, null=False, blank=True)
    main_list_image = models.CharField(default='', max_length=100, null=False, blank=True)
    promotion_list_image = models.CharField(default='', max_length=100, null=False, blank=True)
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
        return str(self.event.name) + ' : ' + str(self.language_type)

    class Meta:
        ordering = ('-id',)


class EventReward(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    probability = models.FloatField(default=0.0, null=False, blank=False)

    def __str__(self):
        return str(self.event.name) + ' : ' + str(self.reward.name) + ' : ' + str(self.probability)

    class Meta:
        ordering = ('-id',)


class EventHistory(models.Model):
    event_id = models.IntegerField(null=False)
    open_id = models.CharField(default='', max_length=100)
    issue_date = models.DateField(default=timezone.now)
    issue_time = models.TimeField(default=timezone.now)
    random_number = models.IntegerField(default=0)
    reward_id = models.IntegerField(null=False)

    def __str__(self):
        return str(self.event_id)

    class Meta:
        ordering = ('-id',)


class ReferralInformation(models.Model):
    referral_type = models.IntegerField(default=0)
    event_name = models.CharField(default='', max_length=100, null=True, blank=True)
    reward_id = models.IntegerField(default=0)
    reward_count = models.IntegerField(default=0)
    reward_sequence = models.IntegerField(default=0)
    issue_available = models.BooleanField(default=False)
    issue_complete = models.BooleanField(default=False)

    def __str__(self):
        return '{} : {}'.format(self.referral_type, self.event_name)

    class Meta:
        ordering = ('reward_sequence', )


class ReferralEvent(models.Model):
    open_id = models.CharField(max_length=128, unique=True, null=False)
    share_id = models.CharField(max_length=8, unique=True, blank=True)
    invitation_url = models.CharField(default='http://intro.viastelle.com/', max_length=100, null=True, blank=True)
    has_invitation_image = models.BooleanField(default=False, blank=True)
    invitation_image = models.CharField(default='', max_length=100, null=True, blank=True)
    invitation_thumbnail = models.CharField(default='', max_length=100, null=True, blank=True)
    register_date = models.DateField(auto_now_add=True)
    friend_membership_count = models.IntegerField(default=0, null=True, blank=True)
    friend_membership_reward_count = models.IntegerField(default=0, null=True, blank=True)
    friend_membership_rest_count = models.IntegerField(default=0, null=True, blank=True)
    friend_membership_over = models.BooleanField(default=False, blank=True)
    friend_coupon_status = models.TextField(default='[]', max_length=1000, null=True, blank=True)
    first_purchase_count = models.IntegerField(default=0, null=True, blank=True)
    first_purchase_reward_count = models.IntegerField(default=0, null=True, blank=True)
    first_purchase_rest_count = models.IntegerField(default=0, null=True, blank=True)
    first_coupon_status = models.TextField(default='[]', max_length=500, null=True, blank=True)
    first_coupon_available = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return '{} : {}'.format(self.open_id, self.share_id)

    class Meta:
        ordering = ('-id',)
