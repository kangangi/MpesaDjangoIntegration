from django.urls import path

from daraja.views import (
    STKCheckout, STKCallBack, B2CCheckout, B2CCallBack, C2BConfirmationCallBack, B2BCheckout, B2BCallBack, DynamicQRView,
    B2CTopup, B2CTopUpCallback
)

urlpatterns = [
    path("stk/", STKCheckout.as_view(), name="stk checkout"),
    path("stk/callback/", STKCallBack.as_view(), name="stk call back"),
    path("b2c/", B2CCheckout.as_view(), name="b2c send money"),
    path("b2c/callback/", B2CCallBack.as_view(), name='b2c call back'),
    path("b2b/", B2BCheckout.as_view(), name="b2b send money"),
    path("b2b/callback/", B2BCallBack.as_view(), name='b2b call back'),
    path("c2b/confirm/", C2BConfirmationCallBack.as_view()),
    path('dynamic_qr/generate/', DynamicQRView.as_view()),
    path("b2c/topup/", B2CTopup.as_view(), name="b2b send money"),
    path("b2c/topup/callback/", B2CTopUpCallback.as_view(), name='b2b call back'),
]
