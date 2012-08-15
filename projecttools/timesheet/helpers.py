"""
Contains logic and additional database abstraction.

Created on Mar 2, 2012

@author: timo
"""
from models import Customer, Entry
from datetime import datetime
from datetime import timedelta
import urllib 

def resume(user, customer, comment = "", delay = 0):
    """
    Start/Resume the current task. Delay specifies how far back (in minutes) the task is started.
    """
        
    # check whether there already is a task running
    if not isAnyTaskRunning(user):
        topTaskEntry = getCurrentTaskEntry(user)
        if topTaskEntry is not None:
            # if there's a previous task, make sure that they don't overlap
            if datetime.now() - timedelta(0, 0, 0, 0, delay) > topTaskEntry.end:
                start = datetime.now() - timedelta(0, 0, 0, 0, delay)
            else:
                start = topTaskEntry.end + timedelta(0, 1)
        else:
            # no previous task, so there can't be any overlapping
            start = datetime.now()
        
        # no task running, so let's just create a new entry
        newTaskEntry = Entry(owner = user, customer = customer, start = start, comment = comment)
        newTaskEntry.save()
    else:
        topTaskEntry = getCurrentTaskEntry(user)
        # there is a task running, so check whether it is for the same customer
        if topTaskEntry.customer != customer:
            # not for the same customer, so finish the current task and start a new one
            topTaskEntry.end = datetime.now()
            topTaskEntry.save()
            if datetime.now() - timedelta(0, 0, 0, 0, delay) > topTaskEntry.end:
                start = datetime.now() - timedelta(0, 0, 0, 0, delay)
            else:
                start = topTaskEntry.end + timedelta(0, 1)
            newTaskEntry = Entry(owner = user, customer = customer, start = start, comment = comment)
            newTaskEntry.save()
        else:
            # for the same customer, so this is a duplicate request. do nothing.
            pass
    
def pause(user):
    """
    Stop/Pause the current task
    """
    # TODO: If the end is not on the same day as the start, create split entries accordingly.
    if isAnyTaskRunning(user):
        topTaskEntry = getCurrentTaskEntry(user)
        topTaskEntry.end = datetime.now()
        topTaskEntry.save()
    else:
        pass
    
def iTookABreak(user, duration, comment):
    """
    Insert a break retroactively with the given duration, i.e. pause the given duration before
    and then immediately resume the task.
    """
    if isAnyTaskRunning(user):
        topTaskEntry = getCurrentTaskEntry(user)
        # make sure that we don't get any overlapping entries.
        durationAsTimedelta = timedelta(0, 0, 0, 0, duration)
        if datetime.now() - topTaskEntry.start > durationAsTimedelta:
            topTaskEntry.end = datetime.now() - durationAsTimedelta
            topTaskEntry.comment = comment
            topTaskEntry.save()
        else:
            topTaskEntry.delete() 
        newTaskEntry = Entry(owner = user, customer = getCurrentCustomer(user), start = datetime.now(), comment = comment)
        newTaskEntry.save()
    else:
        pass

def isAnyTaskRunning(user):
    """
    Returns True if there is a task running for the given user.
    """
    return getRunningTask(user) != None

def getCurrentCustomer(user):
    """
    Get the currently selected customer for the given user, which always is either the
    last customer the user's been working on, or the first customer in the customer
    list if there aren't any task entries yet, or None if there aren't any customers yet.
    """
    topTaskEntry = getCurrentTaskEntry(user)
    if topTaskEntry != None:
        return topTaskEntry.customer
    else:
        try:
            return Customer.objects.order_by("name")[0]
        except IndexError:
            return None

def getRunningTask(user):
    """
    Returns the currently running task for the given user, if any.
    """
    runningTaskQuerySet = Entry.objects.filter(owner = user, end__isnull = True)
    if len(runningTaskQuerySet) == 1:
        return runningTaskQuerySet[0]
    else:
        return None

def getMostRecentTask(user):
    """
    Returns the most recent task, running or not.
    """
    return next(iter(Entry.objects.filter(owner = user).order_by("-start")), None)

def getCurrentTaskEntry(user):
    """
    Returns either tue currently running task for the given user, or the most recent task.
    """
    # If there's a running task, return it
    runningTask = getRunningTask(user)
    if runningTask:
        return runningTask
    else:
        return getMostRecentTask(user)

def getAvailableReports(user):
    """
    Retrieve the years-and-months combinations for which the given user
    has reports available.
    """

def createContentDispositionAttachmentString(filename, request):
    """
    Creates the "Content-Disposition: attachment..." etc. string for use
    in an HTTP header and tries to get the encoding right, depending on
    the browser (not entirely possible for all cases, though.)
    
    See http://greenbytes.de/tech/tc2231/#attwithfnrawpctenclong and
    http://greenbytes.de/tech/tc2231/#attwithfn2231utf8 for documentation.
    """
    if (request.META["HTTP_USER_AGENT"].find("Safari") != -1 and request.META["HTTP_USER_AGENT"].find("Chrome") == -1):
        # Safari
        return "attachment; filename=\"" + filename.encode("utf-8") + "\""
    else:
        # Everyone else
        return "attachment; filename*=UTF-8''" + urllib.quote(filename.encode("utf-8"))
