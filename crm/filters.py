import django_filters
from django_filters import FilterSet, CharFilter, NumberFilter, DateTimeFilter, BooleanFilter
from .models import Customer, Product, Order

class CustomerFilter(FilterSet):
    # Basic text filters
    name = CharFilter(lookup_expr='icontains', help_text="Filter by name (case-insensitive partial match)")
    email = CharFilter(lookup_expr='icontains', help_text="Filter by email (case-insensitive partial match)")
    
    # Date range filters
    created_at_gte = DateTimeFilter(field_name='created_at', lookup_expr='gte', help_text="Created after this date")
    created_at_lte = DateTimeFilter(field_name='created_at', lookup_expr='lte', help_text="Created before this date")
    
    # Custom phone pattern filter
    phone_pattern = CharFilter(method='filter_phone_pattern', help_text="Filter by phone pattern (e.g., '+1' for US numbers)")
    
    class Meta:
        model = Customer
        fields = {
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'created_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_phone_pattern(self, queryset, name, value):
        """Custom filter for phone patterns (e.g., starts with +1)"""
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset

class ProductFilter(FilterSet):
    # Text filters
    name = CharFilter(lookup_expr='icontains', help_text="Filter by product name (case-insensitive)")
    
    # Price range filters
    price_gte = NumberFilter(field_name='price', lookup_expr='gte', help_text="Minimum price")
    price_lte = NumberFilter(field_name='price', lookup_expr='lte', help_text="Maximum price")
    
    # Stock filters
    stock_gte = NumberFilter(field_name='stock', lookup_expr='gte', help_text="Minimum stock quantity")
    stock_lte = NumberFilter(field_name='stock', lookup_expr='lte', help_text="Maximum stock quantity")
    stock_exact = NumberFilter(field_name='stock', lookup_expr='exact', help_text="Exact stock quantity")
    
    # Custom low stock filter
    low_stock = BooleanFilter(method='filter_low_stock', help_text="Filter products with low stock (< 10)")
    
    class Meta:
        model = Product
        fields = {
            'name': ['exact', 'icontains'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
        }
    
    def filter_low_stock(self, queryset, name, value):
        """Filter products with low stock (< 10)"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

class OrderFilter(FilterSet):
    # Amount range filters
    total_amount_gte = NumberFilter(field_name='total_amount', lookup_expr='gte', help_text="Minimum order total")
    total_amount_lte = NumberFilter(field_name='total_amount', lookup_expr='lte', help_text="Maximum order total")
    
    # Date range filters
    order_date_gte = DateTimeFilter(field_name='order_date', lookup_expr='gte', help_text="Orders after this date")
    order_date_lte = DateTimeFilter(field_name='order_date', lookup_expr='lte', help_text="Orders before this date")
    
    # Related field filters (customer)
    customer_name = CharFilter(field_name='customer__name', lookup_expr='icontains', help_text="Filter by customer name")
    customer_email = CharFilter(field_name='customer__email', lookup_expr='icontains', help_text="Filter by customer email")
    
    # Related field filters (products)
    product_name = CharFilter(field_name='products__name', lookup_expr='icontains', help_text="Filter by product name")
    product_id = NumberFilter(field_name='products__id', help_text="Filter orders containing specific product ID")
    
    # Custom filters
    high_value_order = BooleanFilter(method='filter_high_value', help_text="Filter high-value orders (> $500)")
    
    class Meta:
        model = Order
        fields = {
            'total_amount': ['exact', 'gte', 'lte'],
            'order_date': ['exact', 'gte', 'lte'],
            'customer': ['exact'],
        }
    
    def filter_high_value(self, queryset, name, value):
        """Filter high-value orders (> $500)"""
        if value:
            return queryset.filter(total_amount__gt=500)
        return queryset

