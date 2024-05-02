from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('userProfile/<pk>',views.userProfile,name='userProfile'),
    path('user-address/',views.useraddress,name='user-address'),
    path('add-address/',views.addaddress,name='add-address'),
    path('edit-address/<pk>',views.editaddress,name='edit-address'),
    path('del-address/<pk>',views.deleteaddress,name='del-address'),
    path('user-profile/',views.userprofile,name='user-profile'),
    path('user-editprofile',views.usereditprofile,name="user-editprofile"),
    path('change-password/',views.changepassword,name="change-password"),
    
    path('add-to-cart/<pk>',views.add_to_cart,name='add_to_cart'),
    path('cart/',views.cart,name="cart"),
    path('cartitem-remove/<pk>',views.cartitemremove,name="cartitem-remove"),
    path('update_cart/<int:pk>/',views.update_cart, name='update-cart-item'),
    
    path('checkout/',views.checkout,name="checkout"),
    
    path('product-review/<pk>',views.productreview,name="product-review")
]