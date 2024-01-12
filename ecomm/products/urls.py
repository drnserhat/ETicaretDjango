from django.urls import path
from products.views import get_product, product_list


urlpatterns = [
    path('product_list/', product_list, name='product_list'),
    path('<slug>/', get_product, name="get_product"),

]