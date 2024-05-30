from django.urls import path

from mpesa.views import STKCheckout, STKCallBack

urlpatterns = [
    path("stk/", STKCheckout.as_view(), name="checkout"),
    path("stk/callback/", STKCallBack.as_view(), name="callback"),
]
