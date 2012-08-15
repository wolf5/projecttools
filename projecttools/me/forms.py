# -*- coding: utf-8 -*-
"""
Contains forms for the user-facing registration/activation/subscription parts.

Created on Apr 26, 2012

@author: timo
"""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    """
    Provides a user registration form.
    """
    first_name = forms.CharField(max_length = 30, label = "Vorname")
    last_name = forms.CharField(max_length = 30, label = "Nachname")
    email = forms.EmailField(label = "E-Mail")
    
    class Meta(UserCreationForm.Meta):
        fields = ["first_name", "last_name", "email", "username", "password1", "password2"]
        model = User

class SubscriptionForm(forms.Form):
    """
    Provides the subscription essentials form, containing the recurrence choice etc.
    """
    numberYears = forms.IntegerField(min_value = 1, max_value = 10)
    numberYears.widget.attrs = {"size": 4}
    numberMonths = forms.IntegerField(min_value = 1, max_value = 120)
    numberMonths.widget.attrs = {"size": 4}
    recurrenceChoices = [("yearly", "Jährlich, 1 Monat pro Jahr gratis, CHF 54.45 pro Jahr"), 
                         ("monthly", "Monatlich, CHF 4.95 pro Monat")]
    recurrence = forms.ChoiceField(choices = recurrenceChoices, widget = forms.RadioSelect())
    paymentChoices = [("transfer", u"Überweisung"),
                      ("invoice", u"Einzahlungsschein")]
    payment = forms.ChoiceField(choices = paymentChoices, widget = forms.RadioSelect())
    email = forms.EmailField()
    first_name = forms.CharField(max_length = 30, label = "Vorname")
    last_name = forms.CharField(max_length = 30, label = "Nachname")
    billingAddress = forms.CharField(widget = forms.Textarea)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        # check the recurrence part of the form
        if cleaned_data["recurrence"] == u"yearly":
            if "numberMonths" in self._errors: del self._errors["numberMonths"]
        elif cleaned_data["recurrence"] == u"monthly":
            if "numberYears" in self._errors: del self._errors["numberYears"]
            
        # check the payment part of the form
        if cleaned_data["payment"] == u"transfer":
            if "first_name" in self._errors: del self._errors["first_name"]
            if "last_name" in self._errors: del self._errors["last_name"]
            if "billingAddress" in self._errors: del self._errors["billingAddress"]
        if cleaned_data["payment"] == u"invoice":
            if "email" in self._errors: del self._errors["email"]
        return cleaned_data
    
class AuthenticationForm(forms.Form):
    username = forms.CharField(label = "Benutzername", max_length = 30)
    password = forms.CharField(label = "Passwort", widget = forms.PasswordInput)
    
    def clean(self):
        user = authenticate(username = self.cleaned_data.get("username"), password = self.cleaned_data.get("password"))
        if user is None or (user is not None and not user.is_active):
            raise forms.ValidationError("Unbekannter")
        # TODO: twuersch: continue here.