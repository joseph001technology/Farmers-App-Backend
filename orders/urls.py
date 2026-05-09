from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    CheckoutView,
    OrderCancelView,
    OrderReceiptView,
)

urlpatterns = [
    path('',              OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/',     OrderDetailView.as_view(),     name='order-detail'),
    path('checkout/',     CheckoutView.as_view(),         name='order-checkout'),

   
    path('<int:pk>/cancel/',  OrderCancelView.as_view(),  name='order-cancel'),
    path('<int:pk>/receipt/', OrderReceiptView.as_view(), name='order-receipt'),
]