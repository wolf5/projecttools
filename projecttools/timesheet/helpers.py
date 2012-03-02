'''
Created on Mar 2, 2012

@author: timo
'''
from models import Entry
from datetime import datetime

def resume(user, customer):
    # first step: check whether there already is a task running
    if not isAnyTaskRunning(user):
        # no task running, so let's create a new entry
        newTaskEntry = Entry(owner = user, customer = customer, start = datetime.now())
        newTaskEntry.save()
    else:
        # there is a task running, so check whether it is for the same customer
        topTaskEntry = getTopTaskEntry(user)
        if topTaskEntry.customer != customer:
            # not for the same customer, so finish the current task and start a new one
            topTaskEntry.end = datetime.now()
            topTaskEntry.save()
            newTaskEntry = Entry(owner = user, customer = customer, start = datetime.now())
            newTaskEntry.save()
        else:
            # for the same customer, so this is a duplicate request. do nothing.
            pass
    
def pause(user):
    if isAnyTaskRunning(user):
        topTaskEntry = getTopTaskEntry(user)
        topTaskEntry.end = datetime.now()
        topTaskEntry.save()
    else:
        pass

def isAnyTaskRunning(user):
    return Entry.objects.filter(owner = user, end__isnull = True).exists()

def getCurrentCustomer(user):
    topTaskEntry = getTopTaskEntry(user)
    if topTaskEntry != None:
        return topTaskEntry.customer
    else:
        return None

def getTopTaskEntry(user):
    return next(iter(Entry.objects.filter(owner = user).order_by("-start")), None)
