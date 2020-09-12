from django.urls import path
from .views import *


app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('size/<size>', HomeView.as_view(), name='size'),
    path('about', about, name='about'),
    path('clicky', clicky, name='clicky'),
    path('get-richer', get_richer, name='get-richer'),
    path('iamrichnow', iamrichnow, name='iamrichnow'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('products/<slug>', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('order-summary', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout', checkout, name='checkout'),
    path('buy', buy, name='buy'),
]
