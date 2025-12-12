import django_filters
from django.db.models import Q
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Name (contains)'
    )
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        label='Email (contains)'
    )
    created_at_gte = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created after'
    )
    created_at_lte = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created before'
    )
    phone_pattern = django_filters.CharFilter(
        method='filter_phone_pattern',
        label='Phone starts with'
    )

    def filter_phone_pattern(self, queryset, name, value):
        return queryset.filter(phone__startswith=value)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at_gte', 'created_at_lte', 'phone_pattern']


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Name (contains)'
    )
    price_gte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Price from'
    )
    price_lte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Price to'
    )
    stock_gte = django_filters.NumberFilter(
        field_name='stock',
        lookup_expr='gte',
        label='Stock at least'
    )
    stock_lte = django_filters.NumberFilter(
        field_name='stock',
        lookup_expr='lte',
        label='Stock at most'
    )
    low_stock = django_filters.BooleanFilter(
        method='filter_low_stock',
        label='Low stock (< 10)'
    )

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

    class Meta:
        model = Product
        fields = ['name', 'price_gte', 'price_lte', 'stock_gte', 'stock_lte', 'low_stock']


class OrderFilter(django_filters.FilterSet):
    total_amount_gte = django_filters.NumberFilter(
        field_name='total_amount',
        lookup_expr='gte',
        label='Total from'
    )
    total_amount_lte = django_filters.NumberFilter(
        field_name='total_amount',
        lookup_expr='lte',
        label='Total to'
    )
    order_date_gte = django_filters.DateTimeFilter(
        field_name='order_date',
        lookup_expr='gte',
        label='Ordered after'
    )
    order_date_lte = django_filters.DateTimeFilter(
        field_name='order_date',
        lookup_expr='lte',
        label='Ordered before'
    )
    customer_name = django_filters.CharFilter(
        field_name='customer__name',
        lookup_expr='icontains',
        label='Customer name (contains)'
    )
    product_name = django_filters.CharFilter(
        field_name='products__name',
        lookup_expr='icontains',
        label='Product name (contains)'
    )
    product_id = django_filters.NumberFilter(
        field_name='products__id',
        label='Product ID'
    )

    class Meta:
        model = Order
        fields = [
            'total_amount_gte', 'total_amount_lte',
            'order_date_gte', 'order_date_lte',
            'customer_name', 'product_name', 'product_id'
        ]
