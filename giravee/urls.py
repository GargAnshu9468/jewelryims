from django.urls import path
from . import views

urlpatterns = [
    path('', views.giravee, name='giravee'),
    path('add-giravee/', views.add_giravee, name='add-giravee'),
    path('get-giravees/', views.get_giravees, name='get-giravees'),
    path('edit-giravee/', views.edit_giravee, name='edit-giravee'),
    path('delete-giravee/', views.delete_giravee, name='delete-giravee'),
    path('search-giravee/', views.search_giravee, name='search-giravee'),
    path('refresh-giravee/', views.refresh_giravee, name='refresh-giravee'),
]
