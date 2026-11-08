from django.urls import path
from . import views

urlpatterns = [
    # Auth & Home
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart & Order
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    # Profile & Orders
    path('account/', views.my_account, name='my_account'),

    # Admin Control Panel
    path('custom-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/orders/', views.admin_orders, name='admin_orders'),
    path('custom-admin/update-status/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),



    # --- ADMIN SUITE ROUTES ---
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # Products & Categories
    path('admin-panel/products/', views.admin_products, name='admin_products'),
    path('admin-panel/products/add/', views.admin_add_product, name='admin_add_product'),
    path('admin-panel/products/delete/<int:pk>/', views.admin_delete_product, name='admin_delete_product'),
    path('admin-panel/categories/', views.admin_categories, name='admin_categories'),
    path('admin-panel/categories/delete/<int:pk>/', views.admin_delete_category, name='admin_delete_category'),

    # Orders
    path('admin-panel/orders/', views.admin_orders, name='admin_orders'),
    path('admin-panel/orders/update/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),

    # Users
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    # Coupons
    path('admin-panel/coupons/', views.admin_coupons, name='admin_coupons'),
    path('admin-panel/coupons/delete/<int:coupon_id>/', views.admin_delete_coupon, name='admin_delete_coupon'),

    path('admin-panel/profile/', views.admin_profile, name='admin_profile'),

    path('admin-panel/products/update/<int:product_id>/', views.admin_update_product, name='admin_update_product'),
]