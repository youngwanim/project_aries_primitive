from django.contrib import admin
from .models import Restaurant, Menu, Hub, Product, ExpertReview, MenuReviewStatics, \
    RestaurantBrandInfo, HubStock, MenuPairingInformation, ProductType

admin.site.register(Restaurant)
admin.site.register(RestaurantBrandInfo)
admin.site.register(Menu)
admin.site.register(MenuReviewStatics)
admin.site.register(Hub)
admin.site.register(HubStock)
admin.site.register(Product)
admin.site.register(ProductType)
admin.site.register(ExpertReview)
admin.site.register(MenuPairingInformation)
