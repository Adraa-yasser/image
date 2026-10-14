from django.shortcuts import render,redirect
from django.contrib import messages
from products.models import product2
from orders.models import order
from orders.models import OrderDetails
from django.utils import timezone

# Create your views here.
def add_to_cart(request):
    if 'pro_id' in request.GET and 'qty' in request.GET and 'price' in request.GET and request.user.is_authenticated and not request.user.is_anonymous:
        
        pro_id =request.GET['pro_id']
        qty=request.GET['qty']

        order1=order.objects.all().filter(user=request.user)
        if not product2.objects.all().filter(id=pro_id).exists():
           return redirect('products')
        pro=product2.objects.get(id=pro_id)
        if order1:
           #messages.success(request,'يوجد طلب قديم ')
           old_order=order.objects.get(user=request.user)
           orderdetails=OrderDetails.objects.create(product=pro,order=old_order,price=pro.price,quantity=qty)
           messages.success(request,'was added to cart for old order')
        else:
           #messages.success(request,'هنا سوف يتم عمل طلب جديد')
           new_order=order()
           new_order.user= request.user
           new_order.order_date=timezone.now()
           new_order.is_finshed=False
           new_order.save()
           orderdetails=OrderDetails.objects.create(product=pro,order=new_order,price=pro.price,quantity=qty)
           messages.success(request,'was added to cart for new order')


        return redirect('/products/'+ request.GET['pro_id'])
    else:


     return redirect('products')

def cart(request):

   context=None
   if  request.user.is_authenticated and not request.user.is_anonymous:
      if order.objects.all().filter(user=request.user):
         order1=order.objects.get(user=request.user)
         orderdetails=OrderDetails.objects.all().filter(order=order1)
         total=0
         for sub in orderdetails:
            total +=sub.price * sub.quantity
            context={
               'order':order,
               'orderdetails':orderdetails,
               'total':total,
            }
         
   return render(request,'orders/cart.html',context)





