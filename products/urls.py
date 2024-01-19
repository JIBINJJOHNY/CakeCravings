from django.urls import path
from .views import (
    product_list,
    all_products,
    product_detail,
    add_product,
    edit_product,
    delete_product,
    add_tag,
    remove_tag,
    add_discount,
    remove_discount,
)

urlpatterns = [
    path('', all_products, name='all_products'),
    path('category/<slug:category_slug>/', all_products, name='products_by_category'),
    path('<int:product_id>/', product_detail, name='product_detail'),
    path('product_list/', product_list, name='product_list'),
    path('add_product/', add_product, name='add_product'),
    path('<int:product_id>/edit/', edit_product, name='edit_product'),
    path('<int:product_id>/delete/', delete_product, name='delete_product'),
    path('add-tag/', add_tag, name='add-tag'),
    path('remove-tag/<int:tag_id>/', remove_tag, name='remove-tag'),
    path('add-discount/', add_discount, name='add-discount'),
    path('remove-discount/<int:discount_id>/', remove_discount, name='remove-discount'),
]
