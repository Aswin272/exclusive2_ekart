from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
from django.views.decorators.cache import never_cache
from products.models import Category,Product,ProductImage,CategoryOffer,ProductOffer
from . forms import UpdateCategoryForm,ProductForm,ProductImageForm,ProductUpdateForm,AddCategoryForm,AddCouponForm,CategoryOfferForm,ProductOfferForm,EditCouponForm,EditCategoryOfferForm,EditProductOffersForm
from customers.models import Customers
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.exceptions import MultipleObjectsReturned
from orders.models import Order,OrderItem
from django.http import JsonResponse
from django.db.models import F, ExpressionWrapper, DecimalField
from django.template.loader import render_to_string

from datetime import datetime, timedelta
from django.http import HttpResponse

from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum

from .models import Coupon




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
            return render(request,'admin_dashboard.html')   
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    return render(request,'adminn_signin.html')

@never_cache
def adminn_dashboard(request):
    if 'superuser' in request.session:
        return render(request,'admin_dashboard.html')
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
    if 'superuser' in request.session:
        products=Product.objects.all().order_by('id')
        return render(request,'admin_product_list.html',{'products':products})
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
                        return render(request, 'admin-product-update.html', {'form': form})
                    
                    form.save()
                    print("saved")
                    return redirect('product_list')
            else:
                form = ProductUpdateForm(instance=instance_to_be_edited)
            
            return render(request, 'admin-product-update.html', {'form': form})
        except ValidationError as e:
            error_message = "The Product could not be changed because the data didn't validate."
            form = ProductUpdateForm(instance=instance_to_be_edited)  # Re-instantiate form to display with error
            return render(request, 'admin-product-update.html', {'form': form, 'error_message': error_message})
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


def adminorders(request):
    print("triggered")
    if 'superuser' in request.session:
        
        if request.method == 'POST':
        
        # Get the order item ID and new status from the AJAX request
            orderitem_id = request.POST.get('orderitem_id')
            new_status = request.POST.get('status')

            try:
                # Retrieve the order item from the database
                orderitem = OrderItem.objects.get(id=orderitem_id)
                
                # Update the status of the order item
                orderitem.status = new_status
                orderitem.save()

                # Return a success response
                return JsonResponse({'success': True})

            except OrderItem.DoesNotExist:
                # Return an error response if the order item is not found
                return JsonResponse({'success': False, 'error': 'Order item does not exist'})

        # Return a bad request response if the request method is not POST
        # return JsonResponse({'success': False, 'error': 'Bad request'})
            
            
        
        
        all_orders = Order.objects.prefetch_related('orderitem_set').order_by('-created_at')
        
        for order in all_orders:
            for orderitem in order.orderitem_set.all():
                orderitem.total_price = orderitem.quantity * orderitem.product.price
        
        return render(request,'admin-allorders.html',{'orders':all_orders})
    return redirect('signin')
    
    
    
    
    
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




def coupon(request):
    if 'superuser' in request.session:
        coupons=Coupon.objects.all()
        
        return render(request,'admincoupon.html',{'coupons':coupons})
    return redirect('signin')
    
    
def addCoupon(request):
    if 'username' in request.session:
        if request.POST:
            addCoupon_form = AddCouponForm(request.POST)
            if addCoupon_form.is_valid():
                couponcode=addCoupon_form.cleaned_data['coupon_code']
                discount=addCoupon_form.cleaned_data['discount']
                
                if len(couponcode)<6:               
                    addCoupon_form.add_error('coupon_code','it should be length more than 6')
                
                if discount < 1.00:
                    addCoupon_form.add_error('discount','discount should be greater than 0')
                    
                if addCoupon_form.errors:
                    return render(request,'addcoupon.html',{'form':addCoupon_form})
                else:
                    
                    addCoupon_form.save()
                    return redirect('admin-coupon')
        form=AddCouponForm()
        return render(request,'addcoupon.html',{'form':form})
    
    return redirect('signin')

def editcoupon(request, pk):
    if 'superuser' in request.session:
        instance_to_be_edited = Coupon.objects.get(id=pk)
        
        if request.POST:
            addCoupon_form = EditCouponForm(request.POST)
            if addCoupon_form.is_valid():
                
                couponcode=addCoupon_form.cleaned_data['coupon_code']
                discount=addCoupon_form.cleaned_data['discount']
                
                if len(couponcode)<6:               
                    addCoupon_form.add_error('coupon_code','it should be length more than 6')
                
                if discount < 1.00:
                    addCoupon_form.add_error('discount','discount should be greater than 0')
                
                if addCoupon_form.errors:
                    return render(request,'admin-edit-coupon.html',{'form':addCoupon_form})
                    
                addCoupon_form.save()
                return redirect('admin-coupon')
        
        form = EditCouponForm(instance=instance_to_be_edited)
        return render(request, 'admin-edit-coupon.html', {'form': form})
    return redirect('signin')

# offer-------------------\
@never_cache
def categoryoffers(request):
    if 'superuser' in request.session:
        
        categoryoffers=CategoryOffer.objects.all()
        return render(request,'admin-categoryoffers.html',{'categoryoffers':categoryoffers})
    return redirect('signin')



  
def add_category_offer(request):
    if 'superuser' in request.session:
        if request.method=='POST':
            form=CategoryOfferForm(request.POST)
            if form.is_valid():
                
                discount_percentage=form.cleaned_data['discount_percentage']
                
                if discount_percentage < 1:
                    form.add_error('discount_percentage','discount percentage should not less than 0')
                    
                if form.errors:
                    return render(request,'add_category_offer.html',{'form':form})
                form.save()
                return redirect('category-offers')
        form=CategoryOfferForm()
        return render(request,'add_category_offer.html',{'form':form})
    return redirect('signin')


def editCategoryOffer(request,pk):
    if 'superuser' in request.session:
        instance_to_be_edited=CategoryOffer.objects.get(id=pk)
        if request.POST:
            form=EditCategoryOfferForm(request.POST,instance=instance_to_be_edited)
            
            if form.is_valid():
                discount_percentage=form.cleaned_data['discount_percentage']
                
                if discount_percentage < 1:
                    form.add_error('discount_percentage','should greater than 0')

                if form.errors:
                    return render(request,'admin-edit-Categoryofferform.html',{'form':form})
                form.save()
                return redirect('category-offers')
                
        form=EditCategoryOfferForm(instance=instance_to_be_edited)
        return render(request,'admin-edit-Categoryofferform.html',{'form':form})
    return redirect('signin')


# productoffer----------------


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
                
                if discount_price < 0:
                    form.add_error('discount_price','should greater than 0')
                    
                if form.errors:
                    return render(request,'admin-add-product-offer.html',{'form':form})
                form.save()
                return redirect('product-offers')
        form=ProductOfferForm()
        return render(request,'admin-add-product-offer.html',{'form':form})
    return redirect('signin')


def editProductOffers(request,pk):
    if 'superuser' in request.session:
        instance_to_be_edited=ProductOffer.objects.get(id=pk)
        if request.POST:
            form=EditProductOffersForm(request.POST,instance=instance_to_be_edited)
            if form.is_valid():
                discount_price=form.cleaned_data['discount_price']
                print("discount",discount_price)
                if discount_price < 1:
                    form.add_error('discount_price','price should be greater than 0')
                
                if form.errors:
                    return render(request,'admin-EditProductOffers.html',{'form':form})
                form.save()
                return redirect('product-offers')

        form=EditProductOffersForm(instance=instance_to_be_edited)
        return render(request,'admin-EditProductOffers.html',{'form':form})
    return redirect('signin')


def salesreport(request):
    if 'superuser' in request.session:
        if request.method == 'POST':
            interval = request.POST.get('interval')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Define initial queryset based on selected interval
            if interval == 'daily':
                orders = Order.objects.filter(created_at__date=datetime.now().date())
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
                status='Delivered'
            )

            total_sales = order_items.count()

            total_product_price = order_items.aggregate(
                total_product_price=Sum(F('product__price') * F('quantity'))
            )['total_product_price'] or 0

            total_coupon_discount = orders.filter(
                coupon__isnull=False,
                orderitem__status='Delivered'
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
            
                'overall_discount':overall_discount
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
            # Render form for selecting interval
            return render(request, 'admin-sales-report.html')
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




