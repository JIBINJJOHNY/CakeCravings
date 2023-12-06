# views.py
from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from .forms import OrderForm, OrderItemForm
from .models import Order, OrderItem
from cart.contexts import cart_contents  # Assuming you use 'cart' instead of 'bag'

import stripe
import json


class CheckoutView(FormView):
    template_name = 'checkout/checkout.html'
    form_class = OrderForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the user's shopping cart items
        cart = cart_contents(self.request)
        context['cart_items'] = cart['cart_items']

        # Get stripe public key and create a PaymentIntent
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY

        if stripe_public_key:
            context['stripe_public_key'] = stripe_public_key
            stripe.api_key = stripe_secret_key
            intent = stripe.PaymentIntent.create(
                amount=int(cart['total'] * 100),
                currency=settings.STRIPE_CURRENCY,
            )
            context['client_secret'] = intent.client_secret

        return context
