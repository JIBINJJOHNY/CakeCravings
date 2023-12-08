from django.urls import path
from .views import Profileview, address,addressUpdate,account_settings,account_delete



urlpatterns = [
    path('', Profileview.as_view(), name='profile'),
    path('address/', address, name='address'),
    path('address_update/<int:pk>', addressUpdate.as_view(), name='address_update'),
    path('account/settings/', account_settings, name='account_settings'),
    path('account/delete/', account_delete, name='account_delete'),
 ]  