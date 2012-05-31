"""
Contains additional logic and database abstraction.

Created on Apr 22, 2012

@author: timo
"""
from datetime import datetime
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from models import Subscription

def sendActivationEmail(request, email, activationKey):
    """
    Sends an e-mail containing an activation key.
    """
    activationUrl = request.build_absolute_uri("/me/activate/") + activationKey
    mailBody = render_to_string("me/activationemail.txt", {"activationUrl": activationUrl})
    send_mail("Aktivierung", mailBody, "twuersch@gmail.com", [email])

def isSubscriptionValid(user):
    """
    Checks whether a subscription is valid, i.e. it has not expired yet.
    """
    try:
        subscription = Subscription.objects.get(user = user)
        if subscription.expiry is not None:
            return subscription.expiry >= datetime.now()
        else:
            return False
    except Subscription.DoesNotExist:
        return False

def subscription_required(view_function):
    """
    View decorator. If applied, the view will only be shown if the current user has a
    valid subscription. If not, he will be redirected to the subscription page.
    """
    def _subscription_required(request, *args, **kwargs):
        if isSubscriptionValid(request.user):
            return view_function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse("subscribe"))
    return _subscription_required
