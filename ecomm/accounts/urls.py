from django.urls import path
from accounts.views import login_page, register_page, add_to_cart, basket, remove_cart

from accounts.views import LogoutProcess

urlpatterns = [
    path('login/', login_page, name="login"),
    path('register/', register_page, name="register"),
    path('basket/', basket, name="basket"),
    path('add-to-cart/<uid>/', add_to_cart, name="add_to_cart"),
    path('remove-cart/<cart_item_uid>/', remove_cart, name="remove_cart"),
    path('logout/', LogoutProcess.as_view(), name='logout'),

]
