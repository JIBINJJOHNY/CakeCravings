from django.urls import path
from .views import ajax_add_review, product_reviews

app_name = 'reviews'

urlpatterns = [
    path('ajax_add_review/<int:pid>/', ajax_add_review, name='ajax_add_review'),
    path('product_reviews/<int:product_id>/', product_reviews, name='product_reviews'),
]
