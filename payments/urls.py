from django.urls import path
from .views import MpesaSTKPushView, mpesa_callback

urlpatterns = [
    path('stk-push/', MpesaSTKPushView.as_view()),
    path('callback/', mpesa_callback),
]