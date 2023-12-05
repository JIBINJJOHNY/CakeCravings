from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import CombinedWishlist
from inventory.models import Product

class WishlistView(View):
    """Custom view for the wishlist display page."""
    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        if request.user.is_authenticated:
            user_wishlist = CombinedWishlist.objects.get(user=request.user)
            # Retrieve products in the wishlist
            paginator = Paginator(user_wishlist.products.all(), 21)
            page = request.GET.get('page')
            products_page = paginator.get_page(page)
            context = {
                'products': products_page,
            }
            return render(
                request,
                'wishlist/custom_wishlist_display.html',
                context
            )
        else:
            return render(
                request,
                'account/login.html'
            )

class AddRemove_Wishlist(View):
    """Custom view for adding/removing products to/from wishlist using AJAX."""
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.is_ajax():
                product_id = request.POST.get('product_id')
                product = get_object_or_404(Product, id=product_id)
                user_wishlist = CombinedWishlist.objects.get(user=request.user)
                message_alert = ''
                product_in_wishlist = False
                if user_wishlist.add_to_wishlist(product):
                    product_in_wishlist = True
                    message_alert = (
                        f'{product.title} added to wishlist.'
                    )
                else:
                    user_wishlist.remove_from_wishlist(product)
                    product_in_wishlist = False
                    message_alert = (
                        f'{product.title} removed from wishlist.'
                    )
                return JsonResponse(
                    {
                        'success': True,
                        'product_in_wishlist': product_in_wishlist,
                        'message_alert': message_alert,
                    }
                )
            else:
                return JsonResponse(
                    {
                        'success': False,
                        'message_alert': 'Invalid request.',
                    }
                )
        else:
            message_alert = 'You must be logged in to modify your wishlist.'
            return JsonResponse(
                {
                    'success': False,
                    'message_alert': message_alert,
                }
            )

class Empty_WishlistView(View):
    """Custom view for emptying the wishlist using AJAX."""
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.is_ajax():
                user_wishlist = CombinedWishlist.objects.get(user=request.user)
                user_wishlist.remove_all_from_wishlist()
                return JsonResponse(
                    {
                        'success': True,
                        'message_alert': 'Wishlist is now empty.',
                    }
                )
            else:
                return JsonResponse(
                    {
                        'success': False,
                        'message_alert': 'Something went wrong.',
                    }
                )
        else:
            message_alert = 'You must be logged in to empty your wishlist.'
            return JsonResponse(
                {
                    'success': False,
                    'message_alert': message_alert,
                }
            )
