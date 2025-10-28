from django.db import models
from django.conf import settings 
from apps.shop.models import Product

# Create your models here.
class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
    
    @property
    def total_price(self):
        return self.quantity * self.product.price