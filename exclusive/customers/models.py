from django.db import models
from django.contrib.auth.models import AbstractUser
from products.models import Product
from adminn.models import Coupon

# Create your models here.


class Customers(AbstractUser):
    referrel_code=models.CharField(max_length=100)
    pass


class Address(models.Model):
    customers=models.ForeignKey(Customers,on_delete=models.CASCADE)
    street=models.CharField()
    city=models.CharField(max_length=100)
    district=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    pincode=models.IntegerField()
    
class Cart(models.Model):
    customer=models.ForeignKey(Customers,on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
  
  
class Productreview(models.Model):
    customer=models.ForeignKey(Customers,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    rating=models.IntegerField()
    description=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)


class Wallet(models.Model):
    user=models.OneToOneField(Customers,on_delete=models.CASCADE)
    balance=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    
    def __str__(self):
        return f"Wallet of {self.user.username}"
    
class Transaction(models.Model):
    wallet=models.ForeignKey(Wallet,on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    time=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Transaction of {self.amount} for {self.wallet.user.username} at {self.time}"
    
    
class Wishlist(models.Model):
    user=models.OneToOneField(Customers,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user
    
    
class WishlistItems(models.Model):
    Product=models.ForeignKey(Product,on_delete=models.CASCADE)
    wishlist=models.ForeignKey(Wishlist,on_delete=models.CASCADE)
    

