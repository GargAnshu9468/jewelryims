from django.urls import path
from . import views

urlpatterns = [

    path('suppliers/', views.suppliers, name='suppliers'),
    path('new-supplier/', views.new_supplier, name='new-supplier'),
    path('edit-supplier', views.edit_supplier, name='edit-supplier'),
    path('get-suppliers/', views.get_suppliers, name='get-suppliers'),
    path('delete-supplier/', views.delete_supplier, name='delete-supplier'),
    path('search-supplier/', views.search_supplier, name='search-supplier'),
    path('supplier-details/', views.supplier_details, name='supplier-details'),

    path('purchases/', views.purchases, name='purchases'),
    path('new-purchase/', views.new_purchase, name='new-purchase'),
    path('get-purchase/', views.get_purchase, name='get-purchase'),
    path('update-purchase/', views.update_purchase, name='update-purchase'),
    path('delete-purchase/', views.delete_purchase, name='delete-purchase'),
    path('search-purchase/', views.search_purchase, name='search-purchase'),

    path('sales/', views.sales, name='sales'),
    path('new-sale/', views.new_sale, name='new-sale'),
    path("get-sale/", views.get_sale, name="get-sale"),
    path('update-sale/', views.update_sale, name='update-sale'),
    path('delete-sale/', views.delete_sale, name='delete-sale'),
    path('search-sale/', views.search_sale, name='search-sale'),

    path('customers/', views.customers, name='customers'),
    path('new-customer/', views.new_customer, name='new-customer'),
    path("get-customers/", views.get_customers, name="get-customers"),
    path('edit-customer/', views.edit_customer, name='edit-customer'),
    path('delete-customer/', views.delete_customer, name='delete-customer'),
    path('search-customer/', views.search_customer, name='search-customer'),
    path('customer-details/', views.customer_details, name='customer-details'),
    path('customer-suggestions/', views.customer_suggestions, name='customer-suggestions'),

]
