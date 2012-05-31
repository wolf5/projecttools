# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail, mail_admins
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from forms import RegisterForm, SubscriptionForm
from hashlib import sha256
from helpers import sendActivationEmail, isSubscriptionValid
from models import PendingActivation, Subscription
from smtplib import SMTPException
from urllib import urlencode

def register(request):
    """
    Shows a registration form.
    """
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
            pendingActivation = PendingActivation()
            pendingActivation.user = user
            pendingActivation.activationKey = activationKey
            pendingActivation.save()
            
            # ...send an activation link via mail...
            sendActivationEmail(request, email, activationKey)
            
            # ...and display a confirmation page.
            return HttpResponseRedirect("/me/activationSent/?" + urlencode({"email": email}))
        else:
            return render(request, "me/register.html", {"registerForm": registerForm})
    else:
        registerForm = RegisterForm()
        return render(request, "me/register.html", {"registerForm": registerForm})

def activationSent(request):
    """
    Confirms that an activation e-mail has been sent.
    """
    email = request.GET["email"]
    return render(request, "me/activationSent.html", {"email": email})

def activate(request, activationKey):
    """
    Used to activate a registration, given an activation key.
    """
    # remove all expired pending activations.
    # note that this is not very optimized at the moment.
    for pendingActivation in PendingActivation.objects.all():
        if datetime.now() - pendingActivation.registrationDateTime > timedelta(settings.ACCOUNT_ACTIVATION_TIME):
            pendingActivation.delete()
    
    # retrieve the pending activation that corresponds with the activation key
    pendingActivations = PendingActivation.objects.filter(activationKey = activationKey)
    if len(pendingActivations) == 1:
        pendingActivation = pendingActivations[0]
        # check whether the activation key hasn't expired yet
        if datetime.now() - pendingActivation.registrationDateTime <= timedelta(settings.ACCOUNT_ACTIVATION_TIME):
            # everything in order, so activate the user.
            user = pendingActivation.user
            user.is_active = True
            user.save()
            
            # start a timesheet trial period of 40 days.
            subscription = Subscription()
            subscription.user = user
            subscription.trial = True
            subscription.expiry = datetime.now() + timedelta(40)
            subscription.save()
            
            # delete the pending activation since it's no longer in use.
            pendingActivation.delete()
            return HttpResponseRedirect("/login/")
        else:
            return HttpResponseRedirect("/me/activationFailed/")
    else:
        return HttpResponseRedirect("/me/activationFailed/")

def activationFailed(request):
    """
    Display this if the activation failed.
    """
    return render(request, "me/activationFailed.html", {})

def login(request):
    """
    Login view. This replaces the earlier use of django.contrib.auth.views.login
    because we have to check for subscription validity etc.
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username = username, password = password)
        if user is not None:
            if user.is_active:
                django_login(request, user)
                if isSubscriptionValid(user):
                    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
                else:
                    return HttpResponseRedirect("/me/subscribe/")
            else:
                authenticationForm = AuthenticationForm()
                authenticationForm.fields.username.error_messages = {"invalid": "Dieser Benutzer muss zuerst aktiviert werden."}
                return render(request, "me/login.html", {"authenticationForm": authenticationForm})
        else:
            authenticationForm = AuthenticationForm()
            authenticationForm.fields.username.error_messages = {"invalid": "Benutzername und/oder Passwort falsch."}
            return render(request, "me/login.html", {"authenticationForm": authenticationForm})
    elif request.method == "GET":
        authenticationForm = AuthenticationForm()
        return render(request, "me/login.html", {"authenticationForm": authenticationForm})

@login_required
def subscribe(request):
    """
    The subscription view. This view handles subscription renewals, trial cancellations etc.
    """
    # check whether we're in a trial period or regular subscription.
    subscriptionRecord = Subscription.objects.get(user = request.user)
    trial = subscriptionRecord.trial and isSubscriptionValid(request.user)
    trialexpired = subscriptionRecord.trial and not isSubscriptionValid(request.user)
    subscription = not subscriptionRecord.trial and isSubscriptionValid(request.user)
    subscriptionexpired = not subscriptionRecord.trial and not isSubscriptionValid(request.user)
    expiry = subscriptionRecord.expiry
    expirydelta = expiry - datetime.now()
    
    if request.method == "POST":
        subscriptionForm = SubscriptionForm(request.POST)
        if subscriptionForm.is_valid():
            
            # prepare the contents...
            if subscriptionForm.cleaned_data["recurrence"] == "monthly":
                period = str(subscriptionForm.cleaned_data["numberMonths"]) + " Monate"
                amount = "{0:.2f}".format(subscriptionForm.cleaned_data["numberMonths"] * 4.95)   
            elif subscriptionForm.cleaned_data["recurrence"] == "yearly":
                period = str(subscriptionForm.cleaned_data["numberYears"]) + " Jahre"
                amount = "{0:.2f}".format(subscriptionForm.cleaned_data["numberYears"] * 54.45)
             
            if subscriptionForm.cleaned_data["payment"] == "transfer":
                mailBody = render_to_string("me/paymentTransferEmail.txt", {"amount": amount, "period": period})
                subject = u"Aboverlängerung: Zahlungsinformationen"
            elif subscriptionForm.cleaned_data["payment"] == "invoice":
                billingAddress = subscriptionForm.cleaned_data["first_name"] + " " + subscriptionForm.cleaned_data["last_name"] + "\n" + subscriptionForm.cleaned_data["billingAddress"]
                mailBody = render_to_string("me/paymentInvoiceEmail.txt", {"amount": amount, "period": period, "billingAddress": billingAddress})
                subject = u"Aboverlängerung: Zahlungsinformationen"
                
            # ...and then send the mails.
            try:
                send_mail(subject, mailBody, "twuersch@gmail.com", [subscriptionForm.cleaned_data["email"]])
                mail_admins(subject, mailBody)
                return HttpResponseRedirect(reverse("me_mail_success"))
            except SMTPException:
                return HttpResponseRedirect(reverse("me_mail_failed"))
                
        else:
            render(request, "me/subscribe.html", {"trial": trial, "trialexpired": trialexpired, "subscription": subscription, "subscriptionexpired": subscriptionexpired, "subscriptionForm": subscriptionForm, "trialexpiry": expiry, "subscriptionexpiry": expiry, "expirydelta": expirydelta })
    else:
        subscriptionForm = SubscriptionForm(initial = {"email": request.user.email, "first_name": request.user.first_name, "last_name": request.user.last_name, "payment": "transfer", "recurrence": "yearly", "numberYears": 1, "numberMonths": 12, "billingAddress": request.user.get_profile().billingAddress })
    
    return render(request, "me/subscribe.html", {"trial": trial, "trialexpired": trialexpired, "subscription": subscription, "subscriptionexpired": subscriptionexpired, "subscriptionForm": subscriptionForm, "trialexpiry": expiry, "subscriptionexpiry": expiry, "expirydelta": expirydelta })

def mail_failed(request):
    return render(request, "me/mail_failed.html")

def mail_success(request):
    return render(request, "me/mail_success.html")

@login_required
def index(request):
    return HttpResponseRedirect(reverse("clock"))
