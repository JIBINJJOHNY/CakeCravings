from django.shortcuts import render, redirect

from django.contrib import messages
from django.views import View
from .forms import ProfileForm
from .models import  Profile
# Create your views here.
class Profileview(View):
    def get(self,request):
        form = ProfileForm()
        return render(request,'profiles/profile.html',locals())
    def post(self,request):
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
            
            prfl = Profile(user=user,first_name=first_name,last_name=last_name,birthday=birthday,phone_number=phone_number,country=country,postcode=postcode,town_or_city=town_or_city,street_address1=street_address1,street_address2=street_address2,county=county)
            prfl.save()
            messages.success(request,"Congratulations! Profile save successfully")
        else:
            messages.warning(request,'Invalid input Data')

        return render(request,'profiles/profile.html',locals())

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

        return redirect("profiles:address")

    
