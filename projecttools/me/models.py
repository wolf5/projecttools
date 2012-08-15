from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import TextField
from django.db.models.fields.related import OneToOneField
from django.db.models.signals import post_save

class PendingActivation(models.Model):
    registrationDateTime = models.DateTimeField(auto_now = True)
    user = models.ForeignKey(User)
    activationKey = models.CharField(max_length = 64)

class Subscription(models.Model):
    user = OneToOneField(User)
    expiry = models.DateTimeField()
    trial = models.BooleanField(default = False)

class AdditionalProfileInformation(models.Model):
    user = OneToOneField(User)
    billingAddress = TextField(blank = True)

def createAdditionalProfileInformation(sender, instance, created, **kwargs):
    if created:
        AdditionalProfileInformation.objects.create(user = instance)
# Note that the dispatch_uid seems to be necessary to prevent the 
# receiver from being called twice and generating an IntegrityError.
# post_save.connect(createAdditionalProfileInformation, sender = User, dispatch_uid = "createAdditionalProfileInformation")

