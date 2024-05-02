# middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from .views import signin
from customers.models import Customers

class BlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if user is blocked
            
            if request.user.is_active == False:
                # Redirect to a blocked page or any other action
                return redirect(reverse(signin))
        
        if 'username' in request.session:
            
            username=request.session['username']
            user=Customers.objects.get(username=username)
            if user.is_active == False:
                request.session.flush() 
                
                return redirect('blocked')
            
        
        response = self.get_response(request)
        return response
    
    


