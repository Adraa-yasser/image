from django.shortcuts import render ,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from . models import UserProfile1
from django.contrib import auth
from products.models import product2
import re

# Create your views here.
def signin(request):
    if request.method =='POST' and 'btnlogin' in request.POST:
        
        username=request.POST['user']
        password=request.POST['pass']

        user =auth.authenticate(username=username,password=password)

        if user is not None:
           if 'rememberme' not in request.POST:
              request.session.set_expiry(0)
           auth.login(request,user)
          # messages.success(request,'you are now logged in')
        else:
           messages.error(request,'username or password invalid ')  



        return redirect('signin')
    else:
     return render(request , 'accounts/signin.html')

def logout(request): 
   if request.user.is_authenticated:
      auth.logout(request)
   return redirect('index')
def signup(request):
      if request.method =='POST' and  'btnsignup' in request.POST:
        #variables for fields
        fname = None
        lname=None
        address=None
        address2=None
        city=None
        state=None
        zip_number=None
        email=None
        username=None
        password=None
        terms=None
        is_added=None
        #get values from the form
        if 'fname' in request.POST:fname=request.POST['fname']
        else:messages.error(request,'error in first name')
        if 'lname' in request.POST:lname=request.POST['lname']
        else:messages.error(request,'error in last name')
        if 'address'in request.POST:address= request.POST['address']
        else:messages.error(request,'error in adress')
        if 'address2'in request.POST:address2= request.POST['address2']
        else:messages.error(request,'error in address2')
        if 'city'in request.POST:city= request.POST['city']
        else:messages.error(request,'error in city')
        if 'state'in request.POST:state= request.POST['state']
        else:messages.error(request,'error in state')
        if 'zip'in request.POST:zip_number= request.POST['zip']
        else:messages.error(request,'error in zip')
        if 'email'in request.POST:email= request.POST['email']
        else:messages.error(request,'error in email')
        if 'user'in request.POST:username= request.POST['user']
        else:messages.error(request,'error in user')
        if 'pass'in request.POST:password= request.POST['pass']
        else:messages.error(request,'error in  pass')
        if 'terms'in request.POST:terms= request.POST['terms']
        
         #check the values
        if fname and lname and address and  address2 and city and state and zip_number and email and username and password:
           if terms=='on':
              #check if username is taken
              if User.objects.filter(username=username).exists():
                 messages.error(request,'this username is taken')
              else:
                 #check if email is taken
                 if User.objects.filter(email=email).exists():
                    messages.error(request,'this email is taken')
                 else:
                   

                    try: 
                       #code
                       #add user
                       user=User.objects.create_user(first_name=fname,last_name=lname,email=email,username=username,password=password)
                       user.save()
                       #add user profile
                       userprofile=UserProfile1(user=user,address=address,
                                                address2=address2 ,city=city,
                                                state=state,
                                                zip_number=zip_number)
                       userprofile.save()
                       #clear fields
                       fname =''
                       lname=''
                       address=''
                       address2=''
                       city=''
                       state=''
                       zip_number=''
                       email=''
                       username=''
                       password=''
                       terms=None
                       #success message
                       messages.success(request,'youer account is create')
                       is_added=True
                    except:
                       #code
                       messages.error(request,'invalid email')    
           

                   
                  
           else:
              messages.error(request,'you must agree to the trems')
        else:
           messages.error(request,'check empty fields')

        return render(request , 'accounts/signup.html',{'fname':fname,'lname':lname,'address':address,
                                                        'address2':address2,'city':city,'state':state,
                                                        'zip':zip_number,
                                                        'email':email,'user':username,
                                                        'pass':password,'is_added':is_added})
      else:
         return render(request , 'accounts/signup.html')


def profile(request):
     if request.method =='POST' and  'btnsave' in request.POST:
             if request.user is not None and request.user.id !=None:
          
                
                 messages.success(request,'your data has been saved')
             return redirect('profile')
     else:
         if  request.user.is_anonymous:return redirect('index')
         if request.user is not None:
                context=None
                
                
                context={
               'fname':request.user.first_name,
               'lname':request.user.last_name,
               'email':request.user.email,
               'user':request.user.username,
               'pass':request.user.password

            } 
                return render(request , 'accounts/profile.html',context)
         else:
            return redirect('profile')



def product_favorite(request, pro_id) :
    if request.user.is_authenticated and not request.user.is_authenticated:
        pro_fav=product2.objects.get(pk=pro_id)
        if UserProfile1.objects.filter(user=request.user,product_favorites=pro_fav).exists():
            messages.success(request,'already product in the favorite list')
               
        else:
            userprofil=UserProfile1.objects.get(user=request.user)
            userprofil.product_favorites.add(pro_fav)
    else:
        messages.error(request,'youe must signin')   
    return redirect('/products/'+str(pro_id))