from django.contrib import admin

from aries.platform.models import AuthToken, AuthScope, OperationStatus, Operator, HubOperationStatus, OperationPopup

admin.site.register(AuthToken)
admin.site.register(AuthScope)
admin.site.register(OperationStatus)
admin.site.register(OperationPopup)
admin.site.register(HubOperationStatus)
admin.site.register(Operator)
