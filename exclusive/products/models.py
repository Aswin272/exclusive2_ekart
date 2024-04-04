from django.db import models

# Create your models here.


class Category(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField()
    is_active=models.BooleanField(default=True)
    image=models.ImageField(upload_to='media/')
    
    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    Category=models.ForeignKey(Category,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='media/')
    quantity=models.IntegerField()
    priority=models.IntegerField(default=0)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="media/")
