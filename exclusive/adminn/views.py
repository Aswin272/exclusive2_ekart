from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from django.views.decorators.cache import never_cache
from products.models import Category,Product,ProductImage,CategoryOffer,ProductOffer,Brand
from . forms import UpdateCategoryForm,ProductForm,ProductImageForm,ProductUpdateForm,AddCategoryForm,AddCouponForm,CategoryOfferForm,ProductOfferForm,EditCouponForm,EditCategoryOfferForm,EditProductOffersForm
from customers.models import Customers,Wallet
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.exceptions import MultipleObjectsReturned
from orders.models import Order,OrderItem
from django.http import JsonResponse
from django.db.models import F, ExpressionWrapper, DecimalField
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse

from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum,Q

from .models import Coupon
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractWeek, ExtractYear
import calendar
from django.urls import reverse
from django.utils.timezone import now




# Create your views here.


@never_cache
def adminn(request):
    
    if 'superuser' in request.session:       
        return redirect('adminn_dashboard') 
    if request.method=='POST':       
        username=request.POST.get('username')
        password=request.POST.get('password')
            
        try:
            user = authenticate(username=username, password=password)
        except MultipleObjectsReturned:
            
            messages.error(request, "Invalid username or password. Please try again....")
            return render(request, 'adminn_signin.html')  
          
        if user is not None and user.is_superuser:   
                   
            request.session['superuser']=username
            login(request,user)
            return redirect('adminn_dashboard')
            # return render(request,'admin_dashboard.html')   
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    return render(request,'adminn_signin.html')

@never_cache
def adminn_dashboard(request):
    if 'superuser' in request.session:
        
        top_products=(OrderItem.objects.filter(order__status='Delivered')
                      .values('product')
                      .annotate(total_quantity=Sum('quantity'))
                      .order_by('-total_quantity')[:10])
        top_category=(OrderItem.objects.filter(order__status='Delivered')
                        .values('product__Category') 
                        .annotate(total_quantity=Sum('quantity'))
                        .order_by('-total_quantity'))
        # top_brands =(OrderItem.objects.filter(order__status='Delivered')
        #              .values('product__brand')
        #              .annotate(total_quantity=Sum('quantity'))
        #              .order_by('-total_quantity')[:10]
        #              )
        
        product_with_quantities=[]
        for item in top_products:
            product=Product.objects.get(id=item['product'])
            product_with_quantities.append({'product':product,'total_quantity':item['total_quantity']})
            
        categories_with_quantities = []
        for item in top_category:
            category = Category.objects.get(id=item['product__Category'])
            categories_with_quantities.append({
                'category': category,
                'total_quantity': item['total_quantity']
            })
        
        # brand_with_quantity=[]
        # for item in top_brands:
        #     brand=Brand.objects.get(id=item['product__brand'])
        #     brand_with_quantity.append({
        #         'brand':brand,
        #         'total_quantity':item['total_quantity']
        #     })
        
        # return render(request,'admin_dashboard.html',{'top_selling_product':product_with_quantities,'top_selling_category':categories_with_quantities,'top_selling_brand':brand_with_quantity})
        
        
        current_year = timezone.now().year
        timeframe = request.GET.get('timeframe', 'monthly')

        if timeframe == 'weekly':
            sales_data = Order.objects.filter(
                created_at__year=current_year,
                status='Delivered',
                is_cancelled=False
            ).annotate(week=ExtractWeek('created_at')).values('week').annotate(
                count=Count('id'),
                total_price=Sum('total_price')
            ).order_by('week')

            labels = [f"Week {m['week']}" for m in sales_data]

        elif timeframe == 'yearly':
            sales_data = Order.objects.filter(
                status='Delivered',
                is_cancelled=False
            ).annotate(year=ExtractYear('created_at')).values('year').annotate(
                count=Count('id'),
                total_price=Sum('total_price')
            ).order_by('year')

            labels = [str(m['year']) for m in sales_data]

        else:  # Default to monthly
            sales_data = Order.objects.filter(
                created_at__year=current_year,
                status='Delivered',
                is_cancelled=False
            ).annotate(month=ExtractMonth('created_at')).values('month').annotate(
                count=Count('id'),
                total_price=Sum('total_price')
            ).order_by('month')

            labels = [calendar.month_abbr[m['month']] for m in sales_data]

        sales_count = [m['count'] for m in sales_data]
        total_prices = [float(m['total_price']) for m in sales_data]

        #total user------
        total_users = Customers.objects.count()
        
        overall_total_sale_amount = sum(Order.objects.filter(status='Delivered', is_cancelled=False).values_list('total_price', flat=True))
        
        overall_total_sales = Order.objects.filter(status='Delivered', is_cancelled=False).count()

        context = {
            'labels': labels,
            'sales_count': sales_count,
            'total_prices': total_prices,
            'selected_timeframe': timeframe,
            'products_with_quantities':product_with_quantities,
            'categories_with_quantities':categories_with_quantities,
            'total_users': total_users,
            'overall_total_sale_amount':overall_total_sale_amount,
            'overall_total_sales':overall_total_sales
        }
        
        return render(request,'admin_dashboard.html',context)
    return redirect('adminn')





# admin-Category-------------------

@never_cache
def category(request):
    if 'superuser' in request.session:
        
        category_instance=Category.objects.all()
        return render(request,'admin_category.html',{'categories':category_instance})
    
@never_cache
# def add_category(request):
    # if 'superuser' in request.session:
    #     if request.method=='POST':
    #         categ=request.POST.get('name')
    #         description=request.POST.get('description')
    #         image = request.FILES.get('image')
            
            
    #         Category.objects.create(name=categ,description=description,image=image)
    #         return redirect('category')
    #     return render(request,'add_category.html')
    # return redirect('adminn')
@never_cache
def add_category(request):
    if 'superuser' in request.session:
        if request.method=='POST':
            form=AddCategoryForm(request.POST,request.FILES)
            if form.is_valid():
                name = form.cleaned_data['name']
                
                if Category.objects.filter(name=name).exists():
                    form.add_error('name', 'A category with the same name already exists.')
                else:
                    
                    form.save()
                    return redirect('category')
        else:
            form=AddCategoryForm()
        return render(request,'add_category.html',{'form':form})
    return redirect('adminn')


@never_cache
def UpdateCategory(request,pk):
    if 'superuser' in request.session:
        instance=Category.objects.get(id=pk)
      
        
        if request.POST:
            fm=UpdateCategoryForm(request.POST,request.FILES,instance=instance)
            
            if fm.is_valid():
                name = fm.cleaned_data['name']
                if Category.objects.filter(name=name).exists():
                    fm.add_error('name', 'A category with the same name already exists.')
                else:
                    
                    fm.save()
                    return redirect('category')
        else:
            fm=UpdateCategoryForm(instance=instance)
                
        return render(request,'admin_update_category.html',{'instance':instance,'f':fm})
    return redirect('adminn')

@never_cache
def active_unactive_category(request,pk):
    if 'superuser' in request.session:
        category=Category.objects.get(id=pk)
        if category.is_active:
            category.is_active = False
        else:
            category.is_active = True
        category.save()
        return redirect('category')
    return redirect('adminn')

# products---------------------

@never_cache
def product_list(request):
    print("product list")
    if 'superuser' in request.session:
        print("inside product list")
        products=Product.objects.all().order_by('id')
        print("all correct")
        return render(request,'admin_product_list.html',{'products':products})
    print("messed up")
    return redirect('adminn')


@never_cache
def add_products(request):
    if 'superuser' in request.session:
        if request.method == 'POST':
            product_form = ProductForm(request.POST, request.FILES)
            if product_form.is_valid():
                # Custom price validation
                price = product_form.cleaned_data['price']
                if price < 0:
                    product_form.add_error('price', 'Price must be greater than or equal to zero.')
                # Custom quantity validation
                quantity = product_form.cleaned_data['quantity']
                if quantity < 0:
                    product_form.add_error('quantity', 'Quantity must be greater than or equal to zero.')
                # If both price and quantity are valid, proceed with saving the form
                
                name=product_form.cleaned_data['name']
                if Product.objects.filter(name=name).exists():
                    product_form.add_error('name', 'A product with the same name already exists.')
                if price >= 0 and quantity >= 0 and not Product.objects.filter(name=name).exists():
                    product = product_form.save()
                    product_id = product.id
                    
                    images = request.FILES.getlist('image')
                    for img in images:
                        ProductImage.objects.create(product_id=product_id, image=img)
                    return redirect('product_list')
            else:
                print('Form is not valid:', product_form.errors)
        else:
            product_form = ProductForm()
            
        
        return render(request, 'admin_add_product.html', {'frm': product_form})
    return redirect('adminn')



@never_cache
def product_update(request, pk):
    if 'superuser' in request.session:
        try:
            instance_to_be_edited = Product.objects.get(id=pk)
            product_image=ProductImage.objects.filter(product=pk)
            if request.method == 'POST':
                form = ProductUpdateForm(request.POST, request.FILES, instance=instance_to_be_edited)
                if form.is_valid():
                    price = form.cleaned_data.get('price')
                    quantity = form.cleaned_data.get('quantity')
                    
                    
                    if price is not None and price < 0:
                        form.add_error('price', "Price cannot be less than 0.")
                    if quantity is not None and quantity < 0:
                        form.add_error('quantity', "Quantity cannot be less than 0.")
                    
                    if form.errors:
                        return render(request, 'admin-product-update.html', {'form': form,'product_image':product_image})
                    
                    form.save()
                    print("saved")
                    return redirect('product_list')
            else:
                form = ProductUpdateForm(instance=instance_to_be_edited)
            
            return render(request, 'admin-product-update.html', {'form': form,'product_image':product_image, 'instance': instance_to_be_edited})
        except ValidationError as e:
            error_message = "The Product could not be changed because the data didn't validate."
            form = ProductUpdateForm(instance=instance_to_be_edited)  # Re-instantiate form to display with error
            
            return render(request, 'admin-product-update.html', {'form': form, 'error_message': error_message, 'instance': instance_to_be_edited})
    return redirect('adminn')

@never_cache
def active_unactive_product(request,pk): 
    if 'superuser' in request.session:
        product=Product.objects.get(id=pk)
        if product.is_active:
            print("done")
            product.is_active=False
        else:
            product.is_active=True
        product.save()
        return redirect('product_list')
    return redirect('adminn')


@never_cache
def admin_customer_list(request):
    if 'superuser' in request.session:
        customers=Customers.objects.all().order_by('id')
        return render(request,'admin_customers.html',{'customers':customers})
    return redirect('adminn')

@never_cache
def listandunlistcustomer(request,pk):
    if 'superuser' in request.session:
        user = Customers.objects.get(id=pk)
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return redirect('admin-customers')
    return redirect('adminn')







@never_cache
def logout(request):
    if 'username' in request.session:
        print("yesssss.......")
        request.session.flush() 
        return redirect('signin')
    if 'superuser' in request.session:
        request.session.flush()       
        return redirect('adminn')
    
    
@never_cache   
def uploadImage(request,pk):
    if 'superuser' in request.session:
        product=Product.objects.get(id=pk)
        product_id=product.id
        print(product_id)
        print(product)
        if request.method=='POST':
            images = request.FILES.getlist('image')
            print(images)
            for img in images:
                ProductImage.objects.create(product_id=product_id, image=img)
            return redirect('product_list')
    
        return render(request,'uploadImage.html')
    return redirect('adminn')

@never_cache
def deleteproductImage(request,pk):
    print("inside product aimage")
    if 'superuser' in request.session:
        image_to_delete=ProductImage.objects.get(id=pk)
        product_id =image_to_delete.product.id
        image_to_delete.delete()
        
        return redirect(reverse('product-update',args=[product_id]))
    return redirect('adminn')


@never_cache
def adminorders(request):
    print("yesss")
    if 'superuser' in request.session:
        if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('new_status')
            print(order_id)
            print(new_status)
            
            

            try:
                order = Order.objects.get(pk=order_id)
                print(order.user)
                if order.is_return:
                    if new_status=='Returned':
                        wallet=Wallet.objects.get(user=order.user)
                        
                        wallet.balance +=order.total_price
                        wallet.save()
                        
                    order.return_status=new_status
                    if order.coupon:
                        order.coupon=None
                    order.save()
                    
                if new_status == 'Delivered':
                    order.payment_status='Paid'
                    order.save()
                    
                if new_status =="Cancelled":
                    print("order cancelled")
                    order_items=OrderItem.objects.filter(order=order)
                    for item in order_items: 
                        item.product.quantity += item.quantity
                        item.product.save()
                if not order.is_return:
                    
                    order.status = new_status
                    order.save()
                return JsonResponse({'success': True})
            except Order.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Order does not exist'})
        
        orders = Order.objects.all().order_by('-id')
        return render(request, 'admin-allorders.html', {'orders': orders})
    return redirect('signin')


@never_cache
def adminOrderDetail(request,pk):
    if 'superuser' in request.session:
        
        order=Order.objects.get(id=pk)
        order_items = OrderItem.objects.filter(order=order)
        total_order_price = sum(item.price for item in order_items)

        return render(request,'admin-orderdetailpage.html', {'order': order, 'order_items': order_items, 'total_order_price': total_order_price})
    return redirect('signin')




# def adminorders(request):
#     print("triggered")
#     if 'superuser' in request.session:
        
#         if request.method == 'POST':
        
#         # Get the order item ID and new status from the AJAX request
#             orderitem_id = request.POST.get('orderitem_id')
#             new_status = request.POST.get('status')

#             try:
#                 # Retrieve the order item from the database
#                 orderitem = OrderItem.objects.get(id=orderitem_id)
                
#                 # Update the status of the order item
#                 orderitem.status = new_status
#                 if new_status == 'Cancelled':
                    
#                     orderitem.product.quantity += orderitem.quantity
#                     print("quantity",orderitem.product.quantity)
#                     orderitem.product.save()
#                 orderitem.save()

#                 # Return a success response
#                 return JsonResponse({'success': True})

#             except OrderItem.DoesNotExist:
#                 # Return an error response if the order item is not found
#                 return JsonResponse({'success': False, 'error': 'Order item does not exist'})

#         # Return a bad request response if the request method is not POST
#         # return JsonResponse({'success': False, 'error': 'Bad request'})
            
            
        
        
#         all_orders = Order.objects.prefetch_related('orderitem_set').order_by('-created_at')
        
#         for order in all_orders:
#             for orderitem in order.orderitem_set.all():
#                 orderitem.total_price = orderitem.quantity * orderitem.product.price
        
#         return render(request,'admin-allorders.html',{'orders':all_orders})
#     return redirect('signin')
    
    
    
    
    
# def update_status(request):
#     print("acieved")
#     if request.method == 'POST':
        
#         # Get the order item ID and new status from the AJAX request
#         orderitem_id = request.POST.get('orderitem_id')
#         new_status = request.POST.get('status')

#         try:
#             # Retrieve the order item from the database
#             orderitem = OrderItem.objects.get(id=orderitem_id)
            
#             # Update the status of the order item
#             orderitem.status = new_status
#             orderitem.save()

#             # Return a success response
#             return JsonResponse({'success': True})

#         except OrderItem.DoesNotExist:
#             # Return an error response if the order item is not found
#             return JsonResponse({'success': False, 'error': 'Order item does not exist'})

#     # Return a bad request response if the request method is not POST
#     return JsonResponse({'success': False, 'error': 'Bad request'})


#coupon--------------
@never_cache
def coupon(request):
    if 'superuser' in request.session:
        coupons=Coupon.objects.all()
        
        return render(request,'admincoupon.html',{'coupons':coupons})
    return redirect('signin')
    
@never_cache  
def addCoupon(request):
    if 'superuser' in request.session:
        if request.POST:
            addCoupon_form = AddCouponForm(request.POST)
            if addCoupon_form.is_valid():
                couponcode=addCoupon_form.cleaned_data['coupon_code']
                discount=addCoupon_form.cleaned_data['discount']
                min_purchase_amount=addCoupon_form.cleaned_data['min_purchase_amount']
                print(min_purchase_amount)
                
                if len(couponcode)<6:               
                    addCoupon_form.add_error('coupon_code','it should be length more than 6')
                
                if discount < 1.00:
                    addCoupon_form.add_error('discount','discount should be greater than 0')
                
                if min_purchase_amount < 10.00:
                    addCoupon_form.add_error('min_purchase_amount','amount should be greater than 10')
                
                if discount >= min_purchase_amount:
                    addCoupon_form.add_error('discount','discount amount should be lesser than min purchase amount')
                    
                if Coupon.objects.filter(coupon_code=couponcode).exists():
                    print("coupon exists")
                    addCoupon_form.add_error('coupon_code','this coupon code already exists')
                    
                if addCoupon_form.errors:
                    return render(request,'addcoupon.html',{'form':addCoupon_form})
                
                else:
                    
                    addCoupon_form.save()
                    return redirect('admin-coupon')
            else:
                
                return render(request, 'addcoupon.html', {'form': addCoupon_form})
            
        form=AddCouponForm()
        return render(request,'addcoupon.html',{'form':form})
    
    return redirect('signin')

@never_cache
def editcoupon(request, pk):
    if 'superuser' in request.session:
        instance_to_be_edited = Coupon.objects.get(id=pk)
        
        if request.POST:
            editCoupon_form = EditCouponForm(request.POST,instance=instance_to_be_edited)
            if editCoupon_form.is_valid():
                
                couponcode=editCoupon_form.cleaned_data['coupon_code']
                discount=editCoupon_form.cleaned_data['discount']
                min_purchase_amount=editCoupon_form.cleaned_data['min_purchase_amount']

                if len(couponcode)<6:               
                    editCoupon_form.add_error('coupon_code','it should be length more than 6')
                
                if discount < 1.00:
                    editCoupon_form.add_error('discount','discount should be greater than 0')
                    
                if min_purchase_amount < 10.00:
                    editCoupon_form.add_error('min_purchase_amount','amount should be greater than 10')
                    
                if discount >= min_purchase_amount:
                    editCoupon_form.add_error('discount','discount amount should be lesser than min purchase amount')
                    
                if Coupon.objects.filter(coupon_code=couponcode).exists():
                    print("coupon exists")
                    editCoupon_form.add_error('coupon_code','this coupon code already exists')
                
                if editCoupon_form.errors:
                    return render(request,'admin-edit-coupon.html',{'form':editCoupon_form})
                    
                editCoupon_form.save()
                return redirect('admin-coupon')
        
        form = EditCouponForm(instance=instance_to_be_edited)
        return render(request, 'admin-edit-coupon.html', {'form': form})
    return redirect('signin')

@never_cache
def deletecoupon(request,pk):
    if 'superuser' in request.session:
        coupon=Coupon.objects.get(id=pk)
        coupon.delete()
        return redirect('admin-coupon')
    return redirect('signin')


# offer-------------------
@never_cache
def categoryoffers(request):
    if 'superuser' in request.session:
        
        categoryoffers=CategoryOffer.objects.all()
        return render(request,'admin-categoryoffers.html',{'categoryoffers':categoryoffers})
    return redirect('signin')



@never_cache  
def add_category_offer(request):
    if 'superuser' in request.session:
        if request.method=='POST':
            form=CategoryOfferForm(request.POST)
            if form.is_valid():
                
                discount_percentage=form.cleaned_data['discount_percentage']
                start_date=form.cleaned_data['start_date']
                end_date=form.cleaned_data['end_date']
                category=form.cleaned_data['category']
                
                
                
                if discount_percentage < 1 :
                    form.add_error('discount_percentage','discount percentage should not less than 0')
                
                if discount_percentage > 90 :
                    form.add_error('discount_percentage','discount percentage should not greater than 90%')
                    
                if start_date > end_date:
                    form.add_error('end_date','end date should be greater than start date')
                
                if CategoryOffer.objects.filter(category=category).exists():
                    form.add_error('category','offer for this category already exist')
                    
                if form.errors:
                    return render(request,'add_category_offer.html',{'form':form})
                form.save()
                return redirect('category-offers')
        
        else:
                
            form=CategoryOfferForm()
        return render(request,'add_category_offer.html',{'form':form})
    return redirect('signin')

@never_cache
def editCategoryOffer(request,pk):
    if 'superuser' in request.session:
        instance_to_be_edited=CategoryOffer.objects.get(id=pk)
        if request.POST:
            form=EditCategoryOfferForm(request.POST,instance=instance_to_be_edited)
            
            if form.is_valid():
                discount_percentage=form.cleaned_data['discount_percentage']
                start_date=form.cleaned_data['start_date']
                end_date=form.cleaned_data['end_date']
                category=form.cleaned_data['category']
                
                if discount_percentage < 1:
                    form.add_error('discount_percentage','should greater than 0')
                    
                if discount_percentage > 90 :
                    form.add_error('discount_percentage','discount percentage should not greater than 90%')
                    
                if start_date > end_date:
                    form.add_error('end_date','end date should be greater than start date')
                    
                if CategoryOffer.objects.filter(category=category).exists():
                    form.add_error('category','offer for this category already exist')

                if form.errors:
                    return render(request,'admin-edit-Categoryofferform.html',{'form':form})
                
                
                form.save()
                return redirect('category-offers')
        else:
                    
            form=EditCategoryOfferForm(instance=instance_to_be_edited)
        return render(request,'admin-edit-Categoryofferform.html',{'form':form})
    return redirect('signin')

@never_cache
def deleteCategoryOffer(request,pk):
    if 'superuser' in request.session:
        category_offer=CategoryOffer.objects.get(id=pk)
        category_offer.delete()
        return redirect('category-offers')
    return redirect('signin')


# productoffer---------------
@never_cache
def productoffers(request):
    if 'superuser' in request.session:
        productoffers=ProductOffer.objects.all()
        
        return render(request,'admin-productoffers.html',{'productoffers':productoffers})
    return redirect('signin')

@never_cache
def add_product_offer(request):
    if 'superuser' in request.session:
        if request.method=='POST':
            form=ProductOfferForm(request.POST)
            if form.is_valid():
                discount_price=form.cleaned_data['discount_price']
                product=form.cleaned_data['product']
                start_date=form.cleaned_data['start_date']
                end_date=form.cleaned_data['end_date']
                
                
                if discount_price < 0:
                    form.add_error('discount_price','should greater than 0')
                
                if discount_price >= product.price:
                    form.add_error('discount_price','should not be greater than or equal to product price')
                
                if start_date > end_date:
                    form.add_error('end_date','end date should be greater than start date')
                    
                if form.errors:
                    return render(request,'admin-add-product-offer.html',{'form':form})
                form.save()
                return redirect('product-offers')
        form=ProductOfferForm()
        return render(request,'admin-add-product-offer.html',{'form':form})
    return redirect('signin')

@never_cache
def editProductOffers(request,pk):
    if 'superuser' in request.session:
        instance_to_be_edited=ProductOffer.objects.get(id=pk)
        if request.POST:
            form=EditProductOffersForm(request.POST,instance=instance_to_be_edited)
            if form.is_valid():
                discount_price=form.cleaned_data['discount_price']
                start_date=form.cleaned_data['start_date']
                end_date=form.cleaned_data['end_date']
                
                print("discount",discount_price)
                if discount_price < 1:
                    form.add_error('discount_price','price should be greater than 0')
                    
                if start_date > end_date:
                    form.add_error('end_date','end date should be greater than start date')
                
                if form.errors:
                    return render(request,'admin-EditProductOffers.html',{'form':form})
                form.save()
                return redirect('product-offers')

        form=EditProductOffersForm(instance=instance_to_be_edited)
        return render(request,'admin-EditProductOffers.html',{'form':form})
    return redirect('signin')

@never_cache
def deleteProductOffer(request,pk):
    if 'superuser' in request.session:
        product_offer=ProductOffer.objects.get(id=pk)
        product_offer.delete()
        return redirect('product-offers')
    return redirect('signin')


#sales report--------------
@never_cache
def salesreport(request):
    period = request.GET.get('period','weekly')  # Get the selected period from the request parameters

    # Default start and end dates for custom date range
    start_date = end_date = now()

    # Determine start and end dates based on the period
    if period == 'daily':
        start_date = now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'weekly':
        start_date = now() - timedelta(days=now().weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=6)
    elif period == 'monthly':
        start_date = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=31)  # Assuming each month has 31 days
    elif period == 'custom':
        # Get start_date and end_date from request parameters
        start_date_param = request.GET.get('start_date')
        end_date_param = request.GET.get('end_date')

        # Convert start_date and end_date from string to datetime
        start_date = datetime.strptime(start_date_param, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)


    print(f"Period: {period}")
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")
    
    # Filter orders within the specified date range
    delivered_orders = Order.objects.filter(created_at__range=[start_date, end_date], status='Delivered').filter(Q(is_return=False) | Q(return_status='Rejected'))

    # Calculate total sales within the time frame for delivered orders only
    total_sales_delivered = delivered_orders.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0

    # Count of delivered orders
    delivered_orders_count = delivered_orders.count()

    # Calculate total coupon discount for delivered orders that have a coupon applied
    total_coupon_discount = delivered_orders.filter(coupon__isnull=False).aggregate(total_discount=Sum('coupon__discount'))['total_discount'] or 0
    
    total_products_price = sum(
        sum(order_item.product.price * order_item.quantity for order_item in order.orderitem_set.all())
        for order in delivered_orders
    )
    
    total_products_price_without_quantity = sum(
        sum(order_item.price for order_item in order.orderitem_set.all())
        for order in delivered_orders
    )
    
    overall_product_discount = total_products_price - total_products_price_without_quantity
    
    full_discount=overall_product_discount + total_coupon_discount
    
    
    
    
    print(overall_product_discount)

    context = {
        'total_sales_delivered': total_sales_delivered,
        'delivered_orders_count': delivered_orders_count,
        'total_coupon_discount': total_coupon_discount,
        'total_products_price': total_products_price,
        'total_products_price_without_quantity': total_products_price_without_quantity,
        'overall_product_discount': overall_product_discount,
        'full_discount':full_discount,
        'delivered_orders':delivered_orders,
    }
    
    if request.POST:
        
        template = get_template('sales_report_pdf.html')
        html = template.render(context)

        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    
    
    return render(request, 'sales_report.html', context)



def salesreportt(request):
    if 'superuser' in request.session:
        if request.method == 'POST':
            interval = request.POST.get('interval')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Define initial queryset based on selected interval
            if interval == 'daily':
                print("its daily")
                start_of_day = datetime.now().date()
                end_of_day = start_of_day + timedelta(days=1)
                orders = Order.objects.filter(created_at__date__range=[start_of_day, end_of_day])
            elif interval == 'weekly':
                start_of_week = datetime.now().date() - timedelta(days=datetime.now().weekday())
                orders = Order.objects.filter(created_at__date__gte=start_of_week)
            elif interval == 'yearly':
                start_of_year = datetime.now().date().replace(month=1, day=1)
                orders = Order.objects.filter(created_at__date__gte=start_of_year)
            elif interval == 'custom':
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                orders = Order.objects.filter(created_at__date__range=[start_date, end_date])

            # Aggregate sales data for delivered orders
            order_items = OrderItem.objects.filter(
                order__in=orders,
                order__status='Delivered',   
            )
            
            # total_sales = order_items.count()
            
            delivered_orders = orders.filter(status='Delivered')
            delivered_order_items=OrderItem.objects.filter(order__in=delivered_orders)
            
            total_sales=delivered_orders.count()

            total_product_price = order_items.aggregate(
                total_product_price=Sum('price')
            )['total_product_price'] or 0

            total_coupon_discount = orders.filter(
                coupon__isnull=False,
                status='Delivered'
            ).distinct().aggregate(
                total_coupon_discount=Sum('coupon__discount')
            )['total_coupon_discount'] or 0

            # total_discount = order_items.aggregate(
            #     total_discount=Sum((F('price') - F('product__price') * F('quantity')))
            # )['total_discount'] or 0

            total_order_amount = order_items.aggregate(
                total_order_amount=Sum('price')
            )['total_order_amount'] or 0



            product_price_after_averall_discount=total_order_amount - total_coupon_discount
            
            overall_discount=total_product_price-product_price_after_averall_discount
            
            # Pass data to template
            context = {
                'interval': interval,
                'total_sales': total_sales,
                'total_product_price': total_product_price,
                'total_order_amount': total_order_amount,
                'product_price_after_averall_discount': product_price_after_averall_discount,
                'total_coupon_discount': total_coupon_discount,
                'overall_discount':overall_discount,
                'orders': delivered_orders,
                'order_items':delivered_order_items
            }

            # Render HTML template
            template = get_template('admin-sales-report.html')
            html = template.render(context)

            # Generate PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('We had some errors <pre>' + html + '</pre>')
            return response
        else:
            
            sales_data = (
                OrderItem.objects
                .filter(order__status='Delivered')
                .values('product__name')
                .annotate(total_quantity=Sum('quantity'))
                .order_by('-total_quantity')
            )

            # Prepare data for the chart
            products = [item['product__name'] for item in sales_data]
            quantities = [item['total_quantity'] for item in sales_data]

            context = {
                'products': products,
                'quantities': quantities,
                'sales_data':sales_data
            }
                    
            
            # Render form for selecting interval
            return render(request, 'admin-sales-report.html',context)
    return redirect('signin')





# def generate_sales_report(request, interval):
#     # Determine the start and end dates based on the selected interval
#     end_date = datetime.now()
#     if interval == 'daily':
#         start_date = end_date - timedelta(days=1)
#     elif interval == 'weekly':
#         start_date = end_date - timedelta(weeks=1)
#     elif interval == 'yearly':
#         start_date = end_date - timedelta(days=365)
#     elif interval == 'custom':
#         start_date = request.GET.get('start_date')
#         end_date = request.GET.get('end_date')
#         # Convert start_date and end_date to datetime objects if needed

#     # Generate the sales report data
#     sales_report_data = generate_sales_report(start_date, end_date)
    
#     # Render the sales report template with the data
#     html_string = render_to_string('sales_report.html', {'sales_report_data': sales_report_data})
    
#     # Create PDF using WeasyPrint
#     pdf_file = HTML(string=html_string).write_pdf()
    
#     # Create HTTP response with PDF file
#     response = HttpResponse(pdf_file, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    
#     return response


def brand(request):
    brands=Brand.objects.all()
    return render(request,'admin-brands.html',{'brands':brands})


def dashboard(request):
    print("coming")
    return render(request,'dashboard.html')