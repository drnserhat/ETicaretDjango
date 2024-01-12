# views.py

from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from products.models import ColorVariant, Product, SizeVariant
from .models import Cart, CartItems, Profile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from base.emails import send_account_activation_email
import uuid
from django.contrib.auth.views import LogoutView

class LogoutProcess(LogoutView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return redirect('index')

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=email)

        if not user_obj.exists():
            messages.warning(request, 'Bu şekilde bir hesap yok')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username=email, password=password)
        if user_obj:
            login(request, user_obj)
            messages.success(request, 'Giriş Başarılı')
            return redirect('/')
        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/login.html')

def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=email)

        if user_obj.exists():
            messages.warning(request, 'Bu şekilde bir email var zaten')
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, 'Kayıt Başarılı')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/register.html')

def activate_email(request, email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Profile.DoesNotExist:
        return HttpResponse('Geçersiz email')


from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from products.models import Product, ColorVariant, SizeVariant
from .models import Cart, CartItems

def add_to_cart(request, uid):
    variant = request.GET.get('variant')
    quantity1 = request.GET.get('quantity',1)
    product = Product.objects.get(uid=uid)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)

    # Eğer aynı ürün ve varyant zaten sepete eklenmişse, miktarını artır
    existing_cart_item = CartItems.objects.filter(cart=cart, product=product, size_variant__size_name=variant).first()
    if existing_cart_item:
        existing_cart_item.quantity += 1
        existing_cart_item.save()
    else:
        cart_item = CartItems.objects.create(cart=cart, product=product, quantity=quantity1)
        if variant:
            if product.size_variant.exists() and variant in product.size_variant.values_list('size_name', flat=True):
                size_variant = SizeVariant.objects.get(size_name=variant)
                cart_item.size_variant = size_variant
            elif product.color_variant.exists() and variant in product.color_variant.values_list('color_name', flat=True):
                color_variant = ColorVariant.objects.get(color_name=variant)
                cart_item.color_variant = color_variant
        cart_item.save()

    return HttpResponseRedirect('/accounts/basket/')



from .models import Coupon

def basket(request):
    user_basket = Cart.objects.filter(user=request.user)
    basket_detail = []
    total_price = 0  # Initialize total_price

    for cart in user_basket:
        basket_items = cart.cart_items.all()
        basket_total = sum(item.get_total_price() for item in basket_items)
        basket_detail.append({'cart': cart, 'cart_items': basket_items, 'cart_total': basket_total})
        total_price += basket_total  # Accumulate total_price

    # Retrieve discount coupon from the database
    coupon_code = request.POST.get('coupon')

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            discount_amount = coupon.discount_amount
            total_price -= discount_amount
            messages.success(request, 'Coupon applied successfully!')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')

    context = {'basket_detail': basket_detail, 'total_price': total_price}
    return render(request, 'accounts/basket.html', context)


def remove_cart(request, cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid=cart_item_uid)
        cart_item.delete()
        # Başarıyla kaldırıldıktan sonra sepet sayfasına yönlendir
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except CartItems.DoesNotExist:
        # Belirtilen öğe bulunamadığında işlem yap
        messages.error(request, 'Belirtilen öğe bulunamadı.')
        # Sepet sayfasına veya uygun bir sayfaya yönlendir
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except Exception as e:
        # Gerekirse diğer istisnaları işle
        print(e)
        messages.error(request, 'Bir hata oluştu.')
        # Sepet sayfasına veya uygun bir sayfaya yönlendir
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@receiver(post_save, sender=User)
def send_email_token(sender, instance, created, **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user=instance, email_token=email_token)
            email = instance.email
            send_account_activation_email(email, email_token)
    except Exception as e:
        print(e)
