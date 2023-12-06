from django.urls import path
from .views import WishlistPage, add_to_wishlist, remove_wishlist

app_name = 'wishlist'

urlpatterns = [
    path('', WishlistPage, name='wishlist'),
    path('add-to-wishlist/', add_to_wishlist, name='add-to-wishlist'),
    path('remove-from-wishlist/', remove_wishlist, name='remove-from-wishlist'),
]
