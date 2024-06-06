
from django.urls import path,include
from . import views


urlpatterns = [
   
    path('',views.index,name='home'),
    path('product-detail/<pk>',views.product_detail_page,name='product-detail'),
    path('all-product',views.all_products_list,name="all-product-list"),
    path('sort/',views.sort,name='sort'),
   
    path('search/',views.search,name="search")
]