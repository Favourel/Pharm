from django.urls import path
from . import views as product_view

urlpatterns = [
    path('', product_view.home_page, name='home'),
    path('products/', product_view.products_view, name='products'),
    path('product/<uuid:pk>/', product_view.product_detail, name='product-detail'),
    path('add_to_cart/', product_view.add_to_cart, name='add_to_cart'),
    path("<uuid:pk>/delete_from_checkout/", product_view.delete_from_checkout, name="delete_from_checkout"),

    path("checkout/", product_view.checkout, name="checkout"),
    path("process/order/", product_view.process_order, name="process_order"),

]