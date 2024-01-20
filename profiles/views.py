from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.contrib.auth import logout
from .forms import ProfileForm
from .models import Profile


class ProfileView(View):
    def get(self, request):
        form = ProfileForm()
        return render(request, 'profiles/profile.html', {'form': form})

    def post(self, request):
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.first_name = form.cleaned_data['first_name']
            profile.last_name = form.cleaned_data['last_name']
            profile.birthday = form.cleaned_data['birthday']
            profile.phone_number = form.cleaned_data['phone_number']
            profile.country = form.cleaned_data['country']
            profile.postcode = form.cleaned_data['postcode']
            profile.town_or_city = form.cleaned_data['town_or_city']
            profile.street_address1 = form.cleaned_data['street_address1']
            profile.street_address2 = form.cleaned_data['street_address2']
            profile.state = form.cleaned_data['state']
            profile.is_primary_address = form.cleaned_data['is_primary_address']
            profile.save()
            messages.success(request, "Congratulations! Profile saved successfully")
        else:
            messages.warning(request, 'Invalid input data')
            print(form.errors)

        return render(request, 'profiles/profile.html', {'form': form})


@login_required
def address(request):
    profile = get_object_or_404(Profile, user=request.user)
    addresses = Profile.objects.filter(user=request.user)
    return render(request, 'profiles/address.html', {'profile': profile, 'addresses': addresses})


class AddressUpdate(View):
    def get(self, request, pk):
        address = get_object_or_404(Profile, pk=pk)
        form = ProfileForm(instance=address)
        return render(request, 'profiles/address_update.html', {'form': form, 'address': address})

    def post(self, request, pk):
        form = ProfileForm(request.POST)
        if form.is_valid():
            address = get_object_or_404(Profile, pk=pk)
            address.first_name = form.cleaned_data['first_name']
            address.last_name = form.cleaned_data['last_name']
            address.street_address1 = form.cleaned_data['street_address1']
            address.street_address2 = form.cleaned_data['street_address2']
            address.town_or_city = form.cleaned_data['town_or_city']
            address.postcode = form.cleaned_data['postcode']
            address.country = form.cleaned_data['country']
            address.phone_number = form.cleaned_data['phone_number']
            address.state = form.cleaned_data['state']
            address.is_primary_address = form.cleaned_data['is_primary_address']
            address.save()
            messages.success(request, "Your profile was successfully updated.")
            return redirect("address")
        else:
            messages.warning(request, "Invalid input data")
            return render(request, 'profiles/address_update.html', {'form': form})


@login_required
def account_settings(request):
    user = request.user
    context = {'user': user}
    return render(request, 'profiles/account_settings.html', context)


@login_required
def account_delete(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        return redirect('home')
    else:
        return render(request, 'profiles/account_delete.html')