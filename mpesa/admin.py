from django.contrib import admin
from mpesa.models import STKTransaction, B2CTransaction, B2BTransaction

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


@admin.register(B2BTransaction)
class B2BTransactionModelAdmin(admin.ModelAdmin):
    list_display = (
        "conversation_id",  "transaction_id", "paybill_number", "account_reference", "transaction_amount"
    )
    list_filter = ("status",)
    search_fields = ("paybill_number", "transaction_id",)
