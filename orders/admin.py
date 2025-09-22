from django.contrib import admin

# Register your models here.
from .models import Order,OrderItem,Discount,DiscountUsage

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Discount)
admin.site.register(DiscountUsage)