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
    paybill_num = serializers.IntegerField()
    account_num = serializers.CharField(),
    remarks = serializers.CharField(required=False)
    phone_number = PhoneNumberField(required=False)

    def validate(self, attrs):
        phone_number = attrs.pop("phone_number")
        if phone_number:
            attrs["phone_number"] = str(phone_number)[1:]
        remarks = attrs.get("remarks", )
        amount = attrs.get("amount")
        if remarks == "":
            attrs["remarks"] = "{}-{}".format(phone_number, amount)
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
