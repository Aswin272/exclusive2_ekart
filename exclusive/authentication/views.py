from django.shortcuts import render,redirect
from customers . models import Customers
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
import random
import time
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.views.decorators.cache import never_cache
import re
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned,ObjectDoesNotExist


# Create your views here.

@never_cache
def otp_verification(request):
    if request.method=='POST':
        entered_otp =request.POST.get('otp')
        
        
        stored_otp=request.session.get('otp')
        send_time=request.session.get('otp_sent_time')
        
        current_time = time.time()
        if current_time - send_time > 30:
            error_message = 'The OTP has expired.'
            return render(request, 'otp_verification.html', {'error_message': error_message})
        
        if entered_otp == stored_otp:
            username=request.session.get('username')
            email=request.session.get('email')
            # hash password
            raw_password=request.session.get('password')
            hashed_password=make_password(raw_password)
            
            user=Customers.objects.create(username=username,email=email,password=hashed_password)
            del request.session['otp']
            del request.session['otp_sent_time']
            del request.session['username']
            
            
            return redirect('signin')
        else:
            error_message='the otp incorrect'
            return render(request,'otp_verification.html',{'error_message':error_message})
    return render(request,'otp_verification.html')
        
        


@never_cache
def resend_otp(request):
    
    # Check if previous OTP is expired
    otp_sent_time = request.session.get('otp_sent_time', 0)
    if (time.time() - otp_sent_time) > 30:
        # Generate OTP only if the previous OTP is expired
        otp = random.randint(100000, 999999)
        print(otp)
        # Save OTP in session
        request.session['otp'] = str(otp)
        # Save current time in session
        request.session['otp_sent_time'] = time.time()
        # Send OTP via email
        email = request.session.get('email')
        subject = 'Resend OTP for Signup'
        message = f'Your new OTP for signup is: {otp}'
        from_email ='eecommerce094@gmail.com'
        to_email = [email]
        send_mail(subject, message, from_email, to_email)
        return redirect('otp_verification')
    else:
        error_message = 'The otp verification failed'
        return render(request,'otp_verification.html',{'error_message':error_message})




@never_cache
def signup(request):
    if 'username' in request.session:       
        return redirect('home')
    
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        stripped_username=username.strip()
        stripped_email=email.lower().strip()
        if not (username and email and password):
            error_message="all fields are required"
            return render(request,'signup.html',{'error_message':error_message})
        if Customers.objects.filter(Q(username=username) | Q(email=email)).exists():
            error_message = "Username or email already exists. Please choose different ones."
            return render(request,'signup.html',{'error_message':error_message})
        if not stripped_username:
            error_message="username field required"
            return render(request,'signup.html',{'error_message':error_message})
        if not stripped_email:
            error_message="email field required"
            return render(request,'signup.html',{'error_message':error_message})
        if len(password) < 8:
            error_message = "Password must be at least 8 characters long"
            return render(request, 'signup.html', {'error_message': error_message})
        # if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+}{":;\'?/\[\]|,.<>~`])(?=.*[^\s]).{8,}$', password):
        #     error_message = "Password must contain at least one uppercase letter, one lowercase letter, one digit, one special character, and no spaces"
        #     return render(request, 'signup.html', {'error_message': error_message})
        
        otp = random.randint(100000, 999999)
        print(otp)
        request.session['otp']=str(otp)
        request.session['otp_sent_time'] = time.time()
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = password
        
        subject = 'OTP for Signup'
        message = f'Your OTP for signup is: {otp}'
        from_email='eecommerce094@gmail.com'
        to_email=[email]
        send_mail(subject, message, from_email, to_email)
        
        return redirect('otp_verification')
          
    return render(request,'signup.html')
















def signin(request):
    if 'username' in request.session:
        return redirect('home')
    
    if request.method=='POST':
        name=request.POST.get('name')
        password=request.POST.get('password')
        
        try:
            user = authenticate(username=name, password=password)
            if user is not None and user.is_active:
                request.session['username'] = user.username
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password. Please try again.")
        except ObjectDoesNotExist:
            messages.error(request, "User does not exist.")
        except MultipleObjectsReturned:
            messages.error(request, "Multiple users with the same username. Please contact support.")
        
        return render(request, 'signin.html')
    
    return render(request, 'signin.html')





def blocked(request):
    return render(request,'signin.html')
