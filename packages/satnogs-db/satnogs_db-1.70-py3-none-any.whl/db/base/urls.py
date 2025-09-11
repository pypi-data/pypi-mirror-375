"""Django base URL routings for SatNOGS DB"""
from django.urls import path, re_path

from db.base.views import base as base_views
from db.base.views import suggestions as suggestion_views

BASE_URLPATTERNS = (
    [
        path('', base_views.home, name='home'),
        path('about/', base_views.about, name='about'),
        path('satellites/', base_views.satellites, name='satellites'),
        re_path(
            r'^satellite/(?P<sat_id>[A-Z]{4,4}(?:-\d\d\d\d){4,4})/$',
            base_views.satellite,
            name='satellite'
        ),
        path('satellite/<int:norad>/', base_views.satellite, name='satellite'),
        path(
            'satellite_suggestion_handler/',
            suggestion_views.satellite_suggestion_handler,
            name='satellite_suggestion_handler'
        ),
        path(
            'transmitter-suggestion-history/<str:uuid>/',
            suggestion_views.transmitter_suggestion_history,
            name='transmitter-suggestion-history'
        ),
        path('frames/<int:sat_pk>/', base_views.request_export, name='request_export_all'),
        path(
            'frames/<int:sat_pk>/<int:period>/', base_views.request_export, name='request_export'
        ),
        path('help/', base_views.satnogs_help, name='help'),
        path(
            'transmitter_suggestion_handler/',
            suggestion_views.transmitter_suggestion_handler,
            name='transmitter_suggestion_handler'
        ),
        path('transmitters/', base_views.transmitters_list, name='transmitters_list'),
        path('suggestions/', suggestion_views.suggestions, name='suggestions'),
        path('remove-suggestion/', suggestion_views.remove_suggestion, name='remove-suggestion'),
        path(
            'satellite-suggestions/<int:suggestion_id>',
            suggestion_views.satellite_suggestion_detail,
            name='satellite-suggestion-detail'
        ),
        path(
            'transmitter-suggestions/<int:suggestion_id>',
            suggestion_views.transmitter_suggestion_detail,
            name='transmitter-suggestion-detail'
        ),
        path(
            'satellite-reviewed-suggestions/<int:suggestion_id>',
            suggestion_views.satellite_reviewed_suggestion_detail,
            name='satellite-reviewed-suggestion-detail'
        ),
        path(
            'transmitter-reviewed-suggestions/<int:suggestion_id>',
            suggestion_views.transmitter_reviewed_suggestion_detail,
            name='transmitter-reviewed-suggestion-detail'
        ),
        path(
            'modify-suggestion/<str:suggestion_type>/<int:suggestion_id>/',
            suggestion_views.SuggestionModifyView.as_view(),
            name='modify_suggestion'
        ),
        path('new-suggestion/', suggestion_views.new_suggestion, name='new_suggestion'),
        path('launches/', base_views.launches_list, name='launches_list'),
        path('launch/<int:launch_id>', base_views.launch, name='launch'),
        path('statistics/', base_views.statistics, name='statistics'),
        path('stats/', base_views.stats, name='stats'),
        path('users/edit/', base_views.users_edit, name='users_edit'),
        path('robots.txt', base_views.robots, name='robots'),
        path('search/', base_views.search, name='search_results'),
        path('satellite-search/', base_views.satellite_search, name='satellite_search'),
        path(
            'merge_satellites/', base_views.MergeSatellitesView.as_view(), name='merge_satellites'
        ),
        path(
            'create_satellite/',
            suggestion_views.SatelliteCreateView.as_view(),
            name='create_satellite'
        ),
        path(
            'update_satellite/<int:pk>/',
            suggestion_views.SatelliteUpdateView.as_view(),
            name='update_satellite'
        ),
        path(
            'create_transmitter/<int:satellite_pk>',
            suggestion_views.TransmitterCreateView.as_view(),
            name='create_transmitter'
        ),
        path(
            'update_transmitter/<int:pk>',
            suggestion_views.TransmitterUpdateView.as_view(),
            name='update_transmitter'
        ),
        path(
            'ajax/recent_decoded_cnt/<int:norad>',
            base_views.recent_decoded_cnt,
            name='recent_decoded_cnt'
        ),
    ]
)
