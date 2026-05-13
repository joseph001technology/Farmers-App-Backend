## products/views.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Product
from .serializers import ProductSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/products/                     — list all (public, no auth needed)
    GET  /api/products/?search=tomato       — search by name
    GET  /api/products/?category=vegetables — filter by category
    POST /api/products/                     — farmer creates product (auth required)
    """
    serializer_class   = ProductSerializer
    # Read is public so Flutter can fetch products + farmer info without a token
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = (Product.objects
                    .select_related('farmer__profile')   # single JOIN — no N+1 queries
                    .order_by('-created_at'))

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        category = self.request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)

        return queryset

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/products/{id}/  — product detail (public)
    PUT    /api/products/{id}/  — farmer updates product (auth required)
    DELETE /api/products/{id}/  — farmer deletes product (auth required)
    """
    queryset           = Product.objects.select_related('farmer__profile').all()
    serializer_class   = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context