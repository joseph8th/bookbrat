import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from accounts.models import UserProfile
from accounts.forms import UserProfileForm


#### Account views ####

@login_required
def myaccount(request):
    owner = request.user
    return render_to_response('accounts/myaccount.html',
                              context_instance=RequestContext(request))

@login_required
def editprofile(request):
    owner = request.user
    if request.method == 'POST':
        profileform = ProfileForm(request.POST)
        if profileform.is_valid():
            cd = profileform.cleaned_data
            profile = owner.profile.
