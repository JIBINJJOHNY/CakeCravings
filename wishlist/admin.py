from django.contrib import admin
from .models import Wishlist

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'user__email', 'created_at')

    def get_products_count(self, obj):
        return obj.products.count()

    get_products_count.short_description = 'Number of Products'

    readonly_fields = ('created_at',)

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Products in Wishlist', {
            'fields': ('products',)
        }),
        ('Date Information', {
            'fields': ('created_at',),
        }),
    )

    filter_horizontal = ('products',)
