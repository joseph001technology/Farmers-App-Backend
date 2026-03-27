from django.urls import path
from .views import CheckoutView, OrderListCreateView, OrderDetailView

 
urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]