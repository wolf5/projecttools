from django.shortcuts import render
from helpers import RegisterForm
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from models import PendingRegistration
from hashlib import sha256
from datetime import datetime
from django.template.loader import render_to_string
from urllib import urlencode
from django.core.mail import send_mail
from datetime import timedelta
from django.conf import settings

def register(request):
    if request.method == "POST":
        registerForm = RegisterForm(request.POST)
        if registerForm.is_valid():
            
            # create the user...
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password1"]
            user = User.objects.create_user(username, email, password)
            user.first_name = request.POST["first_name"]
            user.last_name = request.POST["last_name"]
            user.is_staff = True
            user.is_active = False  # users are inactive until they use the activation link.
            user.save()
            
            # ...generate an activation key...
            activationKey = sha256(username + str(datetime.now())).hexdigest()
            
            # ...store the pending registration...
            pendingRegistration = PendingRegistration()
            pendingRegistration.user = user
            pendingRegistration.activationKey = activationKey
            pendingRegistration.save()
            
            # ...send an activation link via mail...
            activationurl = request.build_absolute_uri("/me/activate/") + activationKey
            mailBody = render_to_string("me/activationemail.txt", {"activationurl": activationurl})
            send_mail("Aktivierung", mailBody, "twuersch@gmail.com", [email], fail_silently = False)
            
            # ...and display a confirmation page.
            return HttpResponseRedirect("/me/activationSent/?" + urlencode({"email": email}))
        else:
            return render(request, "me/register.html", {"registerForm": registerForm})
    else:
        registerForm = RegisterForm()
        return render(request, "me/register.html", {"registerForm": registerForm})

def activationSent(request):
    email = request.GET["email"]
    return render(request, "me/activationSent.html", {"email": email})

def activate(request, activationKey):
    # remove all expired pending registrations.
    # note that this is not very optimized at the moment.
    for pendingRegistration in PendingRegistration.objects.all():
        if datetime.now() - pendingRegistration.registrationDateTime > timedelta(settings.ACCOUNT_ACTIVATION_TIME):
            pendingRegistration.delete()
    
    # retrieve the pending registration that corresponds with the activation key
    pendingRegistrations = PendingRegistration.objects.filter(activationKey = activationKey)
    if len(pendingRegistrations) == 1:
        pendingRegistration = pendingRegistrations[0]
        # check whether the activation key hasn't expired yet
        if datetime.now() - pendingRegistration.registrationDateTime <= timedelta(settings.ACCOUNT_ACTIVATION_TIME):
            #everything in order.
            user = pendingRegistration.user
            user.is_active = True
            user.save()
            
            # delete the pending registration since it's no longer in use.
            pendingRegistration.delete()
            return HttpResponseRedirect("/login/")
        else:
            return HttpResponseRedirect("/me/activationFailed/")
    else:
        return HttpResponseRedirect("/me/activationFailed/")
    
def activationFailed(request):
    return render(request, "me/activationFailed.html", {})
