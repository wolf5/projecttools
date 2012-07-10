# -*- coding: utf-8 -*-

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
from projecttools.timesheet.constants import COMMAND_PAUSE_AND_RESUME
from projecttools.timesheet.templatetags.timesheettags import duration

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
        # if we only change the comment
        if "comment" in request.POST and not "command" in request.POST:
            topTaskEntry = helpers.getCurrentTaskEntry(request.user)
            if topTaskEntry != None:
                topTaskEntry.comment = request.POST["comment"]
                topTaskEntry.save()
        
        # if we pause/resume a task
        if "command" in request.POST:
            # If there's a comment, read it from the request
            if "comment" in request.POST:
                comment = request.POST["comment"]
            else:
                comment = ""
            
            # pause command
            if request.POST["command"] == COMMAND_PAUSE:
                helpers.pause(request.user)
            
            # pause and immediately resume command
            elif request.POST["command"] == COMMAND_PAUSE_AND_RESUME:
                helpers.iTookABreak(request.user, int(request.POST["duration"]), comment)
            
            # resume command
            elif request.POST["command"] == COMMAND_RESUME:
                customer = Customer.objects.get(pk = request.POST["customer"])
                if "delay" in request.POST:
                    helpers.resume(request.user, customer, comment, int(request.POST["delay"]))
                else:
                    helpers.resume(request.user, customer, comment)
    
    if helpers.isAnyTaskRunning(request.user):
        state = STATE_RUNNING
    else:
        state = STATE_PAUSED
        
    customers = Customer.objects.all().order_by("name")
    entries = Entry.objects.filter(owner = request.user).order_by("-start")
    currentCustomer = helpers.getCurrentCustomer(request.user)
    if not currentCustomer:
        currentCustomer = helpers.getDefaultCustomer()
    topTaskEntry = helpers.getCurrentTaskEntry(request.user)
    
    # calculate presence time
    presence_start = Entry.objects.filter(owner = request.user, start__year = topTaskEntry.start.year, start__month = topTaskEntry.start.month, start__day = topTaskEntry.start.day).order_by("start")[0].start
    presence_date = presence_start.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    try:
        presence_end = Entry.objects.filter(owner = request.user, end__year = presence_date.year, end__month = presence_date.month, end__day = presence_date.day).order_by("-end")[0].end
    except Exception:
        presence_end = datetime.datetime.now()
    presence_duration = presence_end - presence_start
    
    # 0ffwork sum for present day
    offwork_customer = Customer.objects.get(name__exact = "0ffwork")
    if offwork_customer is not None:
        todays_offwork_entries = Entry.objects.filter(owner = request.user, customer = offwork_customer, start__year = presence_date.year, start__month = presence_date.month, start__day = presence_date.day, end__isnull = False)
        todays_offwork_duration = timedelta()
        for todays_offwork_entry in todays_offwork_entries:
            todays_offwork_duration = todays_offwork_duration + (todays_offwork_entry.end - todays_offwork_entry.start)
    
    # 1ntern sum for present day
    intern_customer = Customer.objects.get(name__exact = "1ntern")
    if intern_customer is not None:
        todays_intern_entries = Entry.objects.filter(owner = request.user, customer = intern_customer, start__year = presence_date.year, start__month = presence_date.month, start__day = presence_date.day, end__isnull = False)
        todays_intern_duration = timedelta()
        for todays_intern_entry in todays_intern_entries:
            todays_intern_duration = todays_intern_duration + (todays_intern_entry.end - todays_intern_entry.start)
    
    # really worked
    real_work_duration = presence_duration - todays_offwork_duration
    
    # billable time
    billable_time = real_work_duration - todays_intern_duration
    
    return render(request, "timesheet/clock.html", {"state": state, "customers": customers, "currentCustomer": currentCustomer, "entries": entries, "topTaskEntry": topTaskEntry, "serverTime": datetime.datetime.now(), "user": request.user, "presence_date": presence_date, "presence_start": presence_start, "presence_end": presence_end, "presence_duration": presence_duration, "todays_offwork_duration": todays_offwork_duration, "real_work_duration": real_work_duration, "todays_intern_duration": todays_intern_duration, "billable_time": billable_time})

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
        return render(request, "timesheet/customer_report.html", {"currentCustomer": currentCustomer, "entries": entries, "customers": customers, "totalDuration": totalDuration, "availableYearsAndMonths": availableYearsAndMonths, "year": year, "month": month, "currentYearAndMonth": currentYearAndMonth, "availableYears": availableYears, "user": request.user});

def monthly_report_csv(request, year, month):
    """
    Outputs a monthly report as CSV.
    """
    # initialization
    lines = []
    currentYearAndMonth = datetime.datetime(int(year), int(month), 1)
    lines.append(u"Monatsreport für alle Kunden für " + djangoDate(currentYearAndMonth, "F") + " " + djangoDate(currentYearAndMonth, "Y"))
    
    # retrieve all entries for the given month and year and pre-sort them.
    entries = Entry.objects.filter(end__isnull = False, start__year = year, start__month = month).order_by("customer", "owner", "start")
    
    # keeps track of customer and owner while iterating. used to generate section titles.
    previousCustomer = None
    previousOwner = None
    
    # iterate over entries.
    for entry in entries:
        # customer header, if necessary
        if entry.customer != previousCustomer:
            lines.append(unicode(entry.customer))
            previousCustomer = entry.customer
            previousOwner = None
        # owner header, if necessary
        if entry.owner != previousOwner:
            if entry.owner.first_name is not None or entry.owner.last_name is not None:
                lines.append("Mitarbeiter: " + u" ".join([u"" if entry.owner.first_name is None else entry.owner.first_name, u"" if entry.owner.last_name is None else entry.owner.last_name]))
            else:
                lines.append("Mitarbeiter: " + unicode(entry.owner))
            previousOwner = entry.owner
        
        lines.append(u",".join([djangoDate(entry.start, "d.m.Y"), 
                                djangoDate(entry.start, "H:i"),
                                djangoDate(entry.end, "d.m.Y"),
                                djangoDate(entry.end, "H:i"),
                                duration(entry.duration(), "%H:%m"),
                                duration(entry.duration(), "%O"),
                                entry.comment
                                ]))
    response = HttpResponse(u"\n".join(lines), content_type = "text/csv")
    csvFilename = "Timesheet Report " + djangoDate(currentYearAndMonth, "F") + " " + djangoDate(currentYearAndMonth, "Y") + ".csv"
    response["Content-Disposition"] = helpers.createContentDispositionAttachmentString(csvFilename, request)
    return response

def main_css(request):
    return render(request, "timesheet/main.css", content_type = "text/css")
