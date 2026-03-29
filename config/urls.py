from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from inventory.views import (
    AppLoginView, dashboard, product_list, order_list, delivery_list, issue_list,
    product_create, order_create, delivery_create, issue_create,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', AppLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', dashboard, name='dashboard'),
    path('products/', product_list, name='product_list'),
    path('products/add/', product_create, name='product_create'),
    path('orders/', order_list, name='order_list'),
    path('orders/add/', order_create, name='order_create'),
    path('deliveries/', delivery_list, name='delivery_list'),
    path('deliveries/add/', delivery_create, name='delivery_create'),
    path('issues/', issue_list, name='issue_list'),
    path('issues/add/', issue_create, name='issue_create'),
]
