from django.db import models
from django.contrib.auth.models import User

class PendingRegistration(models.Model):
    registrationDateTime = models.DateTimeField(auto_now = True)
    user = models.ForeignKey(User)
    activationKey = models.CharField(max_length = 64)
