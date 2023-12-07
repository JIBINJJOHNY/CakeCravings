from django.urls import path
from .views import view_wishlist,plus_wishlist, minus_wishlist

app_name = 'wishlist'

urlpatterns = [
    path('', view_wishlist, name='view_wishlist'),
    path('pluswishlist/', plus_wishlist, name='pluswishlist'),
    path('minuswishlist/', minus_wishlist, name='minuswishlist'),

]
