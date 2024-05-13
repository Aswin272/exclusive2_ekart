from django.shortcuts import render,redirect
from customers.models import Customers,Address,Cart,CartItem,Wallet,Transaction
from .models import Order,OrderItem
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
# import razorpay
from django.conf import settings
from products.models import CategoryOffer,ProductOffer
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from django.http import HttpResponse


# Create your views here.

def orderSuccess(request):
    print("order success view")
    if 'username' in request.session:
        

        if request.method == 'POST':
            print("order success view")
            username=request.session['username']
            selected_address_id=request.POST.get('selected_address')
            print(selected_address_id)
            paym=request.POST.get('checkout-pay-method')
            print(paym)
            user=Customers.objects.get(username=username)
            address=Address.objects.get(pk=selected_address_id)
            payment='wallet'
            
            
            cart=Cart.objects.get(customer=user)
            cart_items=CartItem.objects.filter(cart=cart)
            
            
            
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
                
                
        
                # if category_offer:
                #     product_price = item.product.price - (item.product.price * category_offer.discount_percentage / 100)
                # else:
                #     product_price = item.product.price
                
                # item.total_price = product_price * item.quantity
                          
            total_price=sum(item.total_price for item in cart_items)
            
            coupon=None
            if cart.coupon:
                print("yes coupon is here")
                total_price -= cart.coupon.discount
                print("total price",total_price)
                coupon=cart.coupon
                
            
            if payment=='wallet':
                print("inside the wallet")
                wallet,create=Wallet.objects.get_or_create(user=user)
                if wallet.balance >= total_price:
                    print("wallet balance ",wallet.balance)
                    wallet.balance -= total_price
                    wallet.save()
                    print("wallet after ordering",wallet.balance)
                else:
                    return HttpResponse("Error: Insufficient balance in wallet")
            
            order=Order.objects.create(user=user,total_price=total_price,
                                       street_address=address.street,
                                       city=address.city,
                                       district=address.district,
                                       state=address.state,
                                       
                                       pincode=address.pincode,
                                       payment=payment,coupon=coupon)
            
            
            # if payment=='razorpay':
                
            #     razorpay_client=razorpay.Client(auth = (settings.razor_pay_key_id , settings.key_secret))
                
            #     currency = 'INR'
            #     amount = total_price
                
            #     razorpay_order = razorpay_client.order.create(dict(amount=amount,
            #                                            currency=currency,
            #                                            payment_capture='0'))
            #     razorpay_order_id=razorpay_order['id']
            #     callback_url = 'paymenthandler/'
                
            #     context = {}
            #     context['razorpay_order_id'] = razorpay_order_id
            #     context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
            #     context['razorpay_amount'] = amount
            #     context['currency'] = currency
            #     context['callback_url'] = callback_url
                    
            
            for cart_item in cart_items:
                
                
                
                category_offer = CategoryOffer.objects.filter(category=cart_item.product.Category,
                                                               start_date__lte=timezone.now(),
                                                               end_date__gte=timezone.now()).first()
            
                product_offer=ProductOffer.objects.filter(product=cart_item.product,start_date__lte=timezone.now(),end_date__gte=timezone.now()).first()
                
                if category_offer:
                    category_product_price = cart_item.product.price - (cart_item.product.price * category_offer.discount_percentage / 100)
                if product_offer:
                    product_product_price=cart_item.product.price - product_offer.discount_price
                
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
                    product_price = cart_item.product.price
            
                last_price= product_price * cart_item.quantity
                
                
                
                OrderItem.objects.create(order=order,product=cart_item.product,quantity=cart_item.quantity,price=last_price)
                cart_item.product.quantity = F('quantity') - cart_item.quantity
                cart_item.product.save()
                
            cart_items.delete()
            
            if cart.coupon:
                cart.coupon=None
                cart.save()
            return render(request,'order-success.html')
        
        return redirect('checkout')
    return redirect('signin')


def orders(request):
    if 'username' in request.session:
    
        username=request.session['username']
        user=Customers.objects.get(username=username)
        
        orders=Order.objects.filter(user=user).order_by('-created_at')
        
        
        orderitems=[]
        for order in orders:
            orderitems.extend(OrderItem.objects.filter(order=order))
        
        return render(request,'orders.html',{'orderitems':orderitems})
             
            
    return redirect('signin')


def ordercancel(request,pk):
    
    if 'username' in request.session:
        
        username=request.session['username']
        user=Customers.objects.get(username=username)
        
        print("ordercancel")
        item=OrderItem.objects.get(id=pk)
        quantity=item.quantity
        
        coupon_amount=0
        if item.order.coupon:
            print("inside item.order.coupon")
            coupon_min_amount=item.order.coupon.min_purchase_amount
            
            item_price=item.price
            total_price=item.order.total_price
            final_price=total_price-item_price
            
            if final_price < coupon_min_amount:
                
                coupon_amount=item.order.coupon.discount
                
                item.order.coupon=None
                item.order.save()
                print("coupon removed balance amount will be reached to the wallet")
        
        
        
        if item.order.payment != "cod":
            print("inside not cod")
            amount= item.price - coupon_amount
            wallet,created=Wallet.objects.get_or_create(user=user,defaults={'balance':0})
            
            if amount > Decimal('0'):
                wallet.balance += amount
                wallet.save()
                
                Transaction.objects.create(wallet=wallet,amount=amount)
                print("balance payment will be add to your wallet",amount)
        print(item.product.quantity)
        print("quantity",quantity)            
        item.product.quantity += quantity
        item.product.save()
        
        item.is_cancelled=True
        item.save()
        
        return redirect('orders')
    return redirect('signin')
    
def orderdetail(request,pk):
    if 'username' in request.session:
        order_item = OrderItem.objects.get(pk=pk)
        order=order_item.order
        user = order.user
        
        context={
            'order_item':order_item,
            'order':order,
            'user':user
        }
        
        
        return render(request,'orderdetailpage.html',context)
    return redirect('signin')

