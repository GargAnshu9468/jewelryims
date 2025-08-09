from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    # path('activate/<str:uidb64>/<str:token>/', views.activate_account, name='activate_account'),
]
