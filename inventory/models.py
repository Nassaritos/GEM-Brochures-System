from django.db import models
from django.db.models import Sum
from decimal import Decimal


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('brochure', 'Brochure'),
        ('flyer', 'Flyer'),
        ('leaflet', 'Leaflet'),
        ('map', 'Map'),
        ('booklet', 'Booklet'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='brochure')
    reorder_level = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_delivered(self):
        return self.orders.aggregate(total=Sum('deliveries__delivered_quantity')).get('total') or 0

    @property
    def total_issued(self):
        return self.issues.aggregate(total=Sum('issued_quantity')).get('total') or 0

    @property
    def current_stock(self):
        return self.total_delivered - self.total_issued

    @property
    def stock_status(self):
        if self.current_stock <= 0:
            return 'Out of Stock'
        if self.current_stock <= self.reorder_level:
            return 'Low Stock'
        return 'In Stock'


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    print_house = models.CharField(max_length=200)
    pr_number = models.CharField(max_length=100, blank=True)
    po_number = models.CharField(max_length=100, blank=True)
    order_date = models.DateField()
    ordered_quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-order_date', '-id']

    def __str__(self):
        return f'{self.product.name} - {self.po_number or self.id}'

    @property
    def total_price(self):
        return self.ordered_quantity * self.unit_price

    @property
    def delivered_quantity(self):
        return self.deliveries.aggregate(total=Sum('delivered_quantity')).get('total') or 0

    @property
    def remaining_to_deliver(self):
        remaining = self.ordered_quantity - self.delivered_quantity
        return remaining if remaining > 0 else 0

    @property
    def order_status(self):
        if self.delivered_quantity <= 0:
            return 'Open'
        if self.delivered_quantity < self.ordered_quantity:
            return 'Partially Delivered'
        return 'Fully Delivered'


class Delivery(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries')
    delivery_date = models.DateField()
    delivered_quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-delivery_date', '-id']

    def __str__(self):
        return f'{self.order} - {self.delivered_quantity}'


class Issue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='issues')
    issue_date = models.DateField()
    issued_quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        return f'{self.product.name} - {self.issued_quantity}'
