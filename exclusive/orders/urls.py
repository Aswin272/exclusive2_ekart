from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponse



urlpatterns = [
   
    
    path('order-success/',views.orderSuccess,name="ordersuccess"),
    path('orders/',views.orders,name='orders'),
    path('order-cancel/<pk>',views.ordercancel,name="order-cancel"),
    path('order-detail/<pk>',views.orderdetail,name="order-detail"),
    
    path('payment-homepage',views.paymenthomepage,name="payment-homepage"),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    
    path('retrypayment',views.retrypayment,name="retrypayment"),
    
    path('return-request/<pk>',views.returnrequest,name="return-request"),
    
    #pdff---
    path('order_detail_pdf/<pk>',views.download_order_detail_pdf,name="download_order_detail_pdf")
]




