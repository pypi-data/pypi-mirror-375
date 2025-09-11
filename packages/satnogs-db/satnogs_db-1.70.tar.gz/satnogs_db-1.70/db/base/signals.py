"""Django signals for SatNOGS DB"""
import json
import logging

import h5py
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.utils.timezone import now

from db.base.models import Artifact, LatestTleSet, Mode, Satellite, TransmitterEntry
from db.base.utils import remove_latest_tle_set, update_latest_tle_sets

LOGGER = logging.getLogger('db')


def _remove_latest_tle_set(sender, instance, **kwargs):  # pylint: disable=W0613
    """Updates if needed LatestTle entries"""
    if instance.satellite_entry.status in [
            're-entered', 'future'
    ] or instance.associated_satellite or not instance.satellite_entry.approved:
        remove_latest_tle_set(satellite_pk=instance.pk)
    else:
        update_latest_tle_sets(satellite_pks=[instance.pk])


def _extract_network_obs_id(sender, instance, created, **kwargs):  # pylint: disable=W0613
    post_save.disconnect(_extract_network_obs_id, sender=Artifact)
    try:
        with h5py.File(instance.artifact_file, 'r') as h5_file:
            if h5_file.attrs["artifact_version"] == 1:
                # Artifacts version 1
                instance.network_obs_id = h5_file.attrs["observation_id"]
            else:
                # Artifacts version 2 or later
                metadata = json.loads(h5_file.attrs["metadata"])
                instance.network_obs_id = metadata["observation_id"]
    except OSError as error:
        LOGGER.warning(error)

    instance.save()
    post_save.connect(_extract_network_obs_id, sender=Artifact, weak=False)


def _invalidate_api_cache(sender, instance, created=None, **kwargs):  # pylint: disable=W0613
    for key in sender.CacheOptions.cache_purge_keys:
        cache.delete(key)


def _inactivate_transmitters_on_sat_reentry(sender, instance, **kwargs):  # pylint: disable=W0613
    if instance.satellite_entry.status == 're-entered':
        transmitters = instance.transmitters.exclude(status="inactive")
        new_transm = None
        for transmitter in transmitters:
            new_transm = transmitter
            new_transm.id = None
            new_transm.status = "inactive"
            new_transm.created = now()
            new_transm.reviewed = now()
            new_transm.approved = True
            new_transm.citation = "Satellite decayed"
            if instance.satellite_entry and instance.satellite_entry.reviewer:
                new_transm.reviewer = instance.satellite_entry.reviewer
                new_transm.created_by = instance.satellite_entry.reviewer
            else:
                new_transm.reviewer = None
                new_transm.created_by = None
            new_transm.save()


post_save.connect(_invalidate_api_cache, sender=Satellite, weak=False)
post_save.connect(_invalidate_api_cache, sender=TransmitterEntry, weak=False)
post_save.connect(_invalidate_api_cache, sender=LatestTleSet, weak=False)
post_save.connect(_invalidate_api_cache, sender=Mode, weak=False)
post_delete.connect(_invalidate_api_cache, sender=Mode, weak=False)
post_save.connect(_inactivate_transmitters_on_sat_reentry, sender=Satellite, weak=False)
post_save.connect(_remove_latest_tle_set, sender=Satellite, weak=False)
post_save.connect(_extract_network_obs_id, sender=Artifact, weak=False)
