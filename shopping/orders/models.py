from django.db import models
from django.contrib.auth.models import User
from products.models import product2


# Create your models here.
class order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    order_date=models.DateTimeField()
    details=models.ManyToManyField(product2,through='OrderDetails')
    is_finshed=models.BooleanField()


    def __str__(self):
        return 'User: '+ self.user.username + ' ,  order id : '+str(self.id)    

class OrderDetails(models.Model):
    product= models.ForeignKey(product2,on_delete=models.CASCADE)
    order=models.ForeignKey(order,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=15 , decimal_places=2)
    quantity=models.IntegerField()


    def __str__(self):
        return 'User:'+self.order.username +',product:'+ self.product.name + 'order id: '+str(self.order.id)
