from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category,Product,ProductImage,Tag,Discount
from django.utils.text import slugify

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def tag_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')

    tag_image.short_description = 'Image'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at', 'category_image']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ('name',)}

    def category_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')

    category_image.short_description = 'Image'

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('percentage', 'start_date', 'end_date', 'is_active')

class ProductImageInline(admin.TabularInline):  
    model = ProductImage
    extra = 1  # Number of empty image forms to display

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'availability', 'created_at', 'updated_at', 'price')
    list_filter = ('category', 'is_active', 'availability', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]

    fieldsets = (
        ('General Information', {
            'fields': ('name', 'slug', 'description', 'category', 'tags', 'is_active', 'availability', 'ingredients', 'has_sizes'),
        }),
        ('Pricing Information', {
            'fields': ('price', 'discount_price'),
        }),
        ('Product Specific Information', {
            'fields': ('size', 'related_products'),  # Add 'related_products' to the fields
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Automatically generate the slug based on the name
        obj.slug = slugify(obj.name, allow_unicode=True)

        # Save the product
        super().save_model(request, obj, form, change)

admin.site.register(Product, ProductAdmin)
