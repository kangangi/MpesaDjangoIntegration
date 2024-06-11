from django.contrib import admin
from mpesa.models import STKTransaction, B2CTransaction

@admin.register(STKTransaction)
class STKTransactionModelAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "checkout_request_id", "amount", "receipt_no",)
    list_filter = ("status",)
    search_fields = ("phone_number", "transaction_no",)

@admin.register(B2CTransaction)
class B2CTransactionModelAdmin(admin.ModelAdmin):
    list_display = (
        "conversation_id",  "transaction_id", "recipient_phonenumber", "recipient_public_name", "transaction_amount"
    )
    list_filter = ("status",)
    search_fields = ("recipient_phone_number", "transaction_id",)
