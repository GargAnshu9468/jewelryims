from .models import Giravee, GiraveeTransaction
from django.contrib import admin


@admin.register(Giravee)
class GiraveeAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'interest_rate', 'start_date', 'is_cleared')


@admin.register(GiraveeTransaction)
class GiraveeTransactionAdmin(admin.ModelAdmin):
    list_display = ('giravee', 'amount', 'date')
