from django import template
from django.template.defaultfilters import stringfilter
from math import modf
import re

register = template.Library()

# TODO - "< 1 km"--remove decimal on meters. Simply < 1 km
@register.filter(name='distance_format', is_safe=True)
@stringfilter
def distance_format(distance):
    # distance = re.sub("[^0-9]", "", distance)
    non_decimal = re.compile(r'[^\d.]+')
    distance = non_decimal.sub('', distance)  # strip non-numeric/decimal
    if distance:  # BC landing-page query function will search empty distances
        distance = float(distance)
        rounded = float('%.2g' % distance)
        km = modf(rounded / 1000.0)
        if km[1]:
            return "%g km" % (km[0] + km[1])
        else:
            return "%g m" % rounded
