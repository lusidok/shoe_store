from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('add/', views.order_add, name='order_add'),
    path('edit/<int:pk>/', views.order_edit, name='order_edit'),
    path('delete/<int:pk>/', views.order_delete, name='order_delete'),
]