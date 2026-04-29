# dashboard/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from django.db.models import (
    Sum, Count, Avg, Q
)
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from orders.models import Order, OrderItem
from products.models import Product

User = get_user_model()


class FarmerDashboardView(APIView):
    """
    GET /api/dashboard/farmer/

    Returns a full sales summary for the authenticated farmer.
    Only accessible by users with role = 'farmer'.

    Response includes:
    - Order counts by status
    - Total revenue from paid + delivered orders
    - Top 5 products by quantity sold
    - Revenue breakdown for the last 7 days
    - Average rating and total ratings received
    - Total products currently listed
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'farmer':
            return Response(
                {'error': 'Only farmers can access this dashboard.'},
                status=403
            )

        # ── Orders that include this farmer's products ────────────────
        orders = Order.objects.filter(
            items__product__farmer=user
        ).distinct()

        total_orders = orders.count()
        paid_orders = orders.filter(status='paid').count()
        pending_orders = orders.filter(
            status__in=['pending', 'pending_delivery']
        ).count()
        delivered_orders = orders.filter(status='delivered').count()
        cancelled_orders = orders.filter(status='cancelled').count()

        # ── Revenue (only from paid + delivered) ─────────────────────
        total_revenue = OrderItem.objects.filter(
            product__farmer=user,
            order__status__in=['paid', 'delivered']
        ).aggregate(rev=Sum('price'))['rev'] or 0

        # ── Top 5 products by quantity sold ──────────────────────────
        top_products = list(
            OrderItem.objects.filter(
                product__farmer=user
            ).values('product__name').annotate(
                total_qty=Sum('quantity'),
                total_revenue=Sum('price')
            ).order_by('-total_qty')[:5]
        )
        # Clean up key names for Flutter
        top_products = [
            {
                'name': p['product__name'],
                'quantity_sold': p['total_qty'],
                'revenue': str(p['total_revenue'] or 0),
            }
            for p in top_products
        ]

        # ── Revenue per day for last 7 days ──────────────────────────
        seven_days_ago = timezone.now().date() - timedelta(days=6)
        revenue_daily = list(
            OrderItem.objects.filter(
                product__farmer=user,
                order__status__in=['paid', 'delivered'],
                order__created_at__date__gte=seven_days_ago
            ).annotate(
                day=TruncDate('order__created_at')
            ).values('day').annotate(
                daily_revenue=Sum('price'),
                order_count=Count('order', distinct=True)
            ).order_by('day')
        )
        revenue_last_7_days = [
            {
                'date': str(r['day']),
                'revenue': str(r['daily_revenue'] or 0),
                'orders': r['order_count'],
            }
            for r in revenue_daily
        ]

        # ── Ratings ──────────────────────────────────────────────────
        try:
            from ratings.models import Rating
            rating_data = Rating.objects.filter(farmer=user).aggregate(
                avg=Avg('stars'), total=Count('id')
            )
            avg_rating = round(rating_data['avg'] or 0.0, 1)
            total_ratings = rating_data['total'] or 0
        except Exception:
            avg_rating = 0.0
            total_ratings = 0

        # ── Products listed ──────────────────────────────────────────
        total_products = Product.objects.filter(farmer=user).count()

        return Response({
            'total_orders': total_orders,
            'total_revenue': str(total_revenue),
            'paid_orders': paid_orders,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'total_products_listed': total_products,
            'average_rating': avg_rating,
            'total_ratings': total_ratings,
            'top_products': top_products,
            'revenue_last_7_days': revenue_last_7_days,
        })


class AdminDashboardView(APIView):
    """
    GET /api/dashboard/admin/

    Returns platform-wide analytics for county government
    officers or system administrators.
    Only accessible by staff/admin users.

    Response includes:
    - User counts (total, farmers, consumers)
    - Product counts by category
    - Order counts by status + total platform revenue
    - Top 5 selling products across all farmers
    - Top 5 farmers by revenue
    - Orders per day for the last 7 days
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):

        # ── Users ────────────────────────────────────────────────────
        total_users = User.objects.count()
        total_farmers = User.objects.filter(role='farmer').count()
        total_consumers = User.objects.filter(role='customer').count()

        # ── Products ─────────────────────────────────────────────────
        total_products = Product.objects.count()

        products_by_category = list(
            Product.objects.values('category').annotate(
                count=Count('id')
            ).order_by('-count')
        )
        products_by_category = [
            {'category': p['category'], 'count': p['count']}
            for p in products_by_category
        ]

        # ── Orders ───────────────────────────────────────────────────
        total_orders = Order.objects.count()
        total_revenue = OrderItem.objects.filter(
            order__status__in=['paid', 'delivered']
        ).aggregate(rev=Sum('price'))['rev'] or 0

        orders_by_status = {
            status: Order.objects.filter(status=status).count()
            for status, _ in Order.STATUS_CHOICES
        }

        # ── Top 5 selling products ────────────────────────────────────
        top_selling = list(
            OrderItem.objects.values(
                'product__name', 'product__farmer__username'
            ).annotate(
                total_qty=Sum('quantity'),
                total_rev=Sum('price')
            ).order_by('-total_qty')[:5]
        )
        top_selling_products = [
            {
                'name': p['product__name'],
                'farmer': p['product__farmer__username'],
                'quantity_sold': p['total_qty'],
                'revenue': str(p['total_rev'] or 0),
            }
            for p in top_selling
        ]

        # ── Top 5 farmers by revenue ──────────────────────────────────
        top_farmers = list(
            OrderItem.objects.filter(
                order__status__in=['paid', 'delivered']
            ).values('product__farmer__username').annotate(
                revenue=Sum('price'),
                orders=Count('order', distinct=True)
            ).order_by('-revenue')[:5]
        )
        top_farmers_by_revenue = [
            {
                'farmer': f['product__farmer__username'],
                'revenue': str(f['revenue'] or 0),
                'orders': f['orders'],
            }
            for f in top_farmers
        ]

        # ── Orders per day — last 7 days ──────────────────────────────
        seven_days_ago = timezone.now().date() - timedelta(days=6)
        daily_orders = list(
            Order.objects.filter(
                created_at__date__gte=seven_days_ago
            ).annotate(
                day=TruncDate('created_at')
            ).values('day').annotate(
                count=Count('id'),
                revenue=Sum('items__price')
            ).order_by('day')
        )
        orders_last_7_days = [
            {
                'date': str(d['day']),
                'orders': d['count'],
                'revenue': str(d['revenue'] or 0),
            }
            for d in daily_orders
        ]

        return Response({
            'total_users': total_users,
            'total_farmers': total_farmers,
            'total_consumers': total_consumers,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': str(total_revenue),
            'orders_by_status': orders_by_status,
            'top_selling_products': top_selling_products,
            'top_farmers_by_revenue': top_farmers_by_revenue,
            'products_by_category': products_by_category,
            'orders_last_7_days': orders_last_7_days,
        })