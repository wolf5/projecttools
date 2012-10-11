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
    O -- hours, 2 decimals, values > 24 possible
    D -- days, integer
    """
    
    # Fail silently if the value is not a timedelta.
    if not isinstance(value, timedelta):
        return ""

    # Pass 1: Determine which is the smallest unit we have to display
    awaitingFormatIdentifier = False
    seconds_smallest_unit = minutes_smallest_unit = hours_smallest_unit = days_smallest_unit = False
    for c in arg:
        if c == "%":
            if awaitingFormatIdentifier:
                awaitingFormatIdentifier = False
            else:
                awaitingFormatIdentifier = True
        else:
            if awaitingFormatIdentifier:
                if c == "s"or c == "S":
                    seconds_smallest_unit = True
                    minutes_smallest_unit = hours_smallest_unit = days_smallest_unit = False
                elif c == "m" or c == "M":
                    minutes_smallest_unit = not seconds_smallest_unit
                    hours_smallest_unit = days_smallest_unit = False
                elif c == "h" or c == "H" or c == "o" or c == "O":
                    hours_smallest_unit = not minutes_smallest_unit and not seconds_smallest_unit
                    days_smallest_unit = False
                elif c == "D":
                    days_smallest_unit = not hours_smallest_unit and not minutes_smallest_unit and not seconds_smallest_unit
                else:
                    pass
                awaitingFormatIdentifier = False
            else:
                pass
    
    # Now, dissect value and add rounding where necessary
    totalSeconds = (value.microseconds + (value.seconds + value.days * 24 * 3600) * 10**6) / float(10**6)
    
    unroundedTotalDays, remainder = divmod(totalSeconds, 86400)
    unroundedModHours, remainder = divmod(remainder, 3600)
    unroundedModMinutes, unroundedModSeconds = divmod(remainder, 60)
    unroundedTotalHours = math.floor(totalSeconds / 3600)
    unroundedTotalMinutes = math.floor(totalSeconds / 60)
    totalFloatHours = float(totalSeconds) / 3600.0
    totalModFloatHours = float(totalSeconds % 86400) / 3600.0
    
    if days_smallest_unit and divmod(totalSeconds, 86400)[1] >= 43200:
        totalSeconds = totalSeconds + 86400
    elif hours_smallest_unit and divmod(totalSeconds, 3600)[1] >= 1800:
        totalSeconds = totalSeconds + 3600
    elif minutes_smallest_unit and divmod(totalSeconds, 60)[1] >= 30:
        totalSeconds = totalSeconds + 60
    totalDays, remainder = divmod(totalSeconds, 86400)
    modHours, remainder = divmod(remainder, 3600)
    modMinutes, modSeconds = divmod(remainder, 60)
    totalHours = math.floor(totalSeconds / 3600)
    totalMinutes = math.floor(totalSeconds / 60)
    
    
    # Pass 2: Assemble the output
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
                    niceOutput = niceOutput + ("%.2f" % totalModFloatHours)
                elif c == "O":
                    niceOutput = niceOutput + ("%.2f" % totalFloatHours)
                elif c == "D":
                    niceOutput = niceOutput + str(int(totalDays))
                else:
                    pass
                awaitingFormatIdentifier = False
            else:
                niceOutput = niceOutput + c
    return niceOutput
    
duration.is_safe = True
