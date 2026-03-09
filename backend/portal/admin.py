from django.contrib import admin

from .models import Vendor, Product, Store, Sale, Purchase


class VendorAdmin(admin.ModelAdmin):
    list_display = ['vendor_number', 'vendor_name']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['brand', 'description', 'size', 'purchase_price', 'vendor']


class StoreAdmin(admin.ModelAdmin):
    list_display = ['store_id', 'city']


class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'store', 'product', 'quantity', 'revenue', 'price', 'sales_date']


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'store', 'product', 'vendor', 'quantity', 'cost', 'purchase_price', 'po_date']


admin.site.register(Vendor, VendorAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Purchase, PurchaseAdmin)
