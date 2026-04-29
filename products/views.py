 
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/products/          — list all products
    GET  /api/products/?search=tomato  — search by name
    GET  /api/products/?category=vegetables — filter by category
    POST /api/products/          — farmer creates product
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')

        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        # Filter by category
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
    GET    /api/products/{id}/  — product detail
    PUT    /api/products/{id}/  — farmer updates product
    DELETE /api/products/{id}/  — farmer deletes product
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context