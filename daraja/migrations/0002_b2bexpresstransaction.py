# Generated by Django 5.0.6 on 2024-08-26 11:34

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daraja', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='B2BExpressTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ip_address', models.CharField(blank=True, max_length=200, null=True)),
                ('receiver_short_code', models.IntegerField()),
                ('amount', models.IntegerField()),
                ('reference', models.CharField(blank=True, max_length=200, null=True)),
                ('request_ref_id', models.CharField(blank=True, default=uuid.uuid4, max_length=255, unique=True)),
                ('result_description', models.CharField(blank=True, max_length=255, null=True)),
                ('conversation_id', models.CharField(blank=True, max_length=255, null=True)),
                ('transaction_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
            ],
            options={
                'verbose_name': 'B2BExpressTransaction',
                'verbose_name_plural': 'B2BExpressTransactions',
            },
        ),
    ]