from django.contrib import admin
from .models import Bank, Customer, BankAccount, CreditCard, Loan, PaymentHistory, CibilScore, CibilReport

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)

admin.site.register(Customer)
admin.site.register(BankAccount)
admin.site.register(CreditCard)
admin.site.register(Loan)
admin.site.register(PaymentHistory)
admin.site.register(CibilScore)
admin.site.register(CibilReport)
