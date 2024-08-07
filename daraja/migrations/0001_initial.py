# Generated by Django 5.0.6 on 2024-07-22 14:11

import phonenumber_field.modelfields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='B2BTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('conversation_id', models.CharField(max_length=255, unique=True)),
                ('transaction_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('status', models.CharField(choices=[(0, 'Complete'), (1, 'Pending'), (2, 'Failed')], default=1, max_length=10)),
                ('ip_address', models.CharField(blank=True, max_length=200, null=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('originator_conversation_id', models.CharField(blank=True, default=uuid.uuid4, max_length=255, unique=True)),
                ('amount', models.IntegerField()),
                ('debit_account_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('debit_party_charges', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('transaction_time', models.DateTimeField(blank=True, null=True)),
                ('recipient_public_name', models.CharField(blank=True, max_length=255, null=True)),
                ('currency', models.CharField(blank=True, max_length=255, null=True)),
                ('recipient_number', models.IntegerField(blank=True, null=True)),
                ('account_reference', models.CharField(blank=True, max_length=255, null=True)),
                ('initiator_account_current_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('recipient_type', models.CharField(choices=[('paybill', 'PayBill'), ('buygoods', 'BuyGoods')], max_length=20)),
                ('requester', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('failure_description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'B2BTransaction',
                'verbose_name_plural': 'B2BTransactions',
            },
        ),
        migrations.CreateModel(
            name='B2CTopup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('transaction_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('status', models.CharField(choices=[(0, 'Complete'), (1, 'Pending'), (2, 'Failed')], default=1, max_length=10)),
                ('conversation_id', models.CharField(blank=True, max_length=255, null=True)),
                ('debit_account_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('transaction_time', models.DateTimeField(blank=True, null=True)),
                ('amount', models.IntegerField()),
                ('debit_party_charges', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('receiver_public_name', models.CharField(blank=True, max_length=255, null=True)),
                ('currency', models.CharField(blank=True, max_length=50, null=True)),
                ('requester', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('ip_address', models.CharField(blank=True, max_length=200, null=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('initiator_account_current_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('paybill_number', models.CharField(max_length=50)),
                ('account_reference', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'B2CTopup',
                'verbose_name_plural': 'B2CTopups',
            },
        ),
        migrations.CreateModel(
            name='B2CTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('conversation_id', models.CharField(max_length=255, unique=True)),
                ('transaction_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('transaction_amount', models.PositiveIntegerField(blank=True, null=True)),
                ('working_account_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('utility_account_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('transaction_time', models.DateTimeField(blank=True, null=True)),
                ('recipient_phonenumber', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('recipient_public_name', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[(0, 'Complete'), (1, 'Pending'), (2, 'Failed')], default=1, max_length=10)),
                ('ip_address', models.CharField(blank=True, max_length=200, null=True)),
                ('occasion', models.CharField(blank=True, max_length=200, null=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('is_recipient_registered_customer', models.BooleanField(blank=True, null=True)),
                ('charges_paid_available_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('originator_conversation_id', models.CharField(blank=True, default=uuid.uuid4, max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'B2CTransaction',
                'verbose_name_plural': 'B2CTransactions',
            },
        ),
        migrations.CreateModel(
            name='STKTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('checkout_request_id', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('amount', models.IntegerField()),
                ('status', models.CharField(choices=[(0, 'Complete'), (1, 'Pending')], default=1, max_length=10)),
                ('receipt_no', models.CharField(blank=True, max_length=200, null=True)),
                ('ip_address', models.CharField(blank=True, max_length=200, null=True)),
                ('transaction_date', models.CharField(blank=True, max_length=200, null=True)),
                ('reference', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'STKTransaction',
                'verbose_name_plural': 'STKTransactions',
            },
        ),
    ]
