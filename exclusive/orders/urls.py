from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
   
    
    path('order-success/',views.orderSuccess,name="ordersuccess"),
    path('orders/',views.orders,name='orders'),
    path('order-cancel/<pk>',views.ordercancel,name="order-cancel")
]