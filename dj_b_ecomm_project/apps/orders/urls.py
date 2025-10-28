from django.urls import path
from . import views

urlpatterns = [
    path("my-orders/", views.my_orders_view, name="my_orders"),
    path('place-order/', views.place_order_view, name='place_order'),
    path('delete/<int:order_id>/', views.delete_order, name='delete_order'),
   path('update-ordered-product/<int:product_id>/', views.update_ordered_product_view, name='update_ordered_product_view'),
   path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('order-products/<int:order_id>/', views.order_products_view, name='order_products_view'),
]
