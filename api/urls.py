from .views import api_root
from django.urls import path, include

urlpatterns = [
    path('', api_root),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('users/', include('users.urls')),
    path('ratings/', include('ratings.urls')),
    path('dashboard/', include('dashboard.urls')),
]