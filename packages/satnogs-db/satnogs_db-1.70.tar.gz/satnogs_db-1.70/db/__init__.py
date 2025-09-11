"""The core django app for SatNOGS DB"""
from .celery import APP as celery_app  # noqa

__all__ = ['celery_app']

from . import _version

__version__ = _version.get_versions()['version']
