from django.contrib import admin

# Register your models here.
from .models import Category, Product, ProductVariant, Address, Order, OrderItem

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'status')
    inlines = [ProductVariantInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'payment_method', 'order_status', 'created_at')
    list_filter = ('order_status', 'payment_method')
    inlines = [OrderItemInline]

admin.site.register(Category)
admin.site.register(Address)