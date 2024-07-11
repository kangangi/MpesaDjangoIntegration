import uuid

from django.db import models

from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class STKTransaction(BaseModel):
    STATUS = ((0, "Complete"), (1, "Pending"),)
    phone_number = PhoneNumberField()
    checkout_request_id = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    amount = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS, default=1)
    receipt_no = models.CharField(max_length=200, blank=True, null=True)
    ip_address = models.CharField(max_length=200, blank=True, null=True)
    transaction_date = models.CharField(max_length=200, blank=True, null=True)
    reference = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = _("STKTransaction")
        verbose_name_plural = _("STKTransactions")

class B2CTransaction(BaseModel):
    STATUS = ((0, "Complete"), (1, "Pending"),)
    conversation_id = models.CharField(max_length=255, unique=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    transaction_amount = models.PositiveIntegerField(null=True, blank=True)
    working_account_balance = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    utility_account_balance = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    transaction_time = models.DateTimeField(null=True, blank=True)
    recipient_phonenumber = PhoneNumberField(null=True, blank=True)
    recipient_public_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default=1)
    ip_address = models.CharField(max_length=200, blank=True, null=True)
    occassion = models.CharField(max_length=200, blank=True, null=True)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    is_recipient_registered_customer = models.BooleanField(blank=True, null=True)
    charges_paid_available_balance = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    originator_conversation_id = models.CharField(max_length=255, unique=True, default=uuid.uuid4, blank=True)

    class Meta:
        verbose_name = _('B2CTransaction')
        verbose_name_plural = _('B2CTransactions')


class B2BTransaction(BaseModel):
    STATUS = ((0, "Complete"), (1, "Pending"),)
    conversation_id = models.CharField(max_length=255, unique=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    status = models.CharField(max_length=10, choices=STATUS, default=1)
    ip_address = models.CharField(max_length=200, blank=True, null=True)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    originator_conversation_id = models.CharField(max_length=255, unique=True, default=uuid.uuid4, blank=True)
    amount = models.IntegerField()
    debit_account_balance = models.CharField(max_length=255, null=True, blank=True)
    debit_party_affected_account_balance = models.CharField(max_length=255, null=True, blank=True)
    debit_party_charges = models.IntegerField( null=True, blank=True)
    transaction_time = models.DateTimeField(null=True, blank=True)
    recipient_public_name = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    paybill_number = models.IntegerField(null=True, blank=True)
    account_reference = models.CharField(max_length=255, null=True, blank=True)
    initiator_account_current_balance = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _('B2BTransaction')
        verbose_name_plural = _('B2BTransactions')


class B2CTopup(BaseModel):
    STATUS = ((0, "Complete"), (1, "Pending"),)
    transaction_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    status = models.CharField(max_length=10, choices=STATUS, default=1)
    originator_conversation_id = models.CharField(max_length=255, blank=True, null=True)
    bill_reference_number = models.CharField(max_length=255, blank=True, null=True)
    debit_account_balance = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    transaction_time = models.DateTimeField(null=True, blank=True)
    amount = models.IntegerField()
    debit_party_charges = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    receiver_public_name = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=50, null=True, blank=True)
    requester = PhoneNumberField(blank=True, null=True)
    ip_address = models.CharField(max_length=200, blank=True, null=True)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    initiator_account_current_balance = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = _('B2CTopup')
        verbose_name_plural = _('B2CTopups')
