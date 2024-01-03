from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .forms import ProfileForm
from .models import  Profile
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import AuthenticationForm

class ProfileView(View):
    def get(self, request):
        form = ProfileForm()
        return render(request, 'profiles/profile.html', {'form': form})

    def post(self, request):
        form = ProfileForm(request.POST)
        if form.is_valid():
            # Retrieve the user's profile or create a new one
            profile, created = Profile.objects.get_or_create(user=request.user)

            # Update the profile fields
            profile.first_name = form.cleaned_data['first_name']
            profile.last_name = form.cleaned_data['last_name']
            profile.birthday = form.cleaned_data['birthday']
            profile.phone_number = form.cleaned_data['phone_number']
            profile.country = form.cleaned_data['country']
            profile.postcode = form.cleaned_data['postcode']
            profile.town_or_city = form.cleaned_data['town_or_city']
            profile.street_address1 = form.cleaned_data['street_address1']
            profile.street_address2 = form.cleaned_data['street_address2']

            # Save the profile
            profile.save()

            messages.success(request, "Congratulations! Profile saved successfully")
        else:
            messages.warning(request, 'Invalid input data')

        return render(request, 'profiles/profile.html', {'form': form})


def address(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'profiles/address.html', {'profile': profile})


class addressUpdate(View):
    def get(self,request,pk): 
        add=Profile.objects.get(pk=pk)
        form = ProfileForm(instance=add)
        return render(request,'profiles/address_update.html',locals())
    def post(self,request,pk):
        form = ProfileForm(request.POST)
        if form.is_valid():
            add = Profile.objects.get(pk=pk)
            add.first_name = form.cleaned_data['first_name']
            add.last_name = form.cleaned_data['last_name']
            add.street_address1 = form.cleaned_data['street_address1']
            add.street_address2 = form.cleaned_data['street_address2']
            add.town_or_city = form.cleaned_data['town_or_city']
            add.postcode = form.cleaned_data['postcode']
            add.country = form.cleaned_data['country']
            add.phone_number = form.cleaned_data['phone_number']
            add.save()
            messages.success(request,"Your Profile successfully Updated")
        else:
            messages.warning(request,"Invalid Input Data")

        return redirect("address")




@login_required  
def account_settings(request):
   
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'profiles/account_settings.html', context)

@login_required
def account_delete(request):
    # Check if the request method is POST
    if request.method == 'POST':
        user = request.user
        # Delete the user's account
        user.delete()
        # Log the user out
        logout(request)
        # Redirect to a page after successful account deletion
        return redirect('home')
    else:
        # Render a confirmation page for account deletion
        return render(request, 'profiles/account_delete.html')
