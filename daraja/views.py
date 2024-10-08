import json

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from daraja.gateway.b2b import B2B
from daraja.gateway.b2c import B2C
from daraja.gateway.c2b import C2B
from daraja.gateway.dynamicqr import DynamicQR
from daraja.serializers import (
    STKTransactionSerializer, STKCheckoutSerializer, B2CCheckoutSerializer, B2BCheckoutSerializer,
    B2BTransactionSerializer, DynamicQRInputSerializer, B2CTopupInputSerializer, B2BExpressCheckoutSerializer
)

class STKCheckout(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = STKCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        c2b = C2B()
        response = c2b.stk_push(request=request, **serializer.validated_data)
        return Response(response)


class STKCallBack(APIView):
    permission_classes = (AllowAny, )

    def get(self):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.body
        c2b = C2B()
        response = c2b.stk_callback_handler(json.loads(data))
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
        try:
            json_data = json.loads(data)
            b2c.b2c_callback_handler(json_data)
        except json.decoder.JSONDecodeError:
            return Response("Invalid json", status=status.HTTP_400_BAD_REQUEST)
        return Response("Response received", status=status.HTTP_200_OK)


class C2BConfirmationCallBack(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.body
        c2b = C2B()
        c2b.confirmation_handler(json.loads(data))
        return Response("Response received", status=status.HTTP_200_OK)


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
        try:
            json_data = json.loads(data)
            b2b.b2b_callback_handler(json_data)
        except json.decoder.JSONDecodeError:
            return Response("Invalid json", status=status.HTTP_400_BAD_REQUEST)
        return Response("Response received", status=status.HTTP_200_OK)


class DynamicQRView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = DynamicQRInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dynamic_qr = DynamicQR()
        response = dynamic_qr.generate_qr(**serializer.validated_data)
        return Response(response, status=status.HTTP_200_OK)


class B2CTopup(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = B2CTopupInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        b2c = B2C()
        response = b2c.b2c_top_up(request=request, **serializer.validated_data)
        return Response(response, status=status.HTTP_200_OK)


class B2CTopUpCallback(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        data = request.body
        b2c = B2C()
        try:
            json_data = json.loads(data)
            b2c.b2c_topup_callback_handler(json_data)
        except json.decoder.JSONDecodeError:
            return Response("Invalid json", status=status.HTTP_400_BAD_REQUEST)

        return Response("Response received", status=status.HTTP_200_OK)


class B2BExpressCheckout(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = B2BExpressCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        b2b = B2B()
        response = b2b.b2b_express_send(request=request, **serializer.validated_data)
        return Response(response)


class B2BExpressCallBack(APIView):
    permission_classes = (AllowAny, )

    def get(self):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.body
        b2b = B2B()
        try:
            json_data = json.loads(data)
            b2b.b2b_express_callback_handler(json_data)
        except json.decoder.JSONDecodeError:
            return Response("Invalid json", status=status.HTTP_400_BAD_REQUEST)
        return Response("Response received", status=status.HTTP_200_OK)