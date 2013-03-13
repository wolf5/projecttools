from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.core.exceptions import ValidationError

class Customer(models.Model):
    name = models.CharField(max_length = 255, unique = True)
    
    def __unicode__(self):
        return self.name

class Entry(models.Model):
    customer = models.ForeignKey(Customer)
    start = models.DateTimeField()
    end = models.DateTimeField(null = True, blank = True)
    comment = models.TextField(blank = True)
    owner = models.ForeignKey(User)

    def __unicode__(self):
        text = ""
        text += self.owner.username
        text += ": "
        text += self.customer.name
        
        if self.end:
            text += " von "
        else:
            text += " ab "
            
        text += self.start.strftime("%d.%m.%Y %H:%M:%S")
        
        if self.end:
            text += " bis " + self.end.strftime("%d.%m.%Y %H:%M:%S")
            
        if self.comment and self.comment != "":
            text += " (" + self.comment + ")"
        
        return text

    def duration(self):
        if self.end != None:
            return self.end - self.start
        else:
            return timedelta(0)

    def clean(self):
        if self.start != None and self.end != None:
            if self.start >= self.end:
                raise ValidationError("Startzeit muss vor Endzeit liegen.")