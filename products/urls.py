from django.urls import path
from .views import product_list, all_products, product_detail, add_product, edit_product, delete_product

app_name = 'products'

urlpatterns = [
    path('', all_products, name='all_products'),
    path('category/<slug:category_slug>/', all_products, name='products_by_category'),
    path('<int:product_id>/', product_detail, name='product_detail'),
    path('product_list/', product_list, name='product_list'), 
    path('add_product/', add_product, name='add_product'),
    path('<int:product_id>/edit/', edit_product, name='edit_product'),  
    path('<int:product_id>/delete/', delete_product, name='delete_product'),  
]
