from django.shortcuts import redirect, render
from products.models import Product
from django.http import Http404, HttpResponseServerError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import HttpResponse


def get_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        context = {'product': product}
        if request.GET.get('size'):
            size = request.GET.get('size')
            price = product.get_product_price_by_size(size)
            context['selected_size'] = size
            context['updated_price'] = price

        return render(request, 'product/product.html', context=context)
    except Product.DoesNotExist:
        # Product not found, you may want to handle this case appropriately
        return HttpResponse("Product not found.")
    except Exception as e:
        # Handle other exceptions
        print(e)
        return HttpResponse("An error occurred.")


def product_list(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', 'default')  # Varsayılan sıralama

    if query:
        products = Product.objects.filter(product_name__icontains=query)
    else:
        products = Product.objects.all()

    if sort_by == 'price_low_to_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_to_low':
        products = products.order_by('-price')

    context = {
        'products': products,
        'query': query,
        'sort_by': sort_by,
    }

    return render(request, 'product/product_list.html', context)