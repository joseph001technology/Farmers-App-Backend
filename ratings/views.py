from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Rating
from .serializers import RatingSerializer, FarmerRatingSummarySerializer

User = get_user_model()


class CreateRatingView(generics.CreateAPIView):
    """
    POST /api/ratings/
    Consumer submits a star rating + optional review after
    an order is marked as delivered.
    Body: { farmer, order, stars, review }
    """
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(consumer=self.request.user)


class FarmerRatingsListView(APIView):
    """
    GET /api/ratings/farmer/{farmer_id}/
    Returns all ratings for a specific farmer plus
    their average star rating.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, farmer_id):
        farmer = get_object_or_404(User, id=farmer_id, role='farmer')
        ratings = Rating.objects.filter(farmer=farmer)
        avg = ratings.aggregate(avg=Avg('stars'))['avg'] or 0.0
        total = ratings.count()

        serialized = RatingSerializer(ratings, many=True)
        return Response({
            'farmer_id': farmer.id,
            'farmer_name': farmer.username,
            'average_stars': round(avg, 1),
            'total_ratings': total,
            'ratings': serialized.data,
        })


class MyRatingsView(generics.ListAPIView):
    """
    GET /api/ratings/mine/
    Returns all ratings the authenticated consumer has submitted.
    """
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(consumer=self.request.user)