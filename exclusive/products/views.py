from django.shortcuts import render,redirect
from .models import Category,Product,ProductImage,CategoryOffer,ProductOffer
from django.views.decorators.cache import never_cache
from customers.models import Customers,Productreview
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.utils import timezone


# Create your views here.

@never_cache
def index(request):
    
    category=Category.objects.filter(is_active=True)
    products=Product.objects.filter(Category__in=category,is_active=True)[:7]
    
    
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
    
    try:
        product=Product.objects.get(id=pk)
        # product=get_object_or_404(Product,id=pk)
    except Product.DoesNotExist:
        return render(request,'404.html')
    
    # product=Product.objects.get(id=pk)
    related_product=Product.objects.filter(Category=product.Category).exclude(id=pk)
    img=ProductImage.objects.filter(product=pk)
    reviews=Productreview.objects.filter(product=product)
    average_rating = Productreview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    
    category_offer = CategoryOffer.objects.filter(category=product.Category,
                                                   start_date__lte=timezone.now(),
                                                   end_date__gte=timezone.now()).first()
    
    
    product_offer = ProductOffer.objects.filter(product=product,
                                                 start_date__lte=timezone.now(),
                                                 end_date__gte=timezone.now()).first()
    
    
    discounted_price = None  # Initialize discounted price
    
    if category_offer:
        
        category_discounted_price = product.price - (product.price * category_offer.discount_percentage / 100)
        
    
    if product_offer:
        
        product_discounted_price = product.price - product_offer.discount_price
        
    
    if category_offer and product_offer:
        if category_discounted_price < product_discounted_price:
            discounted_price = category_discounted_price
        else:
            discounted_price = product_discounted_price
    elif category_offer:
        discounted_price = category_discounted_price
    elif product_offer:
        discounted_price = product_discounted_price
    print("dicsount price",discounted_price)
    
    for review in reviews:
        review.star_range =range(review.rating)
    return render(request,'product_detail_page.html',{'products':product,'img':img,'related_products':related_product,'average_rating':average_rating,'discounted_price': discounted_price,'reviews':reviews})

@never_cache
def all_products_list(request):
    active_categories = Category.objects.filter(is_active=True)
    products=Product.objects.filter(Category__in=active_categories,is_active=True)
    
    
    sort_by = request.POST.get('sort_by','')
    filter_by = request.POST.get('filter_by','')
    search_query = request.POST.get('search_query', '')

    # Apply filtering based on category
    if filter_by:
        products = products.filter(Category__name=filter_by)
    
    if search_query:
        products = products.filter(
            name__icontains=search_query
        )
    
    # Apply sorting
    if sort_by == 'priceHigh':
        products = products.order_by('price')
    elif sort_by == 'priceLow':
        products = products.order_by('-price')
    elif sort_by == 'nameAsce':
        products = products.order_by('name')
    elif sort_by == 'nameDesc':
        products = products.order_by('-name')
    elif sort_by == 'newArrivals':
        products = products.order_by('-release_date')

    
    
    
    return render(request,'all_product_list.html',{'products':products, 'categories': active_categories,'current_filter':filter_by,'current_sort':sort_by, 'search_query': search_query})


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
    
@never_cache
def search(request):
    print("yesss")
    query = request.GET.get('search_query', '')
    print(query)
    sort_by = request.GET.get('sort_by', '')
    
    if query:
        
        products = Product.objects.filter(name__icontains=query)
    else:
        products=Product.objects.all()
        
    if request.method=="POST":
        sort_by = request.POST.get('sort_by')
        print(sort_by)
    
        if sort_by == 'priceLow':
            products = products.order_by('price')
        elif sort_by == 'priceHigh':
            products = products.order_by('-price')
        elif sort_by == 'nameAsce':
            products = products.order_by('name')
        elif sort_by == 'nameDesc':
            products = products.order_by('-name')
        elif sort_by == 'newArrivals':
            products = products.order_by('-created_at')
    
    return render(request, 'search.html', {'products': products})