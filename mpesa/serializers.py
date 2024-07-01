from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from mpesa.models import STKTransaction, B2CTransaction, B2BTransaction

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


class B2CTransactionSerializer(serializers.Serializer):

    class Meta:
        model = B2CTransaction
        fields = "__all__"

class B2CCheckoutSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    amount = serializers.IntegerField(min_value=1)
    remarks = serializers.CharField(default="")
    occassion = serializers.CharField(default="")

    def validate(self, attrs):
        phone_number = attrs.pop("phone_number")
        attrs["phone_number"] = str(phone_number)[1:]
        remarks = attrs.get("remarks", )
        occasion = attrs.get("occasion")
        amount = attrs.get("amount")
        if remarks == "":
            attrs["remarks"] = "{}-{}".format(phone_number, amount)
        if occasion == "":
            attrs["occassion"] = "{}-{}".format(phone_number, amount)
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


