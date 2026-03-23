from django.urls import path
from .views import OrderListCreateView, OrderDetailView

urlpatterns = [
    path('', OrderListCreateView.as_view()),
    path('<int:pk>/', OrderDetailView.as_view()),
]