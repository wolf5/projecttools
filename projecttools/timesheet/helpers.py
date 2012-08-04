'''
Created on Mar 2, 2012

@author: timo
'''
from models import Entry
from models import Customer
from datetime import datetime
from datetime import timedelta
import urllib 

def resume(user, customer, comment = "", delay = 0):
    """
    Start/Resume the current task. Delay specifies how far back (in minutes) the task is started.
    """
        
    topTaskEntry = getCurrentTaskEntry(user)
    # check whether there already is a task running
    if not isAnyTaskRunning(user):
        
        # make sure tasks don't overlap
        if not topTaskEntry or (datetime.now() - timedelta(0, 0, 0, 0, delay) > topTaskEntry.end):
            start = datetime.now() - timedelta(0, 0, 0, 0, delay)
        else:
            start = topTaskEntry.end + timedelta(0, 1)
        
        # no task running, so let's create a new entry
        newTaskEntry = Entry(owner = user, customer = customer, start = start, comment = comment)
        newTaskEntry.save()
    else:
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
    Get the currently selected customer for the given user.
    """
    topTaskEntry = getCurrentTaskEntry(user)
    if topTaskEntry != None:
        return topTaskEntry.customer
    else:
        return None
    
def getDefaultCustomer():
    """
    Get the "default" customer for the given user. At the moment, this is the first customer that can be found.
    """
    return next(iter(Customer.objects.order_by("name")), None)

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

def get_presence_start(user, date = None):
    """
    Determines the presence start time (Earliest start on the most recent day or the given date)
    """
    if date:
        year, month, day = date.year, date.month, date.day
    else:
        top_task_entry = getCurrentTaskEntry(user)
        year, month, day = top_task_entry.start.year, top_task_entry.start.month, top_task_entry.start.day
    try:
        return Entry.objects.filter(owner = user, start__year = year, start__month = month, start__day = day).order_by("start")[0].start
    except IndexError, Entry.DoesNotExist:
        return None

def get_presence_end(user, date = None):
    """
    Determines the presence end time (Latest end on the most recent day or current time if no date is given, else last end on the given date)
    """
    if date:
        year, month, day = date.year, date.month, date.day
    else:
        presence_start = get_presence_start(user)
        presence_date = presence_start.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        year, month, day = presence_date.year, presence_date.month, presence_date.day
    try:
        return Entry.objects.filter(owner = user, end__year = year, end__month = month, end__day = day).order_by("-end")[0].end
    except IndexError, Entry.DoesNotExist:
        return None

def get_days_total(user, customer, date):
    """
    Retrieves the total of hours logged for the given user on the given date.
    """
    days_completed_entries = Entry.objects.filter(owner = user, customer = customer, start__year = date.year, start__month = date.month, start__day = date.day, end__isnull = False)
    days_total = timedelta()
    for entry in days_completed_entries:
        days_total = days_total + (entry.end - entry.start)
    return days_total
