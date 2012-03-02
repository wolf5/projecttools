from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import helpers
from constants import COMMAND_PAUSE, COMMAND_RESUME, STATE_PAUSED, STATE_RUNNING
from models import Customer
from models import Entry
from django.template import RequestContext, Context, loader

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
            topTaskEntry.comment = request.POST["comment"]
            topTaskEntry.save()
    
    if helpers.isAnyTaskRunning(request.user):
        state = STATE_RUNNING
    else:
        state = STATE_PAUSED
        
    customers = Customer.objects.all()
    entries = Entry.objects.filter(owner = request.user).order_by("-start")
    currentCustomer = helpers.getCurrentCustomer(request.user)
    topTaskEntry = helpers.getTopTaskEntry(request.user)
    return render_to_response("timesheet/clock.html", {"state": state, "customers": customers, "currentCustomer": currentCustomer, "entries": entries, "topTaskEntry": topTaskEntry}, RequestContext(request))

def customer_report(request, customer_id, format_identifier):
    currentCustomer = Customer.objects.get(pk = customer_id)
    customers = Customer.objects.all();
    if format_identifier == "csv":
        entries = Entry.objects.filter(owner = request.user, customer = currentCustomer, end__isnull = False)
        template = loader.get_template("timesheet/customer_report.csv")
        context = Context({"currentCustomer": currentCustomer, "entries": entries, "customers": customers, "format_identifier": format_identifier})
        response = HttpResponse(template.render(context), content_type = "text/csv");
        response["Content-Disposition"] = "inline; filename=\"Report-" + currentCustomer.name + ".csv\""
        return response
    else:
        entries = Entry.objects.filter(owner = request.user, customer = currentCustomer, end__isnull = False).order_by("-start")
        return render_to_response("timesheet/customer_report.html", {"currentCustomer": currentCustomer, "entries": entries, "customers": customers, "format_identifier": format_identifier});
