from django.contrib import admin

from aries.ucc.models import CustomerReview, ReviewItem, CurationArticle, CurationPage, DisplaySchedule, \
    CurationContent, CurationPageContent, Event, EventContent, Reward, RewardContent, EventInformation, \
    EventReward, EventHistory, ReferralEvent, ReferralInformation

# Review
admin.site.register(CustomerReview)
admin.site.register(ReviewItem)
# Curation
admin.site.register(CurationArticle)
admin.site.register(CurationContent)
admin.site.register(CurationPage)
admin.site.register(CurationPageContent)
admin.site.register(DisplaySchedule)
# Event
admin.site.register(Event)
admin.site.register(EventContent)
admin.site.register(Reward)
admin.site.register(RewardContent)
admin.site.register(EventInformation)
admin.site.register(EventReward)
admin.site.register(EventHistory)
# Referral
admin.site.register(ReferralEvent)
admin.site.register(ReferralInformation)
