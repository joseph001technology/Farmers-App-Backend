## users/urls.py
## Replace your existing urls.py with this

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, ProfileView,
    PublicFarmerProfileView, PublicFarmerListView,
)

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(),      name='register'),
    path('login/',    LoginView.as_view(),          name='login'),
    path('refresh/',  TokenRefreshView.as_view(),   name='token_refresh'),

    # Own profile (authenticated)
    path('profile/',  ProfileView.as_view(),        name='profile'),

    # Public farmer endpoints (no auth)
    path('farmers/',              PublicFarmerListView.as_view(),              name='farmer-list'),
    path('farmer/<int:farmer_id>/', PublicFarmerProfileView.as_view(),         name='farmer-detail'),
]