from django.urls import path
from .views import WishlistView, AddRemove_Wishlist, Empty_WishlistView

app_name = 'wishlist'

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist'),
    path('wishlist/add-remove/', AddRemove_Wishlist.as_view(), name='add_remove_wishlist'),
    path('wishlist/empty/', Empty_WishlistView.as_view(), name='empty_wishlist'),
]
