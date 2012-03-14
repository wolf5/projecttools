'''
Created on Mar 2, 2012

@author: timo
'''
from models import Entry
from datetime import datetime
from datetime import timedelta
import urllib 

def resume(user, customer, delay = 0):
    """
    Start/Resume the current task. Delay specifies how far back (in minutes) the task is started.
    """
    # first step: check whether there already is a task running
    if not isAnyTaskRunning(user):
        # no task running, so let's create a new entry
        start = datetime.now() - timedelta(0, 0, 0, 0, delay)
        newTaskEntry = Entry(owner = user, customer = customer, start = start)
        newTaskEntry.save()
    else:
        # there is a task running, so check whether it is for the same customer
        topTaskEntry = getCurrentTaskEntry(user)
        if topTaskEntry.customer != customer:
            # not for the same customer, so finish the current task and start a new one
            topTaskEntry.end = datetime.now()
            topTaskEntry.save()
            start = datetime.now() - timedelta(0, 0, 0, 0, delay)
            newTaskEntry = Entry(owner = user, customer = customer, start = start)
            newTaskEntry.save()
        else:
            # for the same customer, so this is a duplicate request. do nothing.
            pass
    
def pause(user):
    """
    Stop/Pause the current task
    """
    if isAnyTaskRunning(user):
        topTaskEntry = getCurrentTaskEntry(user)
        # TODO: If the end is not on the same day as the start, create split entries accordingly.
        topTaskEntry.end = datetime.now()
        topTaskEntry.save()
    else:
        pass

def isAnyTaskRunning(user):
    """
    Returns True if there is a task running for the given user.
    """
    return getRunningTask(user) != None

def getCurrentCustomer(user):
    """
    Get the currently selected customer for the given user.
    """
    topTaskEntry = getCurrentTaskEntry(user)
    if topTaskEntry != None:
        return topTaskEntry.customer
    else:
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
