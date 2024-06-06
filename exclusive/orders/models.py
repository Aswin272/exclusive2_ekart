from django.db import models
from customers.models import Customers,Address
from django.utils import timezone
from products.models import Product
from adminn.models import Coupon



# Create your models here.

class Order(models.Model):
    
    STATUS_CHOICES=(
        ('Pending','Pending'),
        ('Processing','Processing'),
        ('Shipped','Shipped'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled')
    )
    RETURN_STATUS_CHOICES = (
        ('Return Requested', 'Return Requested'),
        ('Returned', 'Returned'),
        ('Rejected', 'Rejected')
    )
    PAYMENT_STATUS_CHOICES=(
        ('Pending','Pending'),
        ('Paid','Paid')
        
    )
    
    user=models.ForeignKey(Customers,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    status=models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')
    street_address=models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    district=models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    payment = models.CharField(max_length=100)
    payment_status=models.CharField(max_length=100,choices=PAYMENT_STATUS_CHOICES,default="Pending")
    coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)
    is_return=models.BooleanField(default=False)
    return_status=models.CharField(max_length=100,choices=RETURN_STATUS_CHOICES,default='Return Requested')
    is_cancelled=models.BooleanField(default=False)


class OrderItem(models.Model):
    
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    def __str__(self):
        return f"OrderItem {self.id}"
    
    

    
 