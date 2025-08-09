from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock, name='stock'),
    path('add-stock/', views.add_stock, name='add-stock'),
    path('edit-stock/', views.edit_stock, name='edit-stock'),
    path('get-stocks/', views.get_stocks, name='get-stocks'),
    path('delete-stock/', views.delete_stock, name='delete-stock'),
    path('search-stock/', views.search_stock, name='search-stock'),
]
