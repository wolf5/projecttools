from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import helpers
from constants import COMMAND_PAUSE, COMMAND_RESUME, STATE_PAUSED, STATE_RUNNING
from models import Customer
from models import Entry
from django.template import Context, loader
from datetime import timedelta
import datetime
from django.template.defaultfilters import date as djangoDate

def resumeFormFields():
    return '<input type="hidden" name="command" value="resume" /><input type="submit" value="Start" />'

def pauseFormFields():
    return '<input type="hidden" name="command" value="pause" /><input type="submit" value="Pause" />'

# Clock view.
# This view requires the user to be logged in.
@login_required
def clock(request):

    # POST request
    if request.method == "POST":
        if "command" in request.POST:
            # pause command
            if request.POST["command"] == COMMAND_PAUSE:
                helpers.pause(request.user)
                
            # resume command
            elif request.POST["command"] == COMMAND_RESUME:
                customer = Customer.objects.get(pk = request.POST["customer"])
                helpers.resume(request.user, customer)
            
        # set comment
        if "comment" in request.POST:
            topTaskEntry = helpers.getNewestTaskEntry(request.user)
            if topTaskEntry != None:
                topTaskEntry.comment = request.POST["comment"]
                topTaskEntry.save()
    
    if helpers.isAnyTaskRunning(request.user):
        state = STATE_RUNNING
    else:
        state = STATE_PAUSED
        
    customers = Customer.objects.all().order_by("name")
    entries = Entry.objects.filter(owner = request.user).order_by("-start")
    currentCustomer = helpers.getCurrentCustomer(request.user)
    topTaskEntry = helpers.getNewestTaskEntry(request.user)
    return render(request, "timesheet/clock.html", {"state": state, "customers": customers, "currentCustomer": currentCustomer, "entries": entries, "topTaskEntry": topTaskEntry, "serverTime": datetime.datetime.now()})

# Customer report view.
# This view requires the user to be logged in.
@login_required
def customer_report(request, customer_id, format_identifier, year, month):
    
    # coerce type
    if year:
        year = int(year)
    if month:
        month = int(month)
    
    # Read everything we need from the DB
    currentCustomer = Customer.objects.get(pk = customer_id)
    
    if year:
        if month:
            entries = Entry.objects.filter(owner = request.user, customer = currentCustomer, end__isnull = False, start__year = year, start__month = month).order_by("start")
        else:
            entries = Entry.objects.filter(owner = request.user, customer = currentCustomer, end__isnull = False, start__year = year).order_by("start")
    else:
        entries = Entry.objects.filter(owner = request.user, customer = currentCustomer, end__isnull = False).order_by("start")
    customers = Customer.objects.all().order_by("name")
    
    # Iterate once over the entries to get the total hours. This might sound inefficient,
    # but we assume there are not too many total entries per customer and owner anyways.
    totalDuration = timedelta()
    for entry in entries:
        duration = entry.end - entry.start
        totalDuration = totalDuration + duration
    
    # Collect the months and years for the available reports...
    availableYearsAndMonths = Entry.objects.filter(owner = request.user, customer = currentCustomer, end__isnull = False).dates("start", "month", order="DESC")
    availableYears = Entry.objects.filter(owner = request.user, customer = currentCustomer, end__isnull = False).dates("start", "year", order="DESC")
    
    # ...and set up a few objects for display.
    if year:
        if month:
            currentYearAndMonth = datetime.datetime(year, month, 1) 
        else:
            currentYearAndMonth = datetime.datetime(year, 1, 1)
    else:
        currentYearAndMonth = None
    
    if year:
        if month:
            csvFilename = "Timesheet Report " + currentCustomer.name + " " + djangoDate(currentYearAndMonth, "F") + " " + djangoDate(currentYearAndMonth, "Y") + ".csv"
        else:
            csvFilename = "Timesheet Report " + currentCustomer.name + " " + djangoDate(currentYearAndMonth, "Y") + ".csv"
    else:
        csvFilename = "Timesheet Report " + currentCustomer.name + ".csv"
    
    # Output CSV if so desired
    if format_identifier == "csv":
        template = loader.get_template("timesheet/customer_report.csv")
        context = Context({"currentCustomer": currentCustomer, "entries": entries, "customers": customers, "format_identifier": format_identifier})
        response = HttpResponse(template.render(context), content_type = "text/csv");
        response["Content-Disposition"] = helpers.createContentDispositionAttachmentString(csvFilename, request)
        return response

    # Output report as HTML
    else:
        # Most recent at the top
        entries = entries.reverse()
        return render(request, "timesheet/customer_report.html", {"currentCustomer": currentCustomer, "entries": entries, "customers": customers, "totalDuration": totalDuration, "availableYearsAndMonths": availableYearsAndMonths, "year": year, "month": month, "currentYearAndMonth": currentYearAndMonth, "availableYears": availableYears});
