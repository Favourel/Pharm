from django.contrib import admin
from django.shortcuts import render, HttpResponseRedirect
from .models import *
from django.db.models import Q, F
from django.http import HttpResponse
import csv


# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "date"]
    list_per_page = 10


class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "product_purchase", "date_posted"]
    search_fields = ["name", "description"]
    list_filter = ['date_posted', "category__name"]
    actions = ['apply_discount', "remove_discount", "export_products"]
    list_per_page = 10

    def apply_discount(self, request, queryset):
        if 'apply' in request.POST:
            queryset.update(price=F('price') * float(0.9))

            self.message_user(request,
                              "Applied discount on {} product".format([i.name for i in queryset]))
            return HttpResponseRedirect(request.get_full_path())

        return render(request,
                      'products/test.html',
                      context={'products': queryset})

    apply_discount.short_description = 'Apply 10%% discount'

    def remove_discount(self, request, queryset):
        queryset.update(price=F('price') / float(0.9))
        self.message_user(request,
                          "Removed discount on {} product".format([i.name for i in queryset]))

    remove_discount.short_description = 'Remove 10%% discount'

    def export_products(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'name', 'price', 'description',
                         'category', "product_purchase", "date_posted"])
        products = queryset.values_list('id', 'name', 'price', 'description',
                                        'category__name', "product_purchase", "date_posted")
        for product in products:
            writer.writerow(product)
        return response

    export_products.short_description = 'Download as csv'


class CheckoutAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "quantity", "date_posted", "complete"]
    list_filter = ['date_posted', "complete", 'user']
    search_fields = ["user__username", "product__name"]
    list_per_page = 10


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_posted']
    search_fields = ["user__username"]
    filter_horizontal = ['order_item']
    list_filter = ['user', 'date_posted']
    list_per_page = 10


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Checkout, CheckoutAdmin)
admin.site.register(Order, OrderAdmin)
