"""SatNOGS DB API throttling classes, django rest framework"""
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import throttling

from db.base.models import Satellite


class GetTelemetryAnononymousRateThrottle(throttling.AnonRateThrottle):
    """Anonymous GET Throttling for Telemetry API endpoint"""
    scope = 'get_telemetry_anon'

    def allow_request(self, request, view):
        if request.method == 'POST':
            return True
        return super().allow_request(request, view)


class GetTelemetryUserRateThrottle(throttling.UserRateThrottle):
    """User GET Throttling for Telemetry API endpoint"""
    scope = 'get_telemetry_user'

    def allow_request(self, request, view):
        if request.method == 'POST':
            return True
        return super().allow_request(request, view)


class GetTelemetryViolatorThrottle(throttling.BaseThrottle):
    """Violator satellites GET Throttling for Telemetry API endpoint"""
    scope = 'get_telemetry_violator'

    def allow_request(self, request, view):
        if request.method == 'POST':
            return True
        satellite = request.query_params.get('satellite', None)
        sat_id = request.query_params.get('sat_id', None)
        violation = None

        if sat_id:
            violation = cache.get('violator_' + sat_id)
        elif satellite:
            violation = cache.get('violator_' + str(satellite))
        else:
            return True

        if violation is None:
            if sat_id:
                satellite_obj = get_object_or_404(Satellite, satellite_identifier__sat_id=sat_id)
            else:
                satellite_obj = get_object_or_404(
                    Satellite, satellite_entry__norad_cat_id=satellite
                )
            if satellite_obj.associated_satellite:
                satellite_obj = satellite_obj.associated_satellite
            if satellite_obj.has_bad_transmitter:
                return cache.add('violator_telemetry_' + str(satellite_obj.id), True, 86400)
        elif violation['status']:
            return cache.add('violator_telemetry_' + str(violation['id']), True, 86400)
        return True
