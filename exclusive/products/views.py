from django.shortcuts import render
from .models import Category,Product,ProductImage
from django.views.decorators.cache import never_cache
from customers.models import Customers,Productreview
from django.shortcuts import get_object_or_404
from django.db.models import Avg


# Create your views here.

@never_cache
def index(request):
    
    category=Category.objects.filter(is_active=True)
    products=Product.objects.filter(Category__in=category,is_active=True)
    
    
    if 'username' in request.session:
    
        name=request.session.get('username')
        try:
            username=Customers.objects.get(username=name)
            return render(request,'index.html',{'category':category,'products':products,'username':username})
        except:
            del request.session['username']
            return render(request,'index.html',{'category':category,'products':products})

    
    return render(request,'index.html',{'category':category,'products':products})


@never_cache
def product_detail_page(request,pk):
    print("product detail page")
    product=get_object_or_404(Product,id=pk)
    # product=Product.objects.get(id=pk)
    related_product=Product.objects.filter(Category=product.Category).exclude(id=pk)
    img=ProductImage.objects.filter(product=pk)
    average_rating = Productreview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    for i in img:
        print(i.image.url)
    return render(request,'product_detail_page.html',{'products':product,'img':img,'related_products':related_product,'average_rating':average_rating})

@never_cache
def all_products_list(request):
    active_categories = Category.objects.filter(is_active=True)
    products=Product.objects.filter(Category__in=active_categories,is_active=True)
    return render(request,'all_product_list.html',{'products':products})


def sort(request):
    if request.method=='POST':
        
        value=request.POST.get('sort_by')
        if value=='priceHigh':            
            products=Product.objects.all().order_by('price')
            return render(request,'all_product_list.html',{'products':products})
        elif value=='priceLow':
            products=Product.objects.all().order_by('-price')
            return render(request,'all_product_list.html',{'products':products})
        elif value=='nameAsce':
            products=Product.objects.all().order_by('name')
            return render(request,'all_product_list.html',{'products':products})        
        elif value=='nameDesc':
            products=Product.objects.all().order_by('-name')
            return render(request,'all_product_list.html',{'products':products})
        elif value=='newArrivals':
            products=Product.objects.all().order_by('date_joined')
            return render(request,'all_product_list.html',{'products':products})
    
        products=Product.objects.all()
        return render(request,'all_product_list.html',{'products':products})