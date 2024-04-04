
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    
    path('signup/',views.signup,name='signup'),
    path('signin/',views.signin,name='signin'),
    path('otp-verification/',views.otp_verification,name='otp_verification'),
    path('resend-otp/',views.resend_otp,name='resend_otp')
    
]

