from django.shortcuts import render,redirect
from customers.models import Customers,Address,Cart,CartItem,Wallet,Transaction
from .models import Order,OrderItem
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
import razorpay
from django.conf import settings
from products.models import CategoryOffer,ProductOffer
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.conf.urls import handler404
from django.contrib import messages

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
            try:
                
                address=Address.objects.get(pk=selected_address_id)
            except Address.DoesNotExist:
                return HttpResponse("Error:Addrss does not exist")
            payment=paym
            
            
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
                    
                if item.quantity > item.product.quantity:
                    print("yess it is bigger")
                    # messages.error(request, f"Quantity for {cart_item.product.name} exceeds available stock.")
                    return redirect('checkout')
                
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
            
            print(total_price)
            
            
            
            #redirecting to payment home page 
            
            
                
                # print("yrssd")
                
                # request.session['address']=address.pk
                # request.session['total_price'] = str(total_price)
                
            
                
        
            if payment=='wallet':
                print("inside the wallet")
                wallet=Wallet.objects.get(user=user)
                if wallet.balance >= total_price:
                    print("wallet balance ",wallet.balance)
                    wallet.balance -= total_price
                    wallet.save()
                    
                    Transaction.objects.create(wallet=wallet,amount=total_price)
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
            
            if payment=='wallet':
                order.payment_status='Paid'
                order.save()
                
            
            
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
                    
                # if cart_item.quantity > cart_item.product.quantity:
                #     print("yess it is bigger")
                #     # messages.error(request, f"Quantity for {cart_item.product.name} exceeds available stock.")
                #     return redirect('checkout')
                    
            
                last_price= product_price * cart_item.quantity
                
                
                
                OrderItem.objects.create(order=order,product=cart_item.product,quantity=cart_item.quantity,price=last_price)
                cart_item.product.quantity = F('quantity') - cart_item.quantity
                cart_item.product.save()
                
            cart_items.delete()
            
            if cart.coupon:
                cart.coupon=None
                cart.save()
            
            print("order_id",order.id)
            if payment=='razorpay':
                # payment_data = {
                #     'address': address.pk,
                #     'total_price': str(total_price),
                #     'order_id':order.id
                # }
                
                
                request.session['total_price'] = str(total_price)
                request.session['order_id'] = order.id
                
                # print("yrssd")
                
                # request.session['address']=address.pk
                # request.session['total_price'] = str(total_price)
                
                return redirect('payment-homepage')
            
            
            return render(request,'order-success.html')
        
        return redirect('checkout')
    return redirect('signin')




@login_required
def orders(request):
    user=request.user
    
    orders=Order.objects.filter(user=user).order_by('-created_at')
    
    return render(request,'orders.html',{'orders':orders})





# def orders(request):
#     if 'username' in request.session:
    
#         username=request.session['username']
#         user=Customers.objects.get(username=username)
        
#         orders=Order.objects.filter(user=user).order_by('-created_at')
        
        
#         orderitems=[]
#         for order in orders:
#             orderitems.extend(OrderItem.objects.filter(order=order))
        
#         return render(request,'orders.html',{'orderitems':orderitems})
             
            
#     return redirect('signin')




def ordercancel(request,pk):
    if 'username' in request.session:
        
        username=request.session['username']
        user=Customers.objects.get(username=username)
        
        order=Order.objects.get(id=pk)
        orderitem=OrderItem.objects.filter(order=order)
        for item in orderitem:
            item.product.quantity +=item.quantity
            item.product.save()
        if order.coupon:
            order.coupon=None
            
        if order.payment != 'cod':
            total_price=order.total_price
            wallet=Wallet.objects.get(user=user)
            wallet.balance += total_price
            wallet.save() 
            
            Transaction.objects.create(wallet=wallet,amount=total_price)
        
        order.is_cancelled = True
        order.save()
        return redirect('orders')
    return redirect('signin')
        






# def ordercancel(request,pk):
    
#     if 'username' in request.session:
        
#         username=request.session['username']
#         user=Customers.objects.get(username=username)
        
#         print("ordercancel")
#         item=OrderItem.objects.get(id=pk)
#         quantity=item.quantity
        
#         coupon_amount=0
#         if item.order.coupon:
#             print("inside item.order.coupon")
#             coupon_min_amount=item.order.coupon.min_purchase_amount
            
#             item_price=item.price
#             total_price=item.order.total_price
#             final_price=total_price-item_price
            
#             if final_price < coupon_min_amount:
                
#                 coupon_amount=item.order.coupon.discount
                
#                 item.order.coupon=None
#                 item.order.save()
#                 print("coupon removed balance amount will be reached to the wallet")
        
        
        
#         if item.order.payment != "cod":
#             print("inside not cod")
#             amount= item.price - coupon_amount
#             wallet,created=Wallet.objects.get_or_create(user=user,defaults={'balance':0})
            
#             if amount > Decimal('0'):
#                 wallet.balance += amount
#                 wallet.save()
                
#                 Transaction.objects.create(wallet=wallet,amount=amount)
#                 print("balance payment will be add to your wallet",amount)
#         print(item.product.quantity)
#         print("quantity",quantity)            
#         item.product.quantity += quantity
#         item.product.save()
        
#         item.is_cancelled=True
#         item.save()
        
#         return redirect('orders')
#     return redirect('signin')
  
  
@login_required
def orderdetail(request,pk):
    try:
        order = get_object_or_404(Order, pk=pk, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        total_order_price = sum(item.price for item in order_items)

        return render(request,'orderdetailpage.html', {'order': order, 'order_items': order_items, 'total_order_price': total_order_price})
    except Exception as e:
        return render(request,'404.html')
 
 
  
    
# def orderdetail(request,pk):
#     if 'username' in request.session:
#         order_item = OrderItem.objects.get(pk=pk)
#         order=order_item.order
#         user = order.user
        
#         context={
#             'order_item':order_item,
#             'order':order,
#             'user':user
#         }
        
        
#         return render(request,'orderdetailpage.html',context)
#     return redirect('signin')

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))



def paymenthomepage(request):
    
    # total_price = request.session['total_price']
    # address=request.session['address']
    # print(address)
    # print(total_price)
    # total_price = request.session.get('total_price')
    print("home page")
    
    
    total_price=Decimal(request.session.get('total_price'))
    
    print(total_price)
    
    currency='INR'
    
    
    
    amount=float(total_price) * 100
    print(amount)
    
    
    razorpay_order = razorpay_client.order.create(dict(amount=amount,currency=currency,payment_capture='0'))
    
    razorpay_order_id=razorpay_order['id']
    print(razorpay_order)
    print(razorpay_order_id)
    callback_url = 'paymenthandler/'
    
    context={}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
    
    return render(request, 'payment.html', context=context)

@csrf_exempt
def paymenthandler(request):
    if 'username' in request.session:
        
        if request.method =='POST':
            try:
                
                payment_id = request.POST.get('razorpay_payment_id', '')
                razorpay_order_id = request.POST.get('razorpay_order_id', '')
                signature = request.POST.get('razorpay_signature', '')
                params_dict = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                }
                
                
                result = razorpay_client.utility.verify_payment_signature(
                    params_dict)
                if result is not None:
                    # taking total price from session
                    
                    total_price=request.session.get('total_price')
                    
                    # if payment_data:
                    #     address_id = payment_data.get('address')
                    #     total_price = Decimal(payment_data.get('total_price'))
        

        
                    

                    amount=float(total_price) * 100
                    try:
                        print("success try")
                        # capture the payemt
                        razorpay_client.payment.capture(payment_id, amount)
                        
                        order_id=request.session.get('order_id')
                        print("ordeeeeerrrid",order_id)
                        order=Order.objects.get(id=order_id)
                        order.payment_status='Paid'
                        order.save()
                        
                        session_data = []
                        for key, value in request.session.items():
                            session_data.append(f'{key}: {value}')
                        
                        session_details = '<br>'.join(session_data)
                        
                        print(session_details)
                        
                        del request.session['total_price']
                        del request.session['order_id']
                        
                        
                        
                        
                        
                        
                        
                        
                        # #getting details tto create an order
                        # username=request.session['username']
                        # user=Customers.objects.get(username=username)
                        
                        # #getting cart and cartitems
                        # cart=Cart.objects.get(customer=user)
                        # cart_items=CartItem.objects.filter(cart=cart)
                        
                        # for item in cart_items:
                    
                        #     category_offer = CategoryOffer.objects.filter(category=item.product.Category,
                        #                                                 start_date__lte=timezone.now(),
                        #                                                 end_date__gte=timezone.now()).first()
                            
                            
                            
                        #     product_offer=ProductOffer.objects.filter(product=item.product,start_date__lte=timezone.now(),end_date__gte=timezone.now()).first()
                                
                        #     if category_offer:
                        #         category_product_price = item.product.price - (item.product.price * category_offer.discount_percentage / 100)
                        #     if product_offer:
                        #         product_product_price=item.product.price-product_offer.discount_price
                            
                        #     if category_offer and product_offer:
                        #         if category_product_price < product_product_price:
                        #             product_price = category_product_price
                        #         else:
                        #             product_price = product_product_price
                        #     elif category_offer:
                        #         product_price=category_product_price
                        #     elif product_offer:
                        #         product_price = product_product_price
                        #     else:
                        #         product_price = item.product.price
                            
                        #     item.total_price = product_price * item.quantity
                        
                        # total_price=sum(item.total_price for item in cart_items)
                        
                        
                        # coupon=None
                        # if cart.coupon:
                        #     print("yes coupon is here")
                        #     total_price -= cart.coupon.discount
                        #     print("total price",total_price)
                        #     coupon=cart.coupon
                        
                        
                        # order=Order.objects.create(user=user,total_price=total_price,
                        #                street_address=address.street,
                        #                city=address.city,
                        #                district=address.district,
                        #                state=address.state,
                                       
                        #                pincode=address.pincode,
                        #                payment='razorpay',coupon=coupon)
                        
                        
                        # for cart_item in cart_items:
                 
                        #     category_offer = CategoryOffer.objects.filter(category=cart_item.product.Category,
                        #                                                 start_date__lte=timezone.now(),
                        #                                                 end_date__gte=timezone.now()).first()
                        
                        #     product_offer=ProductOffer.objects.filter(product=cart_item.product,start_date__lte=timezone.now(),end_date__gte=timezone.now()).first()
                            
                        #     if category_offer:
                        #         category_product_price = cart_item.product.price - (cart_item.product.price * category_offer.discount_percentage / 100)
                        #     if product_offer:
                        #         product_product_price=cart_item.product.price - product_offer.discount_price
                            
                        #     if category_offer and product_offer:
                        #         if category_product_price < product_product_price:
                        #             product_price = category_product_price
                        #         else:
                        #             product_price = product_product_price
                        #     elif category_offer:
                        #         product_price=category_product_price
                        #     elif product_offer:
                        #         product_price = product_product_price
                        #     else:
                        #         product_price = cart_item.product.price
                        
                        #     last_price= product_price * cart_item.quantity
                            
                            
                            
                        #     OrderItem.objects.create(order=order,product=cart_item.product,quantity=cart_item.quantity,price=last_price)
                        #     cart_item.product.quantity = F('quantity') - cart_item.quantity
                        #     cart_item.product.save()
                            
                        # cart_items.delete()
                        
                        # if cart.coupon:
                        #     cart.coupon=None
                        #     cart.save()
                        
                        
                        # render success page on successful caputre of payment
                        return render(request, 'order-success.html')
                    except:
                        print("payment failed")
                        # if there is an error while capturing payment.
                        return render(request, 'paymentfail.html')
                    
                else:
    
                    # if signature verification fails.
                    
                    return render(request, 'paymentfail.html')
                
            except:
    
                # if we don't find the required parameters in POST data
                return HttpResponseBadRequest()
        else:
        # if other than POST request is made.
            return HttpResponseBadRequest()
    return redirect('signin')
    
    
    
def returnrequest(request,pk):
    if 'username' in request.session:
        print("reached")
        order=Order.objects.get(id=pk)
        
        order.is_return=True
        order.save()
        return redirect('orders')
    return redirect('signin')


@login_required
def download_order_detail_pdf(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    total_order_price = sum(item.price for item in order_items)

    # Render the order detail template as a string
    html_template = render_to_string('orderdetailpdf.html', {'order': order, 'order_items': order_items, 'total_order_price': total_order_price})

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_detail_{pk}.pdf"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        html_template,
        dest=response,
        encoding='UTF-8'
    )

    if pisa_status.err:
        return HttpResponse('Error generating PDF file')

    return response


def retrypayment(request):
    order_id=request.POST.get('order_id')
    print(order_id)
    order=Order.objects.get(id=order_id)
    total_price=order.total_price

    
    request.session['total_price'] = str(total_price)
    request.session['order_id'] = order.id
    
    currency='INR'
    
    
    
    amount=float(total_price) * 100
    print(amount)
    
    
    razorpay_order = razorpay_client.order.create(dict(amount=amount,currency=currency,payment_capture='0'))
    
    razorpay_order_id=razorpay_order['id']
    print(razorpay_order)
    print(razorpay_order_id)
    callback_url = 'paymenthandler/'
    
    
    
    context={}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
    
    return render(request, 'payment.html', context=context)


def custom_404_view(request, exception):
    requested_url = request.path_info
    context = {'requested_url': requested_url}
    return render(request, '404.html', context)

