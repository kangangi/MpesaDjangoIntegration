from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from daraja.models import STKTransaction, B2CTransaction, B2BTransaction

class STKTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = STKTransaction
        fields = "__all__"

class STKCheckoutSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    amount = serializers.IntegerField(min_value=1)
    reference = serializers.CharField(default="")
    description = serializers.CharField(default="")

    def validate(self, attrs):
        phone_number = attrs.pop("phone_number")
        attrs["phone_number"] = str(phone_number)[1:]
        reference = attrs.get("reference", )
        description = attrs.get("description")
        amount = attrs.get("amount")
        if reference == "":
            attrs["reference"] = "{}-{}".format(phone_number, amount)
        if description == "":
            attrs["description"] = "{}-{}".format(phone_number, amount)
        return attrs


class B2CCheckoutSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    amount = serializers.IntegerField(min_value=1)
    remarks = serializers.CharField(default="")
    occasion = serializers.CharField(default="")

    def validate(self, attrs):
        phone_number = attrs.pop("phone_number")
        attrs["phone_number"] = str(phone_number)[1:]
        remarks = attrs.get("remarks", )
        occasion = attrs.get("occasion")
        amount = attrs.get("amount")
        if remarks == "":
            attrs["remarks"] = "{}-{}".format(phone_number, amount)
        if occasion == "":
            attrs["occasion"] = "{}-{}".format(phone_number, amount)
        return attrs

class B2BTransactionSerializer(serializers.Serializer):

    class Meta:
        model = B2BTransaction
        fields = "__all__"

class B2BCheckoutSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)
    recipient_type = serializers.ChoiceField(choices=['buygoods', 'paybill'])
    paybill_number = serializers.IntegerField(required=False)
    account_reference = serializers.CharField(required=False)
    till_number = serializers.IntegerField(required=False)
    remarks = serializers.CharField(required=False)
    phone_number = PhoneNumberField(required=False)

    def validate(self, attrs):
        phone_number = attrs.pop("phone_number", None)
        paybill_number = attrs.pop("paybill_number", None)
        till_number = attrs.pop("till_number", None)
        account_reference = attrs.get("account_reference", None)
        recipient_type = attrs.get('recipient_type')

        if recipient_type == 'buygoods':
            if not till_number:
                raise ValidationError("till_number must be provided for buygoods")
            attrs['party_b'] = till_number
        if recipient_type == 'paybill':
            if not (paybill_number or account_reference):
                raise ValidationError("paybill_number and account_reference must be provided for paybill")
            attrs['party_b'] = paybill_number
        if phone_number:
            attrs["phone_number"] = str(phone_number)[1:]
        remarks = attrs.pop("remarks", None )
        amount = attrs.get("amount")
        if not remarks:
            attrs["remarks"] = "{}-{}".format(till_number if till_number else paybill_number, amount)

        from pprint import pprint
        pprint(attrs)
        return attrs


class DynamicQRInputSerializer(serializers.Serializer):
    trx_code_mapping = {
        "BuyGoods": "BG",
        "PayBill": "PB",
        "SendMoney": "SM",
        "Withdraw": "WA",
        "SendToBusiness": "SB"

    }

    merchant_name = serializers.CharField()
    reference = serializers.CharField()
    amount = serializers.IntegerField()
    transaction_type = serializers.ChoiceField(
        choices=["BuyGoods", "PayBill", "SendMoney", "Withdraw", "SentToBusiness"]
    )
    party_identifier = serializers.CharField(required=False)
    phone_number = PhoneNumberField(required=False)

    def validate(self, attrs):
        transaction_type = attrs.pop('transaction_type',)
        attrs['transaction_type'] = self.trx_code_mapping.get(transaction_type)

        phone_number = attrs.pop('phone_number', None)
        party_identifier = attrs.get("party_identifier")
        if transaction_type in ["SendMoney", "SentToBusiness"]:
            if not phone_number:
                raise ValidationError("phone_number must be provided for SendMoney and SendToBusiness")
            else:
                attrs["party_identifier"] = str(phone_number)[1:]
        else:
            if not party_identifier:
                raise ValidationError("Agent Till, Paybill or Merchant BuyGoods must be provided as a party_identifier")

        return attrs


class B2CTopupInputSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    paybill_number = serializers.IntegerField()
    remarks = serializers.CharField()
    requester_phone_number = PhoneNumberField(required=False)
    account_reference = serializers.CharField(required=False)

    def validate(self, attrs):
        phone_number = attrs.pop("phone_number", None)
        if phone_number:
            attrs["phone_number"] = str(phone_number)[1:]
        return attrs

class B2BExpressCheckoutSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    receiver_short_code = serializers.IntegerField()
    reference = serializers.CharField()

    def validate(self, attrs):
        reference = attrs.pop("reference")
        attrs["reference"] = reference.replace(" ", "")
        return attrs
