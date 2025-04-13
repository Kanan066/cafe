# cart/models.py

from django.db import models

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return self.name

ORDER_STATUS = [
     ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('preparing', 'Preparing'),
    ('out-for-delivery', 'Out for Delivery'),
    ('delivered', 'Delivered'),  
    ('declined', 'Declined'),
]

class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
