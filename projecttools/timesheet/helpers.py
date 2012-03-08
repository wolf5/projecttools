'''
Created on Mar 2, 2012

@author: timo
'''
from models import Entry
from datetime import datetime

def resume(user, customer):
    """
    Start/Resume the current task
    """
    # first step: check whether there already is a task running
    if not isAnyTaskRunning(user):
        # no task running, so let's create a new entry
        newTaskEntry = Entry(owner = user, customer = customer, start = datetime.now())
        newTaskEntry.save()
    else:
        # there is a task running, so check whether it is for the same customer
        topTaskEntry = getNewestTaskEntry(user)
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
    """
    Stop/Pause the current task
    """
    if isAnyTaskRunning(user):
        topTaskEntry = getNewestTaskEntry(user)
        topTaskEntry.end = datetime.now()
        topTaskEntry.save()
    else:
        pass

def isAnyTaskRunning(user):
    """
    Returns True if there is a task running for the given user.
    """
    return Entry.objects.filter(owner = user, end__isnull = True).exists()

def getCurrentCustomer(user):
    """
    Get the currently selected customer for the given user.
    """
    topTaskEntry = getNewestTaskEntry(user)
    if topTaskEntry != None:
        return topTaskEntry.customer
    else:
        return None

def getNewestTaskEntry(user):
    """
    Retrieve the most recent task entry for the given user.
    """
    return next(iter(Entry.objects.filter(owner = user).order_by("-start")), None)

def getAvailableReports(user):
    """
    Retrieve the years-and-monts combinations for which the given user
    has reports available.
    """
