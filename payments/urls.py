from django.urls import path
from .views import MpesaSTKPushView, mpesa_callback

urlpatterns = [
    path('mpesa/stk-push/', MpesaSTKPushView.as_view(), name='mpesa-stk-push'),
    path('mpesa/callback/', mpesa_callback, name='mpesa-callback'),
]