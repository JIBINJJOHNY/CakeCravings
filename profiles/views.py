from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .forms import ProfileForm
from .models import  Profile
from django.shortcuts import get_object_or_404

class Profileview(View):
    def get(self, request):
        form = ProfileForm()
        return render(request, 'profiles/profile.html', locals())

    def post(self, request):
        form = ProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            birthday = form.cleaned_data['birthday']
            phone_number = form.cleaned_data['phone_number']
            country = form.cleaned_data['country']
            postcode = form.cleaned_data['postcode']
            town_or_city = form.cleaned_data['town_or_city']
            street_address1 = form.cleaned_data['street_address1']
            street_address2 = form.cleaned_data['street_address2']
            county = form.cleaned_data['county']

       
            profile = get_object_or_404(Profile, user= request.user)

            # Update existing profile or create a new one
            profile.first_name = first_name
            profile.last_name = last_name
            profile.birthday = birthday
            profile.phone_number = phone_number
            profile.country = country
            profile.postcode = postcode
            profile.town_or_city = town_or_city
            profile.street_address1 = street_address1
            profile.street_address2 = street_address2
            profile.county = county

            profile.save()

            messages.success(request, "Congratulations! Profile saved successfully")
        else:
            messages.warning(request, 'Invalid input data')

        return render(request, 'profiles/profile.html', locals())


def address(request):
        add = Profile.objects.filter(user=request.user)
        return render(request,'profiles/address.html',locals())


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
