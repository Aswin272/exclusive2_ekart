from django.shortcuts import render,redirect
from customers.models import Customers,Address,Cart,CartItem
from .models import Order,OrderItem
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
# import razorpay
from django.conf import settings

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
            payment='razorpay'
            
            
            cart=Cart.objects.get(customer=user)
            cart_items=CartItem.objects.filter(cart=cart)
            
            total_price=sum(item.product.price * item.quantity for item in cart_items)
            
            coupon=None
            if cart.coupon:
                total_price -= cart.coupon.discount
                coupon=cart.coupon
                
                
            order=Order.objects.create(user=user,total_price=total_price,address=address,payment=payment,coupon=coupon)
            
            
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
                
                OrderItem.objects.create(order=order,product=cart_item.product,quantity=cart_item.quantity)
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
        print("ordercancel")
        item=OrderItem.objects.get(id=pk)
        quantity=item.quantity
        
        
        if item.order.payment != "cod":
            print("payment is not cod")
            if item.order.coupon:
                print("inside item.order.coupon")
                coupon_min_amount=item.order.coupon.min_purchase_amount
                
                item_price=item.product.price
                total_price=item.order.total_price
                final_price=total_price-item_price
                
                if final_price < coupon_min_amount:
                    item.order.coupon=None
                    item.order.save()
                    print("coupo removed")
            
        
        item.product.quantity+=quantity
        item.product.save()
        
        item.is_cancelled=True
        item.save()
        
        return redirect('orders')
    return redirect('signin')
    
