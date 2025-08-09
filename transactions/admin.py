from .models import Supplier, PurchaseBill, PurchaseItem, PurchaseBillDetails, SaleBill, SaleItem, SaleBillDetails, Customer
from django.contrib import admin

admin.site.register(Supplier)
admin.site.register(PurchaseBill)
admin.site.register(PurchaseItem)
admin.site.register(PurchaseBillDetails)
admin.site.register(SaleBill)
admin.site.register(SaleItem)
admin.site.register(SaleBillDetails)
admin.site.register(Customer)
