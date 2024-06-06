from django.contrib import admin
from mpesa.models import STKTransaction, B2CTransaction

@admin.register(STKTransaction)
class STKTransactionModelAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "checkout_request_id", "amount", "receipt_no", "status")
    list_filter = ("status",)
    search_fields = ("phone_number", "transaction_no")
