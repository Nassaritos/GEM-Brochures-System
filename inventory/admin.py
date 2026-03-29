from django.contrib import admin
from .models import Product, Order, Delivery, Issue


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'reorder_level', 'active')
    search_fields = ('name',)
    list_filter = ('category', 'active')


class DeliveryInline(admin.TabularInline):
    model = Delivery
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'print_house', 'pr_number', 'po_number', 'order_date', 'ordered_quantity', 'unit_price')
    search_fields = ('product__name', 'pr_number', 'po_number', 'print_house')
    list_filter = ('order_date', 'print_house')
    inlines = [DeliveryInline]


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_date', 'delivered_quantity')
    search_fields = ('order__product__name', 'order__po_number', 'order__pr_number')
    list_filter = ('delivery_date',)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('product', 'issue_date', 'issued_quantity')
    search_fields = ('product__name',)
    list_filter = ('issue_date',)
