from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import helpers
from constants import COMMAND_PAUSE, COMMAND_RESUME, STATE_PAUSED, STATE_RUNNING
from models import Customer
from models import Entry
from django.template import RequestContext, Context, loader
from datetime import timedelta

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
            topTaskEntry = helpers.getTopTaskEntry(request.user)
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
    topTaskEntry = helpers.getTopTaskEntry(request.user)
    return render_to_response("timesheet/clock.html", {"state": state, "customers": customers, "currentCustomer": currentCustomer, "entries": entries, "topTaskEntry": topTaskEntry}, RequestContext(request))

def customer_report(request, customer_id, format_identifier):
    currentCustomer = Customer.objects.get(pk = customer_id)
    customers = Customer.objects.all().order_by("name");
    
    # Output CSV if so desired
    if format_identifier == "csv":
        entries = Entry.objects.filter(owner = request.user, customer = currentCustomer, end__isnull = False)
        template = loader.get_template("timesheet/customer_report.csv")
        context = Context({"currentCustomer": currentCustomer, "entries": entries, "customers": customers, "format_identifier": format_identifier})
        response = HttpResponse(template.render(context), content_type = "text/csv");
        response["Content-Disposition"] = "inline; filename=\"Report-" + currentCustomer.name + ".csv\""
        return response
    
    # Output report as HTML
    else:
        entries = Entry.objects.filter(owner = request.user, customer = currentCustomer, end__isnull = False).order_by("-start")
        
        # Iterate once over the entries to get the total hours. This might sound inefficient, but we assume there are not too many total entries anyways.
        totalDuration = timedelta()
        for entry in entries:
            duration = entry.end - entry.start
            totalDuration = totalDuration + duration
        return render_to_response("timesheet/customer_report.html", {"currentCustomer": currentCustomer, "entries": entries, "customers": customers, "totalDuration": totalDuration});
