# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseNotFound
import helpers
from constants import COMMAND_PAUSE, COMMAND_RESUME, STATE_PAUSED, STATE_RUNNING
from models import Customer
from models import Entry
from django.template import Context, loader
from datetime import timedelta, datetime, date
from django.template.defaultfilters import date as djangoDate
from projecttools.timesheet.constants import COMMAND_PAUSE_AND_RESUME,\
    COMMAND_REPLAY
from projecttools.timesheet.templatetags.timesheettags import duration
from projecttools.timesheet.helpers import get_presence_start, get_presence_end,\
    get_days_total

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
            
            # replay command (re-use customer and comment of an already 
            # existing entry
            elif request.POST["command"] == COMMAND_REPLAY:
                if "entry" in request.POST:
                    entry_id = int(request.POST["entry"])
                    entry = Entry.objects.get(id = entry_id)
                    # a little bit of safety
                    if entry.owner == request.user:
                        helpers.resume(request.user, entry.customer, entry.comment)
    
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
    presence_start = get_presence_start(request.user)
    presence_end = get_presence_end(request.user)
    if presence_start and presence_end:
        presence_duration = presence_end - presence_start
    else:
        presence_duration = timedelta()
    presence_date = presence_start.replace(hour = 0, minute = 0, second = 0, microsecond = 0) if presence_start is not None else None

    # calculate working time
    days_total = get_days_total(request.user, presence_date) if presence_date else timedelta()
    
    # calculate time spent on breaks
    days_breaks = presence_duration - days_total if days_total else timedelta()
    
    # calculate daily totals    
    if len(entries) == 1:
        entry = entries[0]
        if entry.end:
            daily_total = entry.end - entry.start
        else:
            daily_total = datetime.now() - entry.start
        setattr(entry, "daily_total", daily_total)
    elif len(entries) > 1:
        previous_entry = None
        daily_total = timedelta()
        
        for index, entry in enumerate(entries):
            if previous_entry:
                if previous_entry.start.day != entry.start.day or previous_entry.start.month != entry.start.month or previous_entry.start.year != entry.start.year:
                    setattr(entries[index - 1], "daily_total", daily_total)
                    daily_total = timedelta()
            if entry.end:
                daily_total = daily_total + (entry.end - entry.start)
            else:
                daily_total = daily_total + (datetime.now() - entry.start)
            
            previous_entry = entry
        setattr(entries[len(entries) - 1], "daily_total", daily_total)
    
    return render(request, "timesheet/clock.html", {"state": state, 
                                                    "customers": customers, 
                                                    "currentCustomer": currentCustomer, 
                                                    "entries": entries, 
                                                    "topTaskEntry": topTaskEntry, 
                                                    "serverTime": datetime.now(), 
                                                    "user": request.user, 
                                                    "presence_date": presence_date, 
                                                    "presence_start": presence_start, 
                                                    "presence_end": presence_end, 
                                                    "presence_duration": presence_duration, 
                                                    "days_total": days_total, 
                                                    "days_breaks": days_breaks})

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
            currentYearAndMonth = datetime(year, month, 1)
        else:
            currentYearAndMonth = datetime(year, 1, 1)
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

@login_required
def monthly_report_csv(request, year, month):
    """
    Outputs a monthly report as CSV.
    """
    # initialization
    lines = []
    currentYearAndMonth = datetime(int(year), int(month), 1)
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

@login_required
def monthly_time_statistics_csv(request, year, month):
    year = int(year) if year else None
    month = int(month) if month else None
    if year and month:
        rows = []
        rows.append([u"#Datum", u"Präsenzzeit Start", u"Präsenzzeit Ende", u"Total Pause", u"Total Präsenzzeit"])
        current_date = date(year, month, 1)
        one_day = timedelta(days = 1)
        while current_date.month == month:
            
            presence_start = get_presence_start(request.user, current_date)
            presence_end = get_presence_end(request.user, current_date)
            if presence_start and presence_end:
                presence_duration = presence_end - presence_start
            else:
                presence_duration = timedelta()
            presence_date = presence_start.replace(hour = 0, minute = 0, second = 0, microsecond = 0) if presence_start is not None else None
            days_total = get_days_total(request.user, presence_date) if presence_date else timedelta()
            days_breaks = presence_duration - days_total if days_total else timedelta()
            
            current_date_as_string = djangoDate(current_date, "d.m.Y")
            presence_start_as_string = djangoDate(presence_start, "H:i") if presence_start else "00:00"
            presence_end_as_string = djangoDate(presence_end, "H:i") if presence_end else "00:00"
            days_total_as_string = duration(days_total, "%H:%m")
            days_breaks_as_string = duration(days_breaks, "%H:%m")
            
            rows.append([unicode(current_date_as_string), unicode(presence_start_as_string), unicode(presence_end_as_string), unicode(days_breaks_as_string), unicode(days_total_as_string)])
            
            # if we're looking at a sunday, insert two empty lines afterwards.
            if current_date.isoweekday() == 7:
                rows.append([])
                rows.append([])
            
            # go to the next day.
            current_date = current_date + one_day
        
        # Return CSV to the browser
        lines = [u",".join(row) for row in rows]
        response = HttpResponse(u"\n".join(lines), content_type = "text/csv")
        currentYearAndMonth = datetime(int(year), int(month), 1)
        csv_filename = "Arbeitszeitstatistik " + djangoDate(currentYearAndMonth, "F") + " " + djangoDate(currentYearAndMonth, "Y") + ".csv"
        response["Content-Disposition"] = helpers.createContentDispositionAttachmentString(csv_filename, request)
        return response
    else:
        return HttpResponseNotFound("Page not found.")