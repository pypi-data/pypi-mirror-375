"""Django template tags for SatNOGS DB"""
from hashlib import md5

from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


@register.filter
def country_codes_from_string(value):
    """Returns the country code (lowercase) from a stringified list"""
    return [code.lower() for code in value.split(',')]


# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=40):
    """Returns the Gravatar URL based on user's email address"""
    return "https://www.gravatar.com/avatar/%s?s=%s" % (
        md5(email.lower().encode('utf-8')).hexdigest(), str(size)
    )


@register.simple_tag
def active(request, urls):
    """Returns if this is an active URL"""
    if request.path in (reverse(url) for url in urls.split()):
        return 'active'
    return None


@register.filter
def frq(value):
    """Returns Hz formatted frequency html string"""
    try:
        to_format = float(value)
    except (TypeError, ValueError):
        return ''
    if to_format < 1000:
        # Frequency is in Hz range
        formatted = int(to_format)
        response = format_html('{0} Hz', formatted)
    if 1000 <= to_format < 1000000:
        # Frequency is in kHz range
        formatted = format(to_format / 1000, '.3f')
        response = format_html('{0} kHz', formatted)
    if to_format >= 1000000:
        # Frequency is in MHz range
        formatted = format((to_format // 1000) / 1000, '.3f')
        response = format_html('{0} MHz', formatted)
    return response


@register.simple_tag
def dfrq(frequency, drift):
    """Returns frequency drifted by a drift value"""
    print(frequency, drift, flush=True)
    try:
        frequency_value = float(frequency)
        drift_value = float(drift)
    except (TypeError, ValueError):
        return '-'
    drifted_frequency = frequency_value + ((frequency_value * drift_value) / pow(10, 9))
    return str(frq(round(drifted_frequency))) + ' (' + str(
        round(frequency_value - drifted_frequency)
    ) + ' Hz or ' + str(drift) + ' ppb)'
