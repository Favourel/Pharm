from django.urls import path
from . import views as product_view

urlpatterns = [
    path('', product_view.home_page, name='home'),
    path('products/', product_view.products_view, name='products'),
    path('filter-products/', product_view.filter_products, name='filter_products'),

    path('product/<uuid:pk>/', product_view.product_detail, name='product-detail'),
    path('product/<uuid:pk>/modal/', product_view.product_detail_modal, name='product_detail_modal'),

    path("product/<uuid:pk>/review/", product_view.product_review, name="productReview"),

    path("search/", product_view.search_view, name="search"),

    path('add_to_cart/', product_view.add_to_cart, name='add_to_cart'),
    path("<uuid:pk>/delete_from_checkout/", product_view.delete_from_checkout, name="delete_from_checkout"),

    path("checkout/", product_view.checkout, name="checkout"),
    path("process/order/", product_view.process_order, name="process_order"),

    path("<uuid:pk>/add_to_checkout/", product_view.add_to_checkout, name="add_to_checkout"),
    path("<uuid:pk>/remove_from_checkout/", product_view.remove_from_checkout, name="remove_from_checkout"),

]
