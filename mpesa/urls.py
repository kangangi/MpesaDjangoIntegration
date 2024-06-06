from django.urls import path

from mpesa.views import STKCheckout, STKCallBack, B2CCheckout, B2CCallBack

urlpatterns = [
    path("stk/", STKCheckout.as_view(), name="stk checkout"),
    path("stk/callback/", STKCallBack.as_view(), name="stk call back"),
    path("b2c/", B2CCheckout.as_view(), name="b2c send money"),
    path("b2c/callback/", B2CCallBack.as_view(), name='b2c call back')
]
