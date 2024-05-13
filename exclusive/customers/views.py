from django.shortcuts import render,redirect,get_object_or_404,HttpResponse,HttpResponseRedirect
from . models import Customers,Address,Cart,CartItem,Productreview,Wishlist,WishlistItems,Wallet
from django.views.decorators.cache import never_cache
from .forms import AddAddressForm,EditAddressForm
from products.models import Product,Category,CategoryOffer,ProductOffer
import datetime
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.validators import validate_email
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
import re
from django.contrib.auth.hashers import make_password
from adminn.models import Coupon
from django.contrib import messages
from orders.models import Order
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# Create your views here.
@never_cache

def userProfile(request,pk):   
    try:
        user = Customers.objects.get(id=pk)
        print(user)
        
        
            
        wallet, created = Wallet.objects.get_or_create(user=user)            
        
        return render(request, 'userProfile.html', {'username': user,'wallet':wallet})
    
    except ObjectDoesNotExist:
        return redirect('signin')
    
@never_cache
def useraddress(request):
    if 'username' in request.session:
        username=request.session['username']
        try:
            
            user=Customers.objects.get(username=username)
            user_id=user.id
            all_address=Address.objects.filter(customers_id=user_id)
            return render(request,'user-address.html',{'address':all_address})
        except Customers.DoesNotExist:
            return redirect('signin')
        except Address.DoesNotExist:
            return render(request,'user-address.html',{'address':[]})
    else:
        return redirect('signin')


def contains_special_characters(value):
    # Regular expression pattern to match special characters
    pattern = r'[!@#$%^&*()_+}{":;\'?/\[\]|,.<>~`]'
    return re.search(pattern, value)




def redirect_return_url(request):
    # Extract the return URL parameter
    return_url = request.GET.get('return_url')
    
    # Determine the redirect URL based on the return URL parameter
    if return_url == 'user-address':
        redirect_url = reverse('user-address')
    else:
        redirect_url = reverse('checkout')
    
    return HttpResponseRedirect(redirect_url)





@never_cache
def addaddress(request):
    if 'username' in request.session:
        username=request.session['username']
        
        try:
            user=Customers.objects.get(username=username)
        except Customers.DoesNotExist:
            return redirect ('signin')    
        
        if request.method=='POST':
            
            Addressform=AddAddressForm(request.POST,request.FILES)
            if Addressform.is_valid():
                street=Addressform.cleaned_data['street']
                city=Addressform.cleaned_data['city']
                district=Addressform.cleaned_data['district']
                state=Addressform.cleaned_data['state']
                pincode=Addressform.cleaned_data['pincode']
                
                
                if contains_special_characters(street):
                    print("yes street")
                    Addressform.add_error('street', "Dont include special character")
                if contains_special_characters(city):
                    Addressform.add_error('city', "Dont include special character")
                if contains_special_characters(district):
                    Addressform.add_error('district', "Dont include special character")
                if contains_special_characters(state):
                    Addressform.add_error('state', "Dont include special character")
                if pincode==0:
                    Addressform.add_error('pincode', "Enter a valid pincode")

                
                if Addressform.errors:
                    return render(request,'add-address.html',{'f':Addressform})
                
                
                try:
                    form=Addressform.save(commit=False)
                    form.customers_id=user.id
                    form.save()
                    return redirect_return_url(request)
                    # return redirect('user-address')
                except Exception as e:
                    print('error saving address:',e)
            else:
                
                print('Form is not valid:', Addressform.errors)
                
                return render(request,'add-address.html',{'f':Addressform})
                
    
        addaddressform=AddAddressForm()
        return render(request,'add-address.html',{'f':addaddressform})
    return redirect('home')
        
@never_cache     
def editaddress(request,pk):
    if 'username' in request.session:
        try:                  
            address = get_object_or_404(Address, id=pk)
        except Address.DoesNotExist:
            return redirect('user-address')
        
        if request.method=='POST':
            
            form = EditAddressForm(request.POST,instance=address)
            if form.is_valid():
                street=form.cleaned_data['street']
                city=form.cleaned_data['city']
                district=form.cleaned_data['district']
                state=form.cleaned_data['state']
                pincode=form.cleaned_data['pincode']
                
                
                if contains_special_characters(street):
                    print("yes street")
                    form.add_error('street', "Dont include special character")
                if contains_special_characters(city):
                    form.add_error('city', "Dont include special character")
                if contains_special_characters(district):
                    form.add_error('district', "Dont include special character")
                if contains_special_characters(state):
                    form.add_error('state', "Dont include special character")
                if pincode==0:
                    form.add_error('pincode', "Enter a valid pincode")
                
                
                
                if form.errors:
                    return render(request,'add-address.html',{'form':form})
                
                
                
                try:                    
                    form.save()
                    return redirect('user-address')
                except Exception as e:
                    print('error saving address:',e)
                
            else:
                return render(request,'edit-address.html',{'form':form})
                
            
        else:                  
            form=EditAddressForm(instance=address)
                   
        return render(request,'edit-address.html',{'instance':address,'form':form})
    return redirect('home')

def deleteaddress(request,pk):
    if 'username' in request.session:
        instance_to_be_del=Address.objects.get(id=pk)
        instance_to_be_del.delete()
        return redirect('user-address')
    return redirect('signin')
    
# cart--------

def add_to_cart(request,pk):
    if 'username' in request.session:
        try:
            print("is entered")
            try:
                product=get_object_or_404(Product,id=pk)
            except:
                return redirect('home')
            username=request.session['username']
            customer=Customers.objects.get(username=username)
            
            # category offer-----
            category_offer = CategoryOffer.objects.filter(category=product.Category,
                                                           start_date__lte=timezone.now(),
                                                           end_date__gte=timezone.now()).first()
            if category_offer:
                print("yes inside this")
                product_price = product.price - (product.price * category_offer.discount_percentage / 100)
            else:
                product_price = product.price
            
            print("product price",product_price)
            # created customer in cart if there is not customer else it get the customer
            cart, created=Cart.objects.get_or_create(customer=customer)
            
            # creating cartitem with the cart because customer is in the cart
            cart_item, created =CartItem.objects.get_or_create(cart=cart,product=product)
            return redirect('cart')
            # print("everything finished")
            # # then taking all the items from the cart
            # cart_items = CartItem.objects.filter(cart=cart)
            
            # for item in cart_items:
            #     item.total_price = product_price * item.quantity
            # total_price = sum(item.total_price for item in cart_items)

            # return render(request,'cart.html',{'cart_items': cart_items,'total_price':total_price,'product_price': product_price})
        except(Product.DoesNotExist,Customers.DoesNotExist) as e:
            print("trapped")
            return redirect ('signin')
    return redirect('signin')

def cart(request):
    print("haiiii")
    if 'username' in request.session:
        try:
            username=request.session['username']
            customer=Customers.objects.get(username=username)
            cart, created=Cart.objects.get_or_create(customer=customer)
            cart_items = CartItem.objects.filter(cart=cart)
            # products=[item.product for item in cart_items]
            # for items in cart_items:
            #     print(items.quantity)
            
            
            product_price=None
            for item in cart_items:
                
                category_offer = CategoryOffer.objects.filter(category=item.product.Category,
                                                               start_date__lte=timezone.now(),
                                                               end_date__gte=timezone.now()).first()
                
                product_offer=ProductOffer.objects.filter(product=item.product,start_date__lte=timezone.now(),end_date__gte=timezone.now()).first()
                
                
                
                
                if category_offer:
                    category_product_price = item.product.price - (item.product.price * category_offer.discount_percentage / 100)
                
                if product_offer:
                    product_product_price=item.product.price-product_offer.discount_price
                    
                if category_offer and product_offer:
                    if category_product_price < product_product_price:
                        product_price = category_product_price
                    else:
                        product_price = product_product_price
                elif category_offer:
                    product_price=category_product_price
                elif product_offer:
                    product_price = product_product_price
                    
                else:
                    product_price = item.product.price
                
                item.total_price = product_price * item.quantity
                
            total_price = sum(item.total_price for item in cart_items)
            print("totalpriceee",total_price)
            print("productprice",product_price)
            return render(request,'cart.html',{'cart_items': cart_items,'total_price':total_price,'product_price':product_price})
        except Customers.DoesNotExist:
            print("customer does not exist")
            return redirect('signin')
        except Exception as e:
            print("An error occures:",e)
            
    return redirect('signin')



def cartitemremove(request,pk):
    if 'username' in request.session:
       
        # getting the customer
        try:
            
            username=request.session['username']
            customer=Customers.objects.get(username=username)
            # getting the product
            product=Product.objects.get(id=pk)
            cart=Cart.objects.get(customer=customer)
            cart_item=CartItem.objects.get(cart=cart,product=product)
            cart_item.delete()
            return redirect('cart')
        except Customers.DoesNotExist:
            return redirect('signin')
        except(Product.DoesNotExist,Cart.DoesNotExist,CartItem.DoesNotExist):
            return redirect('cart')
        except Exception as e:
            print("an error occured",e)
    return redirect('signin')
  
  
def update_cart(request, pk):
    if request.method == 'POST':
        print("update cart")
        cart_item = get_object_or_404(CartItem, pk=pk)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
            
        
        
        
        # Update cart items and calculate total price
        cart_items = CartItem.objects.filter(cart=cart_item.cart)
        
        for item in cart_items:
            
            category_offer = CategoryOffer.objects.filter(category=item.product.Category,
                                                           start_date__lte=timezone.now(),
                                                           end_date__gte=timezone.now()).first()
            
            product_offer=ProductOffer.objects.filter(product=item.product,start_date__lte=timezone.now(),end_date__gte=timezone.now()).first()
            
            product_price=None
            
            if category_offer:
                category_product_price = item.product.price - (item.product.price * category_offer.discount_percentage / 100)
                
            if product_offer:
                    product_product_price=item.product.price-product_offer.discount_price
                    
            if category_offer and product_offer:
                if category_product_price < product_product_price:
                    product_price = category_product_price
                else:
                    product_price = product_product_price
            elif category_offer:
                    product_price=category_product_price
            elif product_offer:
                    product_price = product_product_price
            else:
                product_price = item.product.price
            
            
            item.total_price = product_price * item.quantity
            item.save()  # Save each item after updating total_price
        
        total_price = sum(item.total_price for item in cart_items)
        
        print("totalprice",total_price)
        print("productprice:::",product_price)
        # Serialize cart items data
        cart_items_html = render_to_string('cart.html', {'cart_items': cart_items, 'total_price': total_price})
        subtotal_dict = {item.pk: item.total_price for item in cart_items}
        
        return JsonResponse({'cart_items_html': cart_items_html, 'total_price': total_price, 'subtotals': subtotal_dict})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@never_cache  
def userprofile(request):
    if 'username' in request.session:
        
        try:            
            username=request.session['username']
            print(username)
            user=Customers.objects.get(username=username)
            return render(request,'userdetailprofile.html',{'user':user})
        except Customers.DoesNotExist:
            return HttpResponse("User does not exist")
        except Exception as e:
            return HttpResponse(f"an error occured:{str(e)}")
    return redirect('signin')
        
        
@never_cache 
def usereditprofile(request):
    if 'username' in request.session:
        
        user=request.session['username']
        try:
            username=Customers.objects.get(username=user) 
        
            if request.method=='POST':
                
                name=request.POST.get('name').strip()
                email=request.POST.get('email').strip()
                
                if not name or not email:
                    print("not namme")
                    error_message="enter valid username or password"
                    return render(request,'user-editprofile.html',{'username':username,'error_message':error_message})
                
                try:
                    validate_email(email)
                except ValidationError:
                    return render(request,'user-editprofile.html',{'username':username})
                
                username.username=name
                username.email=email
                del request.session['username']
                username.save()
                request.session['username']=username.username
                return redirect('user-profile')
            return render(request,'user-editprofile.html',{'username':username})
        except Customers.DoesNotExist:
            return redirect('signin')
    return redirect('signin')
  
@never_cache 
def changepassword(request):
    if 'username' in request.session:
        user=request.session['username']
        
        try:
            username=Customers.objects.get(username=user)
        except:
            error_message="An error occured while retrieving user information"
            return render(request,'user-editprofile.html',{'error_message':error_message})
        
        if request.method=='POST':
            oldpassword=request.POST.get('oldpassword').strip()
            newpassword=request.POST.get('newpassword').strip()

            if not oldpassword or not newpassword:
                error_message="please provide both old and new password"
                return render(request,'change-password.html',{'error_message':error_message})
            
            if not check_password(oldpassword,username.password):
                error_message="old password is not matching"
                return render(request,'change-password.html',{'error_message':error_message})
            
            if len(newpassword) < 8:
                error_message = "Password must be at least 8 characters long"
                return render(request, 'change-password.html', {'error_message': error_message})
        
            if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+}{":;\'?/\[\]|,.<>~`])(?=.*[^\s]).{8,}$', newpassword):
                error_message = "Password must contain at least one uppercase letter, one lowercase letter, one digit, one special character, and no spaces"
                return render(request, 'change-password.html', {'error_message': error_message})
            
            username.password=make_password(newpassword)
            username.save()
            return redirect('user-profile')

        return render(request,'change-password.html') 
    return redirect('signin')
  
  
  
  
  
  
  
  
@never_cache     
def checkout(request):
    if 'username' in request.session:
        
        try:
            username=request.session['username']
            user=Customers.objects.get(username=username)
            
            wallet, created = Wallet.objects.get_or_create(user=user)            
            
            
            
            # if request.method=='POST':
            #     return redirect('ordersuccess')
            # getting address
            user_id=user.id
            all_address=Address.objects.filter(customers_id=user_id)
            
            #getting cart items
            cart=Cart.objects.get(customer=user)
            cart_items = CartItem.objects.filter(cart=cart)
            if cart_items.exists():
                for item in cart_items:
                    
                    category_offer = CategoryOffer.objects.filter(category=item.product.Category,
                                                               start_date__lte=timezone.now(),
                                                               end_date__gte=timezone.now()).first()
            
                    product_offer=ProductOffer.objects.filter(product=item.product,start_date__lte=timezone.now(),end_date__gte=timezone.now()).first()
                    
                    if category_offer:
                        category_product_price = item.product.price - (item.product.price * category_offer.discount_percentage / 100)
                    if product_offer:
                        product_product_price=item.product.price-product_offer.discount_price
                    
                    if category_offer and product_offer:
                        if category_product_price < product_product_price:
                            product_price = category_product_price
                        else:
                            product_price = product_product_price
                    elif category_offer:
                        product_price=category_product_price
                    elif product_offer:
                        product_price = product_product_price
                    else:
                        product_price = item.product.price
                    
                    item.total_price = product_price * item.quantity
                    
                    
                    
                    
                total_price=sum(item.total_price for item in cart_items)
                
                # chceking coupon----------
                if request.POST:
                    coupon=request.POST.get('coupon')
                    print(coupon)
                    
                    try: 
                        print("try") 
                        coupon_obj=Coupon.objects.get(coupon_code=coupon,is_active=True)
                    except :
                        print("except")
                        messages.warning(request,'Invalid Coupon ID')
                        return redirect('checkout')
                    
                    if total_price < coupon_obj.min_purchase_amount:
                        messages.warning(request,f'amount should be greater than {coupon_obj.min_purchase_amount}')
                        return redirect('checkout')
                    
                    if Order.objects.filter(user=user,coupon=coupon_obj).exists():
                        print("already used")
                        messages.warning (request,'you already used the coupon.')
                        return redirect('checkout')
                        
                    cart.coupon=coupon_obj
                    cart.save()
                
                if cart.coupon:
                    total_price=total_price - cart.coupon.discount
                    
                
                
                return render(request,'checkout.html',{'alladdress':all_address,'products':cart_items,'total_price':total_price,'cart':cart,'product_price':product_price,'wallet':wallet})
            
            else:
                print("no items")
                return redirect('cart')
        except CartItem.DoesNotExist:
            print("cartitem do not exist")
            return redirect('cart')
        except Customers.DoesNotExist:
            return redirect('signin')
        except Cart.DoesNotExist:
            return redirect('cart')
        
    return redirect('signin')
 
 
def removeCoupon(request,pk):
    if 'username' in request.session:
        try:
            username=request.session['username']
            user=Customers.objects.get(username=username)
        except:
            return redirect('signin')

        cart=Cart.objects.get(customer=user)
        cart.coupon=None
        cart.save()
        return redirect('checkout')
    return redirect('signin')
       
  
  
def productreview(request,pk):
    if 'username' in request.session:
        try:
            username = request.session['username']
            user = Customers.objects.get(username=username)
        except Customers.DoesNotExist:
            return redirect('signin')
        
        try:
            print("yesss")
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            print("error")
            # Handle the case where the product does not exist
            return redirect('home')
        
        existing_review=Productreview.objects.filter(customer=user,product=product).exists()
        if request.method=='POST':
            
            
            description=request.POST.get('review_text').strip()
            rating=request.POST.get('star_rating')
            if len(description)<2:
                print("Errror")
                message="give a proper description"
                return render(request,'productreview.html',{'messages':message})
            if existing_review:
                print("reviewed")
                message = "You have already reviewed this product."
                return render(request,'productreview.html',{'messages':message})
                
            rating=Productreview.objects.create(customer=user,product=product,description=description,rating=rating)
            return redirect('orders')
        return render(request,'productreview.html')
    return redirect('signin')



# wishlist----------------
@login_required
def wishlist(request):
    
    user=request.user
    
    # try:
    #     wishlist = Wishlist.objects.get(user=user)
    #     wishlist_items = WishlistItems.objects.filter(wishlist=wishlist)
    # except Wishlist.DoesNotExist:
    #     # Handle the case when the wishlist does not exist for the user
    #     wishlist_items = []
    
    wishlist = get_object_or_404(Wishlist, user=user)
    wishlist_items = WishlistItems.objects.filter(wishlist=wishlist)
    
    return render(request, 'wishlist.html', {'wishlistitems': wishlist_items})
    
    
    # if 'username' in request.session:
    #     username = request.session['username']
    #     user = Customers.objects.get(username=username)
        
    #     wishlist=get_object_or_404(Wishlist,user=user)
    #     wishlist_items=WishlistItems.objects.filter(wishlist=wishlist)
        
            
    #     return render(request,'wishlist.html',{'wishlistitems':wishlist_items})
    # return redirect('signin')

@login_required
def addwishlist(request,pk):
    user=request.user
    # if 'username' in request.session:
    #     username = request.session['username']
    #     user = Customers.objects.get(username=username)
        
    product = get_object_or_404(Product, pk=pk)
    
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    
    wishlist_item,created = WishlistItems.objects.get_or_create(Product=product, wishlist=wishlist)
    
    return redirect('wishlist')


@login_required
def removewishlist(request,pk):
    user=request.user
    
    product = get_object_or_404(Product, pk=pk)
    
    wishlist = Wishlist.objects.get(user=user)
    wishlist_item = WishlistItems.objects.get(Product=product, wishlist=wishlist)
    wishlist_item.delete()
    return redirect('wishlist')

    
    