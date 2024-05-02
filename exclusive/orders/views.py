from django.shortcuts import render,redirect
from customers.models import Customers,Address,Cart,CartItem
from .models import Order,OrderItem
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
# import razorpay
from django.conf import settings

# Create your views here.

def orderSuccess(request):
    if 'username' in request.session:
        
        if request.method=='POST':
            
            username=request.session['username']
            selected_address_id=request.POST.get('selected_address')
            
            user=Customers.objects.get(username=username)
            address=Address.objects.get(pk=selected_address_id)
            payment="cod"
            
            cart=Cart.objects.get(customer=user)
            cart_items=CartItem.objects.filter(cart=cart)
            
            total_price=sum(item.product.price * item.quantity for item in cart_items)
            order=Order.objects.create(user=user,total_price=total_price,address=address,payment=payment)
            
            
            for cart_item in cart_items:
                
                OrderItem.objects.create(order=order,product=cart_item.product,quantity=cart_item.quantity)
                cart_item.product.quantity = F('quantity') - cart_item.quantity
                cart_item.product.save()
                
            cart_items.delete()
            
            
            return render(request,'order-success.html')
        
        
        # client=razorpay.Client(auth = (settings.razor_pay_key_id , settings.key_secret))
        # payment=client.order.create()
        
        
        return redirect('checkout')
    return redirect('signin')


def orders(request):
    if 'username' in request.session:
    
        username=request.session['username']
        user=Customers.objects.get(username=username)
        
        orders=Order.objects.filter(user=user).order_by('-created_at')
        print(orders)
        
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
        
        item.product.quantity+=quantity
        item.product.save()
        
        item.is_cancelled=True
        item.save()
        
        return redirect('orders')
    return redirect('signin')
    
