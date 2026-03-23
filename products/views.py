from django.http import JsonResponse
from rest_framework import generics, permissions
from .models import Product
from .serializers import ProductSerializer

# def product_list(request):
#     products = Product.objects.all()
    
#     data = []
#     for product in products:
#         data.append({
#             'id': product.id,
#             'name': product.name,
#             'price': str(product.price),
#             'image': request.build_absolute_uri(product.image.url) if product.image else ""
#         })
    
#     return JsonResponse(data, safe=False)

# 🔹 GET all products + POST new product
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        # Automatically assign logged-in user as farmer
        serializer.save(farmer=self.request.user)


# 🔹 GET single product
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer