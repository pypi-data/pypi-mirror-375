"""Base django views for SatNOGS DB"""
import logging
from datetime import timedelta

from bootstrap_modal_forms.generic import BSModalFormView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import BooleanField, Case, Count, IntegerField, Max, OuterRef, Prefetch, Q, \
    Subquery, Value, When
from django.db.models.functions import Coalesce, Substr
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import now

from db.base.forms import MergeSatellitesForm
from db.base.helpers import get_api_token
from db.base.models import DemodData, Launch, Satellite, SatelliteEntry, SatelliteSuggestion, \
    Transmitter, TransmitterEntry, TransmitterSuggestion
from db.base.tasks import background_cache_statistics, delay_task_with_lock, export_frames
from db.base.utils import millify, read_influx

LOGGER = logging.getLogger('db')


def home(request):
    """View to render home page.

    :returns: base/home.html
    """
    prefetch_approved = Prefetch(
        'transmitter_entries', queryset=Transmitter.objects.all(), to_attr='approved_transmitters'
    )
    prefetch_suggested = Prefetch(
        'transmitter_entries',
        queryset=TransmitterSuggestion.objects.all(),
        to_attr='suggested_transmitters'
    )

    newest_sats = Satellite.objects.filter(
        associated_satellite__isnull=True,
    ).exclude(
        satellite_entry__reviewed__isnull=False,
        satellite_entry__approved=False,
    ).order_by('-id')[:5].prefetch_related(prefetch_approved, prefetch_suggested)
    # Calculate latest contributors
    latest_data_satellites = []
    found = False
    date_from = now() - timedelta(days=1)
    data_list = DemodData.objects.filter(timestamp__gte=date_from
                                         ).order_by('-pk').values('satellite_id')
    paginator = Paginator(data_list, 150)
    page = paginator.page(1)
    while not found:
        for data in page.object_list:
            if data['satellite_id'] not in latest_data_satellites:
                latest_data_satellites.append(data['satellite_id'])
            if len(latest_data_satellites) > 5:
                found = True
                break
        if page.has_next():
            page = paginator.page(page.next_page_number())
        else:
            break

    # Check if satellite is merged and if it is then show its associated entry.
    latest_data = Satellite.objects.filter(
        associated_satellite__isnull=True
    ).filter(Q(pk__in=latest_data_satellites) | Q(associated_with__pk__in=latest_data_satellites)
             ).prefetch_related(prefetch_approved, prefetch_suggested)

    # Calculate latest contributors
    date_from = now() - timedelta(days=1)
    latest_submitters = DemodData.objects.filter(timestamp__gte=date_from
                                                 ).values('station').annotate(c=Count('station')
                                                                              ).order_by('-c')

    decaying_sats = Satellite.objects.select_related(
        "latest_tle_set__latest", "satellite_entry"
    ).filter(satellite_entry__status="alive"
             ).annotate(mean_motion=Substr("latest_tle_set__latest__tle2", 53, 11)
                        ).filter(mean_motion__gt=16.0)

    return render(
        request, 'base/home.html', {
            'newest_sats': newest_sats,
            'latest_data': latest_data,
            'latest_submitters': latest_submitters,
            'decaying_sats': decaying_sats
        }
    )


def transmitters_list(request):
    """View to render transmitters list page.

    :returns: base/transmitters.html
    """
    transmitters = Transmitter.objects.filter(
        satellite__associated_satellite__isnull=True,
        satellite__satellite_entry__approved=True,
    ).select_related(
        'satellite',
        'satellite__satellite_entry',
        'satellite__satellite_identifier',
    ).values(
        'uuid', 'satellite__satellite_identifier__sat_id',
        'satellite__satellite_entry__norad_cat_id', 'satellite__satellite_entry__name',
        'satellite__satellite_entry__id', 'type', 'description', 'downlink_low', 'downlink_drift',
        'uplink_low', 'uplink_drift', 'invert', 'downlink_mode__name', 'baud', 'service', 'status',
        'unconfirmed'
    )

    return render(request, 'base/transmitters.html', {
        'transmitters': transmitters,
    })


def launches_list(request):
    """View to render launches list page.

    :returns: base/launches.html
    """
    launches = Launch.objects.annotate(
        satellites_count=Count("embarked_in"),
        launch_date=Max('embarked_in__launched'),
    ).values('id', 'name', 'forum_thread_url', 'satellites_count', 'launch_date')

    return render(request, 'base/launches.html', {
        'launches': launches,
    })


def launch(request, launch_id=None):
    """View to render launch page.

    :returns: base/launch.html
    """
    launch_obj = get_object_or_404(
        Launch.objects.filter(id=launch_id).annotate(
            satellites_count=Count("embarked_in"),
            launch_date=Max('embarked_in__launched'),
        )
    )

    launched_satellites = Satellite.objects.filter(
        satellite_entry__launch_id=launch_id, associated_satellite__isnull=True
    ).values(
        'satellite_entry__name',
        'satellite_identifier__sat_id',
        'satellite_entry__norad_cat_id',
    )
    return render(
        request, 'base/launch.html', {
            'launch': launch_obj,
            'satellites': launched_satellites
        }
    )


def robots(request):
    """robots.txt handler

    :returns: robots.txt
    """
    data = render(request, 'robots.txt', {'environment': settings.ENVIRONMENT})
    response = HttpResponse(data, content_type='text/plain; charset=utf-8')
    return response


def satellites(request):
    """View to render satellites page.

    :returns: base/satellites.html
    """
    transmitter_subquery = Transmitter.objects.filter(
        satellite=OuterRef('pk')
    ).values('satellite').annotate(count=Count('id')).values('count')

    satellite_objects = Satellite.objects.filter(
        associated_satellite__isnull=True, satellite_entry__approved=True
    ).annotate(
        approved_transmitters_count=Coalesce(
            Subquery(transmitter_subquery, output_field=IntegerField()), 0
        ),
        satellite_suggestions_count=Count(
            'satellite_identifier__satellite_entries',
            filter=Q(satellite_identifier__satellite_entries__reviewed__isnull=True)
        )
    ).values(
        'satellite_entry__id',
        'satellite_entry__name',
        'satellite_entry__norad_cat_id',
        'satellite_entry__status',
        'satellite_entry__names',
        'satellite_entry__norad_follow_id',
        'satellite_entry__operator',
        'satellite_entry__launched',
        'satellite_entry__website',
        'satellite_entry__dashboard_url',
        'satellite_entry__countries',
        'satellite_entry__launch__name',
        'satellite_identifier__sat_id',
        'approved_transmitters_count',
        'satellite_suggestions_count',
    )
    return render(request, 'base/satellites.html', {'satellites': satellite_objects})


def get_satellite_suggestion_history(sat, is_user_authenticated):
    """Gets the history of suggestions for a satellite"""
    queryset = SatelliteEntry.objects.filter(
        satellite_identifier=sat.satellite_identifier, reviewed__isnull=False
    ).order_by('-reviewed')

    if not is_user_authenticated:
        queryset = queryset.filter(approved=True)

    return queryset


def satellite(request, norad=None, sat_id=None):
    """View to render satellite page.

    :returns: base/satellite.html
    """
    if norad:
        satellite_obj = get_object_or_404(Satellite, satellite_entry__norad_cat_id=norad)
    else:
        satellite_obj = get_object_or_404(Satellite, satellite_identifier__sat_id=sat_id)

    if satellite_obj.associated_satellite:
        satellite_obj = satellite_obj.associated_satellite

    latest_tle = None
    latest_tle_set = None
    latest_tle_warning = None
    if hasattr(satellite_obj, 'latest_tle_set'):
        latest_tle_set = satellite_obj.latest_tle_set

    if latest_tle_set:
        if request.user.has_perm('base.access_all_tles'):
            latest_tle = latest_tle_set.latest
        else:
            latest_tle = latest_tle_set.latest_distributable
            if latest_tle_set.latest != latest_tle_set.latest_distributable:
                latest_tle_warning = "There is at least one newer non-redestributable TLE set."

    satellite_suggestions = SatelliteSuggestion.objects.select_related(
        'satellite_identifier', 'satellite_identifier__satellite', 'created_by'
    ).filter(satellite_identifier=satellite_obj.satellite_identifier)

    reviewed_transmitter_uuids = TransmitterEntry.objects.filter(
        reviewed__isnull=False, satellite=satellite_obj
    ).values('uuid')

    transmitter_suggestions = TransmitterEntry.objects.filter(
        reviewed__isnull=True, satellite=satellite_obj
    ).select_related(
        'satellite', 'satellite__satellite_identifier', 'satellite__satellite_entry', 'created_by'
    ).annotate(
        is_new=Case(
            When(uuid__in=Subquery(reviewed_transmitter_uuids), then=Value(False)),
            default=Value(True),
            output_field=BooleanField()
        )
    )

    try:
        # pull the last 5 observers and their last submission timestamps for this satellite and for
        # the satellites that are associated with it for the last 24 hours
        satellites_list = list(satellite_obj.associated_with.all().values_list('pk', flat=True))
        satellites_list.append(satellite_obj.pk)

        recent_observers = DemodData.objects.filter(
            satellite__in=satellites_list, timestamp__gte=now() - timedelta(days=1)
        ).values('observer').annotate(latest_payload=Max('timestamp')
                                      ).order_by('-latest_payload')[:5]
    except (ObjectDoesNotExist, IndexError):
        recent_observers = ''

    # decide whether a map (and map link) will be visible or not (ie: re-entered)
    showmap = False
    if satellite_obj.satellite_entry.status not in ['re-entered', 'future'] and latest_tle:
        showmap = True

    return render(
        request, 'base/satellite.html', {
            'satellite': satellite_obj,
            'exists': satellite_obj.satellite_entry.approved,
            'latest_tle': latest_tle,
            'transmitter_suggestions': transmitter_suggestions,
            'satellite_suggestions': satellite_suggestions,
            'suggestion_count': transmitter_suggestions.count() + satellite_suggestions.count(),
            'mapbox_token': settings.MAPBOX_TOKEN,
            'recent_observers': recent_observers,
            'badge_telemetry_count': millify(satellite_obj.telemetry_data_count),
            'showmap': showmap,
            "latest_tle_warning": latest_tle_warning,
            "suggestion_history_items": get_satellite_suggestion_history(
                satellite_obj, request.user.is_authenticated
            )
        }
    )


@login_required
def request_export(request, sat_pk, period=None):
    """View to request frames export download.

    This triggers a request to collect and zip up the requested data for
    download, which the user is notified of via email when the celery task is
    completed.
    :returns: the originating satellite page
    """
    satellite_obj = get_object_or_404(Satellite, id=sat_pk)
    if satellite_obj.associated_satellite:
        satellite_obj = satellite_obj.associated_satellite

    export_frames.delay(satellite_obj.satellite_identifier.sat_id, request.user.id, period)
    messages.success(
        request, ('Your download request was received. '
                  'You will get an email when it\'s ready')
    )
    return redirect(
        reverse('satellite', kwargs={'sat_id': satellite_obj.satellite_identifier.sat_id})
    )


def about(request):
    """View to render about page.

    :returns: base/about.html
    """
    return render(request, 'base/about.html')


def satnogs_help(request):
    """View to render help modal. Have to avoid builtin 'help' name

    :returns: base/modals/help.html
    """
    return render(request, 'base/modals/satnogs_help.html')


def remove_leading_zeros(s):
    """Removes leading zeros from a string"""
    if s.isdigit():
        stripped = s.lstrip('0')
        if not stripped:
            stripped = '0'
        zeros_removed = len(s) - len(stripped)
        return stripped, zeros_removed
    return s, 0


def search(request):
    """View to render search page.

    :returns: base/search.html
    """
    query_string = ''
    results = Satellite.objects.none()
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q'].strip()

    if query_string:
        query_string_zeros_removed, zeros_removed = remove_leading_zeros(query_string)

        results = Satellite.objects.filter(
            associated_satellite__isnull=True, satellite_entry__approved=True
        )

        # If we removed leading zeros, we need to avoid results with norad e.g. 11234 if the query
        # was 01234
        if query_string_zeros_removed.isdigit() and zeros_removed:
            results = results.filter(
                Q(satellite_entry__name__icontains=query_string)
                | Q(satellite_entry__names__icontains=query_string)
                | Q(satellite_entry__norad_cat_id=query_string_zeros_removed)
                | Q(satellite_entry__norad_follow_id=query_string_zeros_removed)
                | Q(satellite_identifier__sat_id__icontains=query_string)
                | Q(associated_with__satellite_identifier__sat_id__icontains=query_string)
            )
        else:
            results = results.filter(
                Q(satellite_entry__name__icontains=query_string)
                | Q(satellite_entry__names__icontains=query_string)
                | Q(satellite_entry__norad_cat_id__icontains=query_string)
                | Q(satellite_entry__norad_follow_id__icontains=query_string)
                | Q(satellite_identifier__sat_id__icontains=query_string)
                | Q(associated_with__satellite_identifier__sat_id__icontains=query_string)
            )

        results = results.order_by('satellite_entry__name').prefetch_related(
            Prefetch(
                'transmitter_entries',
                queryset=Transmitter.objects.all(),
                to_attr='approved_transmitters'
            )
        ).distinct()

    if results.count() == 1:
        return redirect(
            reverse('satellite', kwargs={'sat_id': results[0].satellite_identifier.sat_id})
        )

    return render(request, 'base/search.html', {'results': results, 'q': query_string})


def satellite_search(request):
    """View to return satellite search results using AJAX.

    :returns: Satellites in json format
    """
    query_string = ''
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

    results = []
    if query_string:
        results = Satellite.objects.filter(
            associated_satellite__isnull=True, satellite_entry__approved=True
        ).filter(
            Q(satellite_entry__name__icontains=query_string)
            | Q(satellite_entry__names__icontains=query_string)
            | Q(satellite_entry__norad_cat_id__icontains=query_string)
            | Q(satellite_entry__norad_follow_id__icontains=query_string)
            | Q(satellite_identifier__sat_id__icontains=query_string)
            | Q(associated_with__satellite_identifier__sat_id__icontains=query_string)
        ).values('id', 'satellite_entry__norad_cat_id', 'satellite_entry__name').distinct()

    data = []
    for result in results:
        label = f"{result['satellite_entry__norad_cat_id']} - {result['satellite_entry__name']}"
        value = result['id']
        data.append({
            'value': value,
            'label': label,
        })

    return JsonResponse(data, safe=False)


def stats(request):
    """View to render stats page.

    :returns: base/stats.html or base/calc-stats.html
    """
    cached_satellites = []
    ids = cache.get('satellites_ids')
    observers = cache.get('stats_observers')
    if not ids or not observers:
        delay_task_with_lock(background_cache_statistics, 1, 3600)
        return render(request, 'base/calc-stats.html')

    for sid in ids:
        stat = cache.get(sid)
        cached_satellites.append(stat)

    return render(
        request, 'base/stats.html', {
            'satellites': cached_satellites,
            'observers': observers
        }
    )


def statistics(request):
    """Return transmitter cached statistics if the cache exist

    :returns: JsonResponse of statistics
    """
    cached_stats = cache.get('stats_transmitters')
    if not cached_stats:
        cached_stats = []
    return JsonResponse(cached_stats, safe=False)


@login_required
def users_edit(request):
    """View to render user settings page.

    :returns: base/users_edit.html
    """
    token = get_api_token(request.user)
    return render(request, 'base/modals/users_edit.html', {'token': token})


def recent_decoded_cnt(request, norad):
    """Returns a query of InfluxDB for a count of points across a given measurement
    (norad) over the last 30 days, with a timestamp in unixtime.

    :returns: JSON of point counts as JsonResponse
    """
    if settings.USE_INFLUX:
        results = read_influx(norad)
        return JsonResponse(results, safe=False)

    return JsonResponse({})


class MergeSatellitesView(LoginRequiredMixin, BSModalFormView):
    """Merges satellites if user has merge permission.
    """
    template_name = 'base/modals/satellites_merge.html'
    form_class = MergeSatellitesForm
    user = get_user_model()

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.user.has_perm('base.merge_satellites'):
            # Check if request is an AJAX one
            if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                primary_satellite = form.cleaned_data['primary_satellite']
                associated_satellite = form.cleaned_data['associated_satellite']
                associated_satellite.associated_satellite = primary_satellite
                associated_satellite.save(update_fields=['associated_satellite'])
                messages.success(self.request, ('Satellites have been merged!'))
        else:
            messages.error(self.request, ('No permission to merge satellites!'))
            response = redirect(reverse('satellites'))

        return response

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')
