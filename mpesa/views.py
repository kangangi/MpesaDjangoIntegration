import json

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from mpesa.gateway.express import Express
from mpesa.gateway.b2b import B2B
from mpesa.gateway.b2c import B2C
from mpesa.gateway.c2b import C2B
from mpesa.serializers import (
    STKTransactionSerializer, STKCheckoutSerializer, B2CCheckoutSerializer, B2CTransactionSerializer,
    B2BCheckoutSerializer, B2BTransactionSerializer
)

class STKCheckout(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = STKCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        express = Express()
        response = express.stk_push(request=request, **serializer.validated_data)
        return Response(response)


class STKCallBack(APIView):
    permission_classes = (AllowAny, )

    def get(self):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.body
        express = Express()
        response = express.stk_callback_handler(json.loads(data))
        return Response(STKTransactionSerializer(response).data, status=status.HTTP_200_OK)


class B2CCheckout(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = B2CCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        b2c = B2C()
        response = b2c.b2c_send(request=request, **serializer.validated_data)
        return Response(response)


class B2CCallBack(APIView):
    permission_classes = (AllowAny, )

    def get(self):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.body
        b2c = B2C()
        response = b2c.b2c_callback_handler(json.loads(data))
        return Response(B2CTransactionSerializer(response).data, status=status.HTTP_200_OK)


class C2BConfirmationCallBack(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.body
        c2b = C2B()
        response = c2b.confirmation_handler(json.loads(data))
        return Response(B2CTransactionSerializer(response).data, status=status.HTTP_200_OK)


class B2BCheckout(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = B2BCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        b2b = B2B()
        response = b2b.b2b_send(request=request, **serializer.validated_data)
        return Response(response)


class B2BCallBack(APIView):
    permission_classes = (AllowAny, )

    def get(self):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.body
        b2b = B2B()
        response = b2b.b2b_callback_handler(json.loads(data))
        return Response(B2BTransactionSerializer(response).data, status=status.HTTP_200_OK)
