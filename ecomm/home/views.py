from django.shortcuts import render
from products.models import Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
    query = request.GET.get('q', '')
    products_list = Product.objects.all()

    if query:
        products_list = products_list.filter(product_name__icontains=query)

    paginator = Paginator(products_list, 10)  # Sayfada 10 ürün gösterilecek

    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # Eğer sayfa sayısı bir tamsayı değilse, ilk sayfayı al
        products = paginator.page(1)
    except EmptyPage:
        # Eğer sayfa sayısı çok büyükse, son sayfayı al
        products = paginator.page(paginator.num_pages)

    context = {'products': products, 'query': query}
    return render(request, 'home/index.html', context)
