from django.db import models
from customers.models import Customers,Address
from django.utils import timezone
from products.models import Product
from adminn.models import Coupon



# Create your models here.

class Order(models.Model):
    
    user=models.ForeignKey(Customers,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    address=models.ForeignKey(Address,on_delete=models.CASCADE)
    payment = models.CharField(max_length=100)
    coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)
    

class OrderItem(models.Model):
    STATUS_CHOICES=(
        ('Pending','Pending'),
        ('Processing','Processing'),
        ('Shipped','Shipped'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled')
    )
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status=models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')
    is_cancelled=models.BooleanField(default=False)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    def __str__(self):
        return self.product
    
    

    
 