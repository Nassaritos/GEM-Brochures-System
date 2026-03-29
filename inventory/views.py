from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import group_required
from .forms import ProductForm, OrderForm, DeliveryForm, IssueForm
from .models import Product, Order, Delivery, Issue
from .utils import export_to_excel, export_to_pdf


class AppLoginView(LoginView):
    template_name = 'registration/login.html'


def _apply_product_filters(qs, request):
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    status = request.GET.get('status', '').strip()

    if q:
        qs = qs.filter(name__icontains=q)
    if category:
        qs = qs.filter(category=category)

    products = list(qs)
    if status == 'in':
        products = [p for p in products if p.stock_status == 'In Stock']
    elif status == 'low':
        products = [p for p in products if p.stock_status == 'Low Stock']
    elif status == 'out':
        products = [p for p in products if p.stock_status == 'Out of Stock']
    return products


def _apply_order_filters(qs, request):
    q = request.GET.get('q', '').strip()
    print_house = request.GET.get('print_house', '').strip()
    status = request.GET.get('status', '').strip()
    if q:
        qs = qs.filter(Q(product__name__icontains=q) | Q(pr_number__icontains=q) | Q(po_number__icontains=q))
    if print_house:
        qs = qs.filter(print_house__icontains=print_house)
    orders = list(qs)
    if status:
        orders = [o for o in orders if o.order_status == status]
    return orders


def _apply_delivery_filters(qs, request):
    q = request.GET.get('q', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    if q:
        qs = qs.filter(Q(order__product__name__icontains=q) | Q(order__po_number__icontains=q) | Q(order__pr_number__icontains=q))
    if date_from:
        qs = qs.filter(delivery_date__gte=date_from)
    if date_to:
        qs = qs.filter(delivery_date__lte=date_to)
    return qs


def _apply_issue_filters(qs, request):
    q = request.GET.get('q', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    if q:
        qs = qs.filter(product__name__icontains=q)
    if date_from:
        qs = qs.filter(issue_date__gte=date_from)
    if date_to:
        qs = qs.filter(issue_date__lte=date_to)
    return qs


@login_required
def dashboard(request):
    products = Product.objects.all()
    orders = Order.objects.all()
    total_stock_left = sum(p.current_stock for p in products)
    low_stock_products = [p for p in products if p.current_stock > 0 and p.current_stock <= p.reorder_level]
    out_of_stock_products = [p for p in products if p.current_stock <= 0]
    context = {
        'products_count': products.count(),
        'orders_count': orders.count(),
        'total_stock_left': total_stock_left,
        'low_stock_count': len(low_stock_products),
        'out_of_stock_count': len(out_of_stock_products),
        'total_delivered': Delivery.objects.aggregate(total=Sum('delivered_quantity')).get('total') or 0,
        'total_issued': Issue.objects.aggregate(total=Sum('issued_quantity')).get('total') or 0,
        'low_stock_products': low_stock_products[:10],
        'out_of_stock_products': out_of_stock_products[:10],
        'recent_deliveries': Delivery.objects.select_related('order', 'order__product')[:10],
        'recent_issues': Issue.objects.select_related('product')[:10],
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required
def product_list(request):
    products = _apply_product_filters(Product.objects.all(), request)
    if request.GET.get('export') == 'xlsx':
        rows = [[p.name, p.get_category_display(), p.reorder_level, p.total_delivered, p.total_issued, p.current_stock, p.stock_status] for p in products]
        return export_to_excel('products.xlsx', ['Product', 'Category', 'Reorder Level', 'Delivered', 'Issued', 'Current Stock', 'Status'], rows)
    if request.GET.get('export') == 'pdf':
        return export_to_pdf(request, 'inventory/export_table_pdf.html', {
            'title': 'Products Export',
            'headers': ['Product', 'Category', 'Reorder Level', 'Delivered', 'Issued', 'Current Stock', 'Status'],
            'rows': [[p.name, p.get_category_display(), p.reorder_level, p.total_delivered, p.total_issued, p.current_stock, p.stock_status] for p in products]
        }, 'products.pdf')
    return render(request, 'inventory/product_list.html', {'products': products, 'categories': Product.CATEGORY_CHOICES})


@group_required('Marketing Team')
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product created successfully.')
        return redirect('product_list')
    return render(request, 'inventory/form.html', {'title': 'Add Product', 'form': form, 'submit_label': 'Save Product'})


@group_required('Marketing Team')
def order_list(request):
    orders = _apply_order_filters(Order.objects.select_related('product').all(), request)
    if request.GET.get('export') == 'xlsx':
        rows = [[o.product.name, o.print_house, o.pr_number, o.po_number, str(o.order_date), o.ordered_quantity, float(o.unit_price), float(o.total_price), o.delivered_quantity, o.remaining_to_deliver, o.order_status] for o in orders]
        return export_to_excel('orders.xlsx', ['Product', 'Print House', 'PR', 'PO', 'Order Date', 'Ordered Qty', 'Unit Price', 'Total Price', 'Delivered Qty', 'Remaining Qty', 'Status'], rows)
    if request.GET.get('export') == 'pdf':
        return export_to_pdf(request, 'inventory/export_table_pdf.html', {
            'title': 'Orders Export',
            'headers': ['Product', 'Print House', 'PR', 'PO', 'Order Date', 'Ordered Qty', 'Unit Price', 'Total Price', 'Delivered Qty', 'Remaining Qty', 'Status'],
            'rows': [[o.product.name, o.print_house, o.pr_number, o.po_number, str(o.order_date), o.ordered_quantity, o.unit_price, o.total_price, o.delivered_quantity, o.remaining_to_deliver, o.order_status] for o in orders]
        }, 'orders.pdf')
    return render(request, 'inventory/order_list.html', {'orders': orders})


@group_required('Marketing Team')
def order_create(request):
    form = OrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Order created successfully.')
        return redirect('order_list')
    return render(request, 'inventory/form.html', {'title': 'Create Order', 'form': form, 'submit_label': 'Save Order'})


@login_required
def delivery_list(request):
    deliveries = _apply_delivery_filters(Delivery.objects.select_related('order', 'order__product').all(), request)
    if request.GET.get('export') == 'xlsx':
        rows = [[d.order.product.name, d.order.po_number, d.order.pr_number, str(d.delivery_date), d.delivered_quantity, d.notes] for d in deliveries]
        return export_to_excel('deliveries.xlsx', ['Product', 'PO', 'PR', 'Delivery Date', 'Delivered Qty', 'Notes'], rows)
    if request.GET.get('export') == 'pdf':
        return export_to_pdf(request, 'inventory/export_table_pdf.html', {
            'title': 'Deliveries Export',
            'headers': ['Product', 'PO', 'PR', 'Delivery Date', 'Delivered Qty', 'Notes'],
            'rows': [[d.order.product.name, d.order.po_number, d.order.pr_number, str(d.delivery_date), d.delivered_quantity, d.notes] for d in deliveries]
        }, 'deliveries.pdf')
    return render(request, 'inventory/delivery_list.html', {'deliveries': deliveries})


@group_required('Marketing Team')
def delivery_create(request):
    form = DeliveryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Delivery batch added successfully.')
        return redirect('delivery_list')
    return render(request, 'inventory/form.html', {'title': 'Add Delivery Batch', 'form': form, 'submit_label': 'Save Delivery'})


@login_required
def issue_list(request):
    issues = _apply_issue_filters(Issue.objects.select_related('product').all(), request)
    if request.GET.get('export') == 'xlsx':
        rows = [[i.product.name, str(i.issue_date), i.issued_quantity, i.notes] for i in issues]
        return export_to_excel('issues.xlsx', ['Product', 'Issue Date', 'Issued Qty', 'Notes'], rows)
    if request.GET.get('export') == 'pdf':
        return export_to_pdf(request, 'inventory/export_table_pdf.html', {
            'title': 'Issues Export',
            'headers': ['Product', 'Issue Date', 'Issued Qty', 'Notes'],
            'rows': [[i.product.name, str(i.issue_date), i.issued_quantity, i.notes] for i in issues]
        }, 'issues.pdf')
    return render(request, 'inventory/issue_list.html', {'issues': issues})


@group_required('Storekeeper', 'Marketing Team')
def issue_create(request):
    form = IssueForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Issue recorded successfully.')
        return redirect('issue_list')
    return render(request, 'inventory/form.html', {'title': 'Record Issue', 'form': form, 'submit_label': 'Save Issue'})
