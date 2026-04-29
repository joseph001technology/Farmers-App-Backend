# dashboard/urls.py
from django.urls import path
from .views import FarmerDashboardView, AdminDashboardView

urlpatterns = [
    path('farmer/', FarmerDashboardView.as_view(), name='farmer-dashboard'),
    path('admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
]