from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
from django.views.decorators.cache import never_cache
from products.models import Category,Product,ProductImage
from . forms import UpdateCategoryForm,ProductForm,ProductImageForm,ProductUpdateForm,AddCategoryForm
from customers.models import Customers
from django.contrib import messages
from django.core.exceptions import ValidationError

# Create your views here.


@never_cache
def adminn(request):
    if 'superuser' in request.session:       
        return redirect('adminn_dashboard') 
    if request.method=='POST':       
        username=request.POST.get('username')
        password=request.POST.get('password')      
        user=authenticate(username=username,password=password)       
        if user is not None:          
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
        products=Product.objects.all()
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
                if price >= 0 and quantity >= 0:
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
                    
                    # Check if price and quantity are valid
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
        customers=Customers.objects.all()
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