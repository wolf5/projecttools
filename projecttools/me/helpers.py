"""
Contains logic, additional classes, and additional database abstraction.

Created on Apr 22, 2012

@author: timo
"""

from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField
from django.forms import CharField
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    first_name = CharField(max_length = 30, label = "Vorname")
    last_name = CharField(max_length = 30, label = "Nachname")
    email = EmailField(label = "E-Mail")
    
    class Meta(UserCreationForm.Meta):
        fields = ["first_name", "last_name", "email", "username", "password1", "password2"]
        model = User
