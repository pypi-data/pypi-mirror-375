"""django views for SatNOGS DB suggestions"""
import logging

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import BadRequest, PermissionDenied
from django.db import transaction
from django.db.models import BooleanField, Case, Subquery, Value, When
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.views.generic import UpdateView

from db.base.forms import SatelliteCreateForm, SatelliteSuggestionModifyForm, \
    SatelliteUpdateForm, TransmitterCreateForm, TransmitterSuggestionModifyForm, \
    TransmitterUpdateForm
from db.base.models import Satellite, SatelliteEntry, SatelliteIdentifier, SatelliteSuggestion, \
    Transmitter, TransmitterEntry, TransmitterSuggestion
from db.base.tasks import notify_suggestion, notify_suggestion_review

LOGGER = logging.getLogger('db')


class SatelliteCreateView(LoginRequiredMixin, BSModalCreateView):
    """A django-bootstrap-modal-forms view for creating satellite suggestions"""
    template_name = 'base/satellite-suggestion-form.html'
    model = SatelliteEntry
    form_class = SatelliteCreateForm
    success_message = 'Your satellite suggestion was stored successfully and will be \
                       reviewed by a moderator. Thanks for contributing!'

    user = get_user_model()
    sat_id = ''
    is_copy = False

    def get_initial(self):
        initial = super().get_initial()
        from_pk = self.request.GET.get("from")
        if from_pk and from_pk.isdigit():
            self.is_copy = True
            original_obj = get_object_or_404(SatelliteSuggestion, pk=int(from_pk))
            for field in self.model._meta.fields:
                if field.name not in ('id', 'citation'):
                    initial[field.name] = getattr(original_obj, field.name)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Display 'Update Satellite' when copying
        context["suggestion_mode"] = 'update' if self.is_copy else 'create'
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        satellite_entry = form.instance
        satellite_obj = None
        # Create Satellite Identifier only when POST request is for saving and
        # NORAD ID is not used by other Satellite.
        # Check if request is an AJAX one
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # If the form doesn't contain NORAD ID, create a new satellite
                if satellite_entry.norad_cat_id:
                    satellite_obj = Satellite.objects.get(
                        satellite_entry__norad_cat_id=satellite_entry.norad_cat_id
                    )
                    satellite_entry.satellite_identifier = satellite_obj.satellite_identifier
                else:
                    satellite_entry.satellite_identifier = SatelliteIdentifier.objects.create()
            except Satellite.DoesNotExist:
                satellite_entry.satellite_identifier = SatelliteIdentifier.objects.create()
            finally:
                self.sat_id = satellite_entry.satellite_identifier.sat_id

        satellite_entry.created = now()
        satellite_entry.created_by = self.user

        # form_valid triggers also save() allowing us to use satellite_entry
        # for creating Satellite object, see comment bellow.
        response = super().form_valid(form)

        # Prevents sending notification twice as form_valid is triggered for
        # validation and saving. Also create and Satellite object only when POST
        # request is for saving and NORAD ID is not used by other Satellite.
        # Check if request is an AJAX one
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if not satellite_obj:
                satellite_obj = Satellite.objects.create(
                    satellite_identifier=satellite_entry.satellite_identifier,
                    satellite_entry=satellite_entry
                )
            notify_suggestion.delay(
                satellite_obj.satellite_entry.pk, self.object.pk, self.user.id, 'satellite'
            )

        return response

    def get_success_url(self):
        return reverse('satellite', kwargs={"sat_id": self.sat_id}) + '#suggestions'


class SatelliteUpdateView(LoginRequiredMixin, BSModalUpdateView):
    """A django-bootstrap-modal-forms view for updating satellite entries"""
    template_name = 'base/satellite-suggestion-form.html'
    model = SatelliteEntry
    form_class = SatelliteUpdateForm
    success_message = 'Your satellite suggestion was stored successfully and will be \
                       reviewed by a moderator. Thanks for contributing!'

    user = get_user_model()
    sat_id = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["suggestion_mode"] = 'update'
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        satellite_entry = form.instance
        initial_satellite_entry_pk = satellite_entry.pk
        # Add update as a new SatelliteEntry object and change fields in order to be a suggestion
        satellite_entry.pk = None
        satellite_entry.reviewed = None
        satellite_entry.reviewer = None
        satellite_entry.approved = False
        satellite_entry.created = now()
        satellite_entry.created_by = self.user
        # Prevents sending notification twice as form_valid is triggered for validation and saving
        # Check if request is an AJAX one
        self.sat_id = satellite_entry.satellite_identifier.sat_id
        response = super().form_valid(form)
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            notify_suggestion.delay(
                initial_satellite_entry_pk, self.object.id, self.user.id, 'satellite'
            )
        return response

    def get_success_url(self):
        return reverse('satellite', kwargs={"sat_id": self.sat_id}) + '#suggestions'


class TransmitterCreateView(LoginRequiredMixin, BSModalCreateView):
    """A django-bootstrap-modal-forms view for creating transmitter suggestions"""
    template_name = 'base/transmitter-suggestion-form.html'
    model = TransmitterEntry
    form_class = TransmitterCreateForm
    success_message = 'Your transmitter suggestion was stored successfully and will be \
                       reviewed by a moderator. Thanks for contibuting!'

    satellite = Satellite()
    user = get_user_model()
    is_copy = False

    def get_initial(self):
        initial = super().get_initial()
        from_pk = self.request.GET.get("from")
        if from_pk and from_pk.isdigit():
            self.is_copy = True
            original_obj = get_object_or_404(TransmitterSuggestion, pk=int(from_pk))
            for field in self.model._meta.fields:
                if field.name not in ('id', 'citation'):
                    initial[field.name] = getattr(original_obj, field.name)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Display 'Update Satellite' when copying
        context["suggestion_mode"] = 'update' if self.is_copy else 'create'
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Overridden so we can make sure the `Satellite` instance exists first
        """
        self.satellite = get_object_or_404(
            Satellite.objects.select_related('satellite_identifier').all(),
            satellite_entry__pk=kwargs['satellite_pk']
        )
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Overridden to add the `Satellite` relation to the `Transmitter` instance.
        """
        transmitter = form.instance
        transmitter.satellite = self.satellite
        transmitter.created = now()
        transmitter.created_by = self.user
        # Prevents sending notification twice as form_valid is triggered for validation and saving
        # Check if request is an AJAX one
        response = super().form_valid(form)
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            notify_suggestion.delay(
                transmitter.satellite.satellite_entry.id, self.object.id, self.user.id,
                'transmitter'
            )
        return response

    def get_success_url(self):
        return reverse(
            'satellite', kwargs={"sat_id": self.satellite.satellite_identifier.sat_id}
        ) + '#suggestions'


class TransmitterUpdateView(LoginRequiredMixin, BSModalUpdateView):
    """A django-bootstrap-modal-forms view for updating transmitter entries"""
    template_name = 'base/transmitter-suggestion-form.html'
    model = TransmitterEntry
    form_class = TransmitterUpdateForm
    success_message = 'Your transmitter suggestion was stored successfully and will be \
                       reviewed by a moderator. Thanks for contributing!'

    user = get_user_model()
    sat_id = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["suggestion_mode"] = 'update'
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        transmitter = form.instance
        # Add update as a new TransmitterEntry object and change fields in order to be a suggestion
        transmitter.pk = None
        transmitter.reviewed = None
        transmitter.reviewer = None
        transmitter.approved = False
        transmitter.created = now()
        transmitter.created_by = self.user
        # Prevents sending notification twice as form_valid is triggered for validation and saving
        # Check if request is an AJAX one
        self.sat_id = transmitter.satellite.satellite_identifier.sat_id
        response = super().form_valid(form)
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            notify_suggestion.delay(
                transmitter.satellite.satellite_entry.id, self.object.id, self.user.id,
                'transmitter'
            )
        return response

    def get_success_url(self):
        return reverse('satellite', kwargs={"sat_id": self.sat_id}) + '#suggestions'


@login_required
def new_suggestion(request):
    """View for submitting new suggestions"""
    suggestion_type = request.GET.get('type')
    if not suggestion_type or suggestion_type not in ('satellite', 'transmitter'):
        suggestion_type = None
    suggestion_mode = request.GET.get('mode', None)
    copy_from_pk = request.GET.get('from', None)
    if suggestion_mode not in ('copy', 'update'):
        suggestion_mode = 'create'
    sat_entry_pk = request.GET.get('satellite', None)  # It is the pk of SatelliteEntry model
    # It is the pk of Transmitter (when suggesting an edit to a transmitter )
    transmitter_pk = request.GET.get('transmitter', None)
    satellite_obj = get_object_or_404(
        Satellite.objects.values('id', 'satellite_entry__norad_cat_id', 'satellite_entry__name'),
        satellite_entry__pk=sat_entry_pk
    ) if sat_entry_pk else None
    return render(
        request, 'base/new-suggestion.html', {
            'suggestion_type': suggestion_type,
            'suggestion_mode': suggestion_mode,
            'sat_entry_pk': sat_entry_pk,
            'copy_from_pk': copy_from_pk,
            'transmitter_pk': transmitter_pk,
            'satellite': satellite_obj
        }
    )


@login_required
def suggestions(request):
    """View for listing all suggestions."""

    reviewed_satellite_ids = SatelliteEntry.objects.filter(reviewed__isnull=False
                                                           ).values('satellite_identifier')
    satellite_suggestions = SatelliteEntry.objects.filter(reviewed__isnull=True).select_related(
        'satellite_identifier', 'satellite_identifier__satellite', 'created_by'
    ).annotate(
        is_new=Case(
            When(satellite_identifier__in=Subquery(reviewed_satellite_ids), then=Value(False)),
            default=Value(True),
            output_field=BooleanField()
        )
    )

    reviewed_transmitter_uuids = TransmitterEntry.objects.filter(reviewed__isnull=False
                                                                 ).values('uuid')

    transmitter_suggestions = TransmitterEntry.objects.filter(
        reviewed__isnull=True
    ).select_related(
        'satellite', 'satellite__satellite_identifier', 'satellite__satellite_entry', 'created_by'
    ).annotate(
        is_new=Case(
            When(uuid__in=Subquery(reviewed_transmitter_uuids), then=Value(False)),
            default=Value(True),
            output_field=BooleanField()
        )
    )

    return render(
        request, 'base/suggestions.html', {
            'satellites': satellite_suggestions,
            'transmitters': transmitter_suggestions
        }
    )


def satellite_suggestion_detail(request, suggestion_id):
    """Detail page for satellite suggestions"""
    satellite_entry = get_object_or_404(SatelliteSuggestion, pk=suggestion_id)
    try:
        current_entry = satellite_entry.satellite_identifier.satellite.satellite_entry
        if not current_entry.reviewed:
            current_entry = None
    except AttributeError:
        current_entry = None

    return render(
        request, 'base/satellite-suggestion-detail.html', {
            'satellite_entry': satellite_entry,
            'current_entry': current_entry,
            'is_new': current_entry is None,
            'is_reviewed': False
        }
    )


def satellite_reviewed_suggestion_detail(request, suggestion_id):
    """Detail page for reviewed satellite suggestions"""
    satellite_entry = get_object_or_404(SatelliteEntry, id=suggestion_id, reviewed__isnull=False)

    current_entry = SatelliteEntry.objects.filter(
        satellite_identifier=satellite_entry.satellite_identifier,
        approved=True,
        reviewed__lt=satellite_entry.created
    ).order_by('-reviewed').first()

    return render(
        request, 'base/satellite-suggestion-detail.html', {
            'satellite_entry': satellite_entry,
            'current_entry': current_entry,
            'is_new': current_entry is None,
            'is_reviewed': True
        }
    )


def transmitter_suggestion_detail(request, suggestion_id):
    """Detail page for transmitter suggestions"""
    transmitter_entry = get_object_or_404(TransmitterSuggestion, pk=suggestion_id)
    try:
        current_entry = Transmitter.objects.get(
            reviewed__isnull=False, uuid=transmitter_entry.uuid
        )
    except Transmitter.DoesNotExist:
        current_entry = None
    return render(
        request,
        'base/transmitter-suggestion-detail.html',
        {
            'transmitter_entry': transmitter_entry,
            'current_entry': current_entry,
            'is_new': current_entry is None,
            'is_reviewed': False
        },
    )


def transmitter_reviewed_suggestion_detail(request, suggestion_id):
    """Detail page for reviewed transmitter suggestions"""
    transmitter_entry = get_object_or_404(
        TransmitterEntry.objects.filter(reviewed__isnull=False), pk=suggestion_id
    )

    current_entry = Transmitter.objects.filter(
        uuid=transmitter_entry.uuid, approved=True, reviewed__lt=transmitter_entry.created
    ).order_by('-reviewed').first()

    return render(
        request,
        'base/transmitter-suggestion-detail.html',
        {
            'transmitter_entry': transmitter_entry,
            'current_entry': current_entry,
            'is_new': current_entry is None,
            'is_reviewed': True
        },
    )


@require_POST
def remove_suggestion(request):
    """Removes a suggestion if the user is the suggestion's creator or an admin"""
    suggestion_type = request.POST.get('suggestion_type')
    suggestion_id = request.POST.get('suggestion_id')

    if suggestion_type not in ['satellite', 'transmitter']:
        return HttpResponseBadRequest("Invalid suggestion type.")

    try:
        suggestion_id = int(suggestion_id)
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid suggestion ID.")

    if suggestion_type == 'satellite':
        suggestion = get_object_or_404(SatelliteSuggestion, id=suggestion_id)
    elif suggestion_type == 'transmitter':
        suggestion = get_object_or_404(TransmitterSuggestion, id=suggestion_id)
    else:
        return HttpResponseBadRequest("Invalid suggestion type.")
    if suggestion.created_by != request.user and (
        (suggestion_type == 'satellite'
         and not request.user.has_perm('base.delete_satellitesuggestion')) or  # noqa W504
        (suggestion_type == 'transmitter'
         and not request.user.has_perm('base.delete_transmittersuggestion'))):
        return HttpResponseForbidden("You are not allowed to delete this suggestion.")
    with transaction.atomic():
        # If the suggested satellite doesn't exist yet, delete the related instances as well
        if (suggestion_type == 'satellite'
                and not suggestion.satellite_identifier.satellite.satellite_entry.approved):
            suggestion.delete()
            suggestion.satellite_identifier.satellite.transmitter_entries.all().delete()
            suggestion.satellite_identifier.delete()
            # Satellite model instance get deleted due to on_delete CASCADE
        else:
            suggestion.delete()

    messages.success(request, 'Suggestion deleted successfully.')

    return redirect('suggestions')


class SuggestionModifyView(UpdateView):
    """Class for modifying a submitted suggestion"""

    template_name = 'base/modify-suggestion.html'
    sat_id = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suggestion_mode'] = 'modify'
        context['suggestion_type'] = self.kwargs.get('suggestion_type')
        return context

    def get_object(self, queryset=None):
        suggestion_type = self.kwargs.get('suggestion_type')
        suggestion_id = self.kwargs.get('suggestion_id')

        if not suggestion_type or suggestion_type not in ('satellite', 'transmitter'):
            raise BadRequest(
                'Suggestion type invalid. Choose between \'satellite\' and \'transmitter\'.'
            )

        try:
            if suggestion_type == 'satellite':
                suggestion = SatelliteSuggestion.objects.select_related('satellite_identifier'
                                                                        ).get(id=suggestion_id)
                self.sat_id = suggestion.satellite_identifier.sat_id
            else:
                suggestion = TransmitterSuggestion.objects.select_related(
                    'satellite__satellite_identifier'
                ).get(id=suggestion_id)
                self.sat_id = suggestion.satellite.satellite_identifier.sat_id
        except (SatelliteEntry.DoesNotExist, TransmitterEntry.DoesNotExist) as error:
            raise Http404('Could not find the suggestion.') from error

        if self.request.user != suggestion.created_by:
            raise PermissionDenied("You are not allowed to modify this suggestion.")
        return suggestion

    def get_form_class(self):
        suggestion_type = self.kwargs.get('suggestion_type')
        if suggestion_type == 'satellite':
            return SatelliteSuggestionModifyForm
        return TransmitterSuggestionModifyForm

    def form_valid(self, form):
        messages.success(self.request, 'Suggestion was successfully modified.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('satellite', kwargs={"sat_id": self.sat_id}) + '#suggestions'


def transmitter_suggestion_history(request, uuid):
    """View for getting the history of suggestions for a transmitter"""
    transmitter_history_items = TransmitterEntry.objects.filter(
        uuid=uuid, reviewed__isnull=False
    ).order_by('-reviewed')
    if not request.user.is_authenticated:
        transmitter_history_items = transmitter_history_items.filter(approved=True)
    return render(
        request, 'includes/transmitter_history_table.html',
        {'transmitter_history_items': transmitter_history_items}
    )


@login_required
@require_POST
def satellite_suggestion_handler(request):
    """Returns the Satellite page after approving or rejecting a suggestion if
    user has approve permission.

    :returns: Satellite page
    """
    satellite_entry = get_object_or_404(SatelliteSuggestion, pk=request.POST['pk'])
    satellite_obj = get_object_or_404(
        Satellite, satellite_identifier=satellite_entry.satellite_identifier
    )
    if request.user.has_perm('base.approve_satellitesuggestion'):
        if request.POST['verdict'] == 'approve':
            satellite_entry.approved = True
            messages.success(request, ('Satellite approved.'))
        elif request.POST['verdict'] == 'reject':
            satellite_entry.approved = False
            messages.success(request, ('Satellite rejected.'))
        satellite_entry.reviewed = now()
        satellite_entry.reviewer = request.user
        satellite_entry.review_message = request.POST['review_message'] or None

        satellite_entry.save(update_fields=['approved', 'reviewed', 'reviewer', 'review_message'])
        if satellite_entry.receive_review_update:
            notify_suggestion_review.delay('satellite', satellite_entry.pk)

        if satellite_entry.approved:
            satellite_obj.satellite_entry = satellite_entry
            satellite_obj.save(update_fields=['satellite_entry'])
    redirect_page = redirect(reverse('suggestions'))
    return redirect_page


@login_required
@require_POST
def transmitter_suggestion_handler(request):
    """Returns the Satellite page after approving or rejecting a suggestion if
    user has approve permission.

    :returns: Satellite page
    """
    transmitter = get_object_or_404(TransmitterSuggestion, pk=request.POST['pk'])
    if request.user.has_perm('base.approve_transmittersuggestion'):
        if request.POST['verdict'] == 'approve':
            # Force re-checking of bad transmitters be removing permanent cache
            cache.delete("violator_" + str(transmitter.satellite.satellite_entry.norad_cat_id))
            cache.delete("violator_" + transmitter.satellite.satellite_identifier.sat_id)
            for merged_satellite in transmitter.satellite.associated_with.all():
                cache.delete("violator_" + merged_satellite.satellite_identifier.sat_id)
            transmitter.approved = True
            messages.success(request, ('Transmitter approved.'))
        elif request.POST['verdict'] == 'reject':
            transmitter.approved = False
            messages.success(request, ('Transmitter rejected.'))
        transmitter.reviewed = now()
        transmitter.reviewer = request.user
        transmitter.review_message = request.POST['review_message'] or None
        transmitter.save(update_fields=['approved', 'reviewed', 'reviewer', 'review_message'])
        if transmitter.receive_review_update:
            notify_suggestion_review.delay('transmitter', transmitter.pk)
    redirect_page = redirect(f"{reverse('suggestions')}#transmitters")
    return redirect_page
