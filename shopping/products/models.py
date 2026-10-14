from django.db import models
from datetime import datetime
# Create your models here.
  
class product2(models.Model):
     name= models.CharField(max_length=150)
     price = models.DecimalField(max_digits=15 , decimal_places=2)
     image = models.ImageField(upload_to='photos/%y/%m/%d')
     active = models.BooleanField(default = True)

     def __str__(self):
         return self.name
     
   