from django.shortcuts import render
from django.http import HttpResponse
from products.models import product2
# Create your views here.

def index(requset):
    context ={
        'products': product2.objects.all(),

    }
    return render( requset , 'pages/index.html',context)


def about(requset):
    return render(requset,'pages/about.html')