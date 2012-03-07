'''
Created on Mar 2, 2012

@author: timo
'''
from django import template
from datetime import timedelta
register = template.Library()
import math

@register.filter
def duration(value, arg = "%h:%m"):
    """
    Renders a timedelta in human-readable format. Each format identifier is
    preceded by a '%' and is one of:

    s -- seconds, 00...59
    S -- seconds, integer, values > 59 possible
    m -- minutes, 00...59
    M -- minutes, integer, values > 59 possible
    h -- hours, 0...23
    H -- hours, integer, values > 23 possible
    o -- hours, 2 decimals, 0...23.99
    O -- hours, 2 decimals, values > 23 possible
    D -- days, integer
    """
    
    # Fail silently if the value is not a timedelta.
    if not isinstance(value, timedelta):
        return ""
    
    totalSeconds = value.total_seconds()
    totalDays, remainder = divmod(totalSeconds, 86400)
    modHours, remainder = divmod(remainder, 3600)
    modMinutes, modSeconds = divmod(remainder, 60)
    totalHours = math.floor(totalSeconds / 3600)
    totalMinutes = math.floor(totalSeconds / 60)

    niceOutput = ""
    awaitingFormatIdentifier = False
    
    for c in arg:
        if c == "%":
            if awaitingFormatIdentifier:
                niceOutput = niceOutput + "%"
                awaitingFormatIdentifier = False
            else:
                awaitingFormatIdentifier = True
        else:
            if awaitingFormatIdentifier:
                if c == "s":
                    niceOutput = niceOutput + ("%02d" % modSeconds)
                elif c == "S":
                    niceOutput = niceOutput + ("%02d" % totalSeconds)
                elif c == "m":
                    niceOutput = niceOutput + ("%02d" % modMinutes)
                elif c == "M":
                    niceOutput = niceOutput + ("%02d" % totalMinutes)
                elif c == "h":
                    niceOutput = niceOutput + str(int(modHours))
                elif c == "H":
                    niceOutput = niceOutput + str(int(totalHours))
                elif c == "o":
                    decimalModHours = modHours + (modMinutes / 60)
                    niceOutput = niceOutput + ("%.2f" % decimalModHours)
                elif c == "O":
                    decimalTotalHours = totalHours + (modMinutes / 60)
                    niceOutput = niceOutput + ("%.2f" % decimalTotalHours)
                elif c == "D":
                    niceOutput = niceOutput + str(int(totalDays))
                else:
                    pass
                awaitingFormatIdentifier = False
            else:
                niceOutput = niceOutput + c
    return niceOutput
    
duration.is_safe = True
