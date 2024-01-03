from django.urls import path
from django.contrib.auth import views as auth_views
from .views import ProfileView, address, addressUpdate, account_settings, account_delete

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('address/', address, name='address'),
    path('address_update/<int:pk>', addressUpdate.as_view(), name='address_update'),
    path('account/settings/', account_settings, name='account_settings'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('account/delete/', account_delete, name='account_delete'),
 ]  