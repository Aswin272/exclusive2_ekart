
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings




urlpatterns = [
    
    path('adminn/',views.adminn,name='adminn'),
    path('dashboard/',views.adminn_dashboard,name='adminn_dashboard'),
    path('logout/',views.logout,name='logout'),
    
    path('category/',views.category,name='category'),
    path('add-category/',views.add_category,name="add-category"),
    path('update-category/<pk>',views.UpdateCategory,name='update-category'),
    
    path('products-list',views.product_list,name='product_list'),
    path('add-products',views.add_products,name='add_products'),
    path('product-update/<pk>',views.product_update,name="product-update"),
    
    path('activeunactive_product/<pk>',views.active_unactive_product,name="active-unactive-product" ),
    # delete image
    path('delete-productImage/<pk>',views.deleteproductImage,name="delete-productImage"),
    
    path('customers/',views.admin_customer_list,name='admin-customers'),
    path('update/<pk>',views.listandunlistcustomer,name="update"),
    path('activeUnactive/<pk>',views.active_unactive_category,name='active-unactive-category'),
    
    path('upload-image/<pk>',views.uploadImage,name='upload-image'),
    
    path('admin-orders/',views.adminorders,name="admin-orders"),
    path('admin-order-detail/<pk>',views.adminOrderDetail,name="admin-order-detail"),
    
    #coupon -------
    path('admin-coupon/',views.coupon,name='admin-coupon'),
    path('add-coupon/',views.addCoupon,name='add-coupon'),
    path('edit-coupon/<pk>',views.editcoupon,name="edit-coupon"),
    path('delete-coupon/<pk>',views.deletecoupon,name="delete-coupon"),
    # path('update_status/', views.update_status, name='update_status'),
    
    #catefory offer
    path('category-offers/',views.categoryoffers,name="category-offers"),
    path('add-category-offer/', views.add_category_offer, name='add-category-offer'),
    path('edit-category-offer/<pk>',views.editCategoryOffer,name='edit-category-offer'),
    path('delete-categoryoffer/<pk>',views.deleteCategoryOffer,name="delete-categoryoffer"),
    
    #product offer------
    path('product-offers/',views.productoffers,name="product-offers"),
    path('add-product-offer/', views.add_product_offer, name='add-product-offer'),
    path('edit-product-offers/<pk>',views.editProductOffers,name="edit-product-offers"),
    path('delete-productoffer/<pk>',views.deleteProductOffer,name="delete-productoffer"),
    
    path('sales-report/',views.salesreport,name="sales-report"),
    # path('sales-report/<str:interval>/', views.generate_sales_report, name='generate_sales_report'),
    
    path('admin-brand/',views.brand,name="brand"),
    path('dashboardd/',views.dashboard,name="dashboard")

]

urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)