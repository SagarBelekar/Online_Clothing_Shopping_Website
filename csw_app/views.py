import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum

from .models import (
    Category,
    Product,
    ProductVariant,
    ProductImage,
    Cart,
    Address,
    Order,
    OrderItem,
    Coupon
)

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def is_admin(user):
    return user.is_authenticated and user.is_staff


# ---------------------------------------------------------
# Authentication & User Views
# ---------------------------------------------------------
def register_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        phone = request.POST.get('phone')
        addr = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        p = request.POST.get('password')
        cp = request.POST.get('confirm_password')

        if p != cp:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'auth/register.html')

        if User.objects.filter(username=u).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'auth/register.html')

        if User.objects.filter(email=e).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'auth/register.html')

        # User create karein
        user = User.objects.create_user(username=u, email=e, password=p)

        # Address aur mobile number Address model me save karein
        Address.objects.create(
            user=user,
            address=addr,
            city=city,
            state=state,
            pincode=pincode,
            phone=phone
        )

        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')

    return render(request, 'auth/register.html')


def home_view(request):
    # 1. Agar user login NAHI hai, to direct login page par bhej do
    if not request.user.is_authenticated:
        return redirect('login')

    # 2. Agar user admin hai, to Admin Dashboard par bhejo
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')

    # 3. Normal logged-in user ko store ka home page dikhao
    categories = Category.objects.all()
    products = Product.objects.filter(status=True)[:8]
    return render(request, 'user/home.html', {'categories': categories, 'products': products})


def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ---------------------------------------------------------
# Product & Shopping Views
# ---------------------------------------------------------
def product_list(request):
    category_id = request.GET.get('category')
    categories = Category.objects.all()
    if category_id:
        products = Product.objects.filter(category_id=category_id, status=True)
    else:
        products = Product.objects.filter(status=True)
    return render(request, 'user/product_list.html', {'products': products, 'categories': categories})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    variants = product.variants.all()

    # Unique images collect karna
    gallery_list = []
    seen_names = set()

    if product.image:
        main_filename = product.image.name.split('/')[-1]
        gallery_list.append(product.image.url)
        seen_names.add(main_filename)

    for extra in product.images.all():
        if extra.image:
            extra_filename = extra.image.name.split('/')[-1]
            if extra_filename not in seen_names and extra.image.url not in gallery_list:
                gallery_list.append(extra.image.url)
                seen_names.add(extra_filename)

    return render(request, 'user/product_detail.html', {
        'product': product,
        'variants': variants,
        'gallery_list': gallery_list
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    size = request.POST.get('size', 'M')
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product, size=size)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')


@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, 'user/cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def remove_from_cart(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)
    item.delete()
    return redirect('view_cart')


# ---------------------------------------------------------
# Checkout (Supports Both: Single Item & Full Cart)
# ---------------------------------------------------------
@login_required
def checkout_view(request):
    item_id = request.GET.get('item_id') or request.POST.get('item_id')

    # Agar single item checkout par click kiya ho
    if item_id:
        cart_items = Cart.objects.filter(id=item_id, user=request.user)
    else:
        cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.warning(request, "No items to checkout.")
        return redirect('view_cart')

    total = sum(item.subtotal() for item in cart_items)

    if request.method == 'POST':
        address = Address.objects.create(
            user=request.user,
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            phone=request.POST.get('phone')
        )
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total,
            payment_method=request.POST.get('payment_method', 'Cash on Delivery'),
            order_status='Pending'
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                size=item.size,
                quantity=item.quantity,
                price=item.product.discount_price if item.product.discount_price else item.product.price
            )

        # Sirf check out kiye huye item(s) ko cart se delete karein
        cart_items.delete()
        return redirect('order_success', order_id=order.id)

    return render(request, 'user/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'item_id': item_id
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'user/order_success.html', {'order': order})


@login_required
def my_account(request):
    address_info = Address.objects.filter(user=request.user).last()
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'address_info': address_info,
        'orders': orders,
    }
    return render(request, 'user/account.html', context)


# ---------------------------------------------------------
# Admin Panel Views
# ---------------------------------------------------------
@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    total_sales = Order.objects.filter(order_status='Delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_users = User.objects.filter(is_staff=False).count()

    status_counts = {
        'Pending': Order.objects.filter(order_status='Pending').count(),
        'Confirmed': Order.objects.filter(order_status='Confirmed').count(),
        'Shipped': Order.objects.filter(order_status='Shipped').count(),
        'Delivered': Order.objects.filter(order_status='Delivered').count(),
        'Cancelled': Order.objects.filter(order_status='Cancelled').count(),
    }

    low_stock = ProductVariant.objects.filter(stock__lt=5).select_related('product')[:5]
    recent_orders = Order.objects.order_by('-created_at')[:5]

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_users': total_users,
        'status_counts': list(status_counts.values()),
        'status_labels': list(status_counts.keys()),
        'low_stock': low_stock,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@user_passes_test(is_admin, login_url='login')
def admin_products(request):
    products = Product.objects.all().select_related('category').prefetch_related('variants')
    return render(request, 'admin_panel/products.html', {'products': products})


@user_passes_test(is_admin, login_url='login')
def admin_add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price') or None
        primary_image = request.FILES.get('image')  # Main thumbnail

        category = get_object_or_404(Category, id=category_id)
        product = Product.objects.create(
            name=name,
            category=category,
            description=description,
            price=price,
            discount_price=discount_price,
            image=primary_image,
            status=True
        )

        # 1. Multiple Gallery Images Save Karein
        extra_images = request.FILES.getlist('extra_images')
        for img in extra_images:
            ProductImage.objects.create(product=product, image=img)

        # 2. Size-wise Stock Variants Save Karein (S, M, L, XL)
        for s in ['S', 'M', 'L', 'XL']:
            val = request.POST.get(f'stock_{s}', 10)
            try:
                qty = int(val)
            except (ValueError, TypeError):
                qty = 0
            ProductVariant.objects.create(product=product, size=s, color='Standard', stock=qty)

        messages.success(request, 'Product, variants, aur multiple images successfully add ho gaye!')
        return redirect('admin_products')

    return render(request, 'admin_panel/add_product.html', {'categories': categories})


@user_passes_test(is_admin, login_url='login')
def admin_update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()

    # Current S, M, L, XL stock nikalna
    stock_dict = {'S': 0, 'M': 0, 'L': 0, 'XL': 0}
    for v in product.variants.all():
        if v.size in stock_dict:
            stock_dict[v.size] = v.stock

    if request.method == 'POST':
        product.name = request.POST.get('name')
        cat_id = request.POST.get('category')
        if cat_id:
            product.category = Category.objects.get(id=cat_id)

        product.price = request.POST.get('price')
        discount_price = request.POST.get('discount_price')
        product.discount_price = discount_price if discount_price else None
        product.description = request.POST.get('description')

        # 1. Main Cover Image Update
        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()

        # 2. Add New Multiple Gallery Images
        new_gallery_images = request.FILES.getlist('extra_images')
        for img in new_gallery_images:
            ProductImage.objects.create(product=product, image=img)

        # 3. Update S, M, L, XL Stock
        for size in ['S', 'M', 'L', 'XL']:
            val = request.POST.get(f'stock_{size}', 0)
            try:
                qty = int(val)
            except (ValueError, TypeError):
                qty = 0

            variant, _ = ProductVariant.objects.get_or_create(
                product=product,
                size=size,
                defaults={'stock': qty, 'color': 'Standard'}
            )
            variant.stock = qty
            variant.save()

        messages.success(request, f"'{product.name}' details and images updated successfully!")
        return redirect('admin_products')

    return render(request, 'admin_panel/update_product.html', {
        'product': product,
        'categories': categories,
        'stock_dict': stock_dict
    })


@user_passes_test(is_admin, login_url='login')
def admin_delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('admin_products')


@user_passes_test(is_admin, login_url='login')
def admin_categories(request):
    if request.method == 'POST':
        name = request.POST.get('category_name')
        img = request.FILES.get('image')
        if name:
            Category.objects.create(category_name=name, image=img)
            messages.success(request, 'Category added!')
            return redirect('admin_categories')
    categories = Category.objects.all()
    return render(request, 'admin_panel/categories.html', {'categories': categories})


@user_passes_test(is_admin, login_url='login')
def admin_delete_category(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    cat.delete()
    messages.success(request, 'Category deleted.')
    return redirect('admin_categories')


@user_passes_test(is_admin, login_url='login')
def admin_users(request):
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users})


@user_passes_test(is_admin, login_url='login')
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    messages.info(request, f"User status changed to {'Active' if user.is_active else 'Blocked'}.")
    return redirect('admin_users')


@user_passes_test(is_admin, login_url='login')
def admin_coupons(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        discount = request.POST.get('discount')
        if Coupon.objects.filter(code=code).exists():
            messages.error(request, 'Coupon code already exists!')
        else:
            Coupon.objects.create(code=code, discount_percent=discount)
            messages.success(request, 'Coupon added!')
            return redirect('admin_coupons')
    coupons = Coupon.objects.all()
    return render(request, 'admin_panel/coupons.html', {'coupons': coupons})


@user_passes_test(is_admin, login_url='login')
def admin_delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    messages.success(request, 'Coupon removed.')
    return redirect('admin_coupons')


@user_passes_test(is_admin, login_url='login')
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/orders.html', {'orders': orders})


@user_passes_test(is_admin, login_url='login')
def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)
    order.order_status = status
    order.save()
    messages.success(request, f"Order #{order.id} status changed to {status}.")
    return redirect('admin_orders')


@user_passes_test(is_admin, login_url='login')
def admin_profile(request):
    admin_user = request.user
    if request.method == 'POST':
        admin_user.first_name = request.POST.get('first_name', '')
        admin_user.last_name = request.POST.get('last_name', '')
        admin_user.email = request.POST.get('email', '')

        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password:
            if new_password == confirm_password:
                admin_user.set_password(new_password)
                admin_user.save()
                update_session_auth_hash(request, admin_user)
                messages.success(request, 'Profile and password updated successfully!')
                return redirect('admin_profile')
            else:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'admin_panel/profile.html', {'admin_user': admin_user})

        admin_user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('admin_profile')

    return render(request, 'admin_panel/profile.html', {'admin_user': admin_user})