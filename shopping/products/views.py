from django.shortcuts import get_object_or_404,render
from . models import product2 
# Create your views here.
def products(request):
    pro = product2.objects.all()
    pfrom = None
    pto = None
    name= None
    cs =None
    if 'cs' in request.GET:
        cs = request.GET['cs']
        if not cs:
            cs='off'
            
    
    if 'searchname' in request.GET:
        name = request.GET['searchname']
        if  name:
            if cs=='on':
                 pro = pro.filter(name__contains =name)
            else:
                 pro = pro.filter(name__icontains =name)
                      
    if 'searchpricefrom' in request.GET and  'searchpricefronm' in request.GET:
        pfrom=request.GET['searchpricefronm']
        pto =request.GET['searchpricefrom']
        if pfrom and pto:
            pro=pro.filter(price__gte=pfrom,price__lte=pto)       

    context ={
        'products': pro,
        
        
    }
    return render(request , 'products/products.html', context )



def product(request, pro_id):

    context ={
        'pro':get_object_or_404(product2,pk=pro_id)
    }
    return render(request , 'products/product.html',context)


def search(request):
    return render(request ,'products/search.html' )
