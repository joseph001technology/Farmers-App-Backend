from django.urls import path
from .views import CreateRatingView, FarmerRatingsListView, MyRatingsView

urlpatterns = [
    path('', CreateRatingView.as_view(), name='rating-create'),
    path('farmer/<int:farmer_id>/', FarmerRatingsListView.as_view(), name='farmer-ratings'),
    path('mine/', MyRatingsView.as_view(), name='my-ratings'),
]