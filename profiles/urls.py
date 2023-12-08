from django.urls import path
from .views import Profileview, address,addressUpdate

app_name = 'profiles'

urlpatterns = [
    path('', Profileview.as_view(), name='profile'),
    path('address/', address, name='address'),
    path('address_update/<int:pk>', addressUpdate.as_view(), name='address_update'),
 ]  