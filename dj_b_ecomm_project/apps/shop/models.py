

from django.db import models

# Create your models here.
class Product(models.Model):
    CATEGORY_CHOICES = [('electronics', "Electronics"),
                        ('tech', "Tech"),
                        ('sports', "Sports"),
                        ('fashion', "Fashion"),
                        ("Home", 'Home & Kitchen')
                        ]
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to="products/")
    category = models.CharField(max_length=200, choices=CATEGORY_CHOICES, default='electronics')
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    


    
