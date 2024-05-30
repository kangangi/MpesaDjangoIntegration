import json

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from mpesa.gateway import MpesaGateWay
from mpesa.serializers import STKTransactionSerializer, STKCheckoutSerializer


class STKCheckout(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = STKCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mpesa = MpesaGateWay()
        response = mpesa.stk_push(request=request, **serializer.validated_data)
        return Response(response)


class STKCallBack(APIView):
    permission_classes = (AllowAny, )

    def get(self):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.body
        mpesa = MpesaGateWay()
        response = mpesa.stk_callback_handler(json.loads(data))
        return Response(TransactionSerializer(response).data, status=status.HTTP_200_OK)
