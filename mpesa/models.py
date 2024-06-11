import uuid

from django.db import models

from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

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
    ip = models.CharField(max_length=200, blank=True, null=True)
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
    working_account_balance = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    utility_account_balance = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    transaction_time = models.DateTimeField(null=True, blank=True)
    recipient_phonenumber = PhoneNumberField(null=True, blank=True)
    recipient_public_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default=1)
    ip = models.CharField(max_length=200, blank=True, null=True)
    occassion = models.CharField(max_length=200, blank=True, null=True)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    originator_conversation_id = models.CharField(max_length=255, unique=True, default=uuid.uuid4, blank=True)

    class Meta:
        verbose_name = _('B2CTransaction')
        verbose_name_plural = _('B2CTransactions')
