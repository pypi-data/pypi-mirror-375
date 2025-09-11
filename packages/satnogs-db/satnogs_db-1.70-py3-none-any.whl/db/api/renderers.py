"""SatNOGS DB django rest framework API custom renderers"""
# pylint:disable=too-few-public-methods
from rest_framework.renderers import BaseRenderer, BrowsableAPIRenderer, JSONRenderer

from db.base.structured_data import get_structured_data


class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):
    """Renders the browsable api, but excludes the forms."""

    def show_form_for_method(self, view, method, request, obj):
        """Return True in GET request to display filter form."""
        return False


class TLERenderer(BaseRenderer):
    """ Renderer which serializes 3le format """

    media_type = 'text/plain'
    format = '3le'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """ Render `data` into 3le, returning a bytestring. """
        tle_lines = []
        for tle in data:
            tle_lines.extend([tle["tle0"][:25], tle["tle1"], tle["tle2"]])
        return "\n".join(tle_lines).encode()


class JSONLDRenderer(JSONRenderer):
    """ Renderer which serializes to JSONLD. """

    media_type = 'application/ld+json'
    format = 'json-ld'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """ Render `data` into JSONLD, returning a bytestring. """
        if renderer_context['response'].exception:
            return super().render(data, accepted_media_type, renderer_context)

        structured_data = get_structured_data(renderer_context['view'].basename, data)
        jsonld = structured_data.get_jsonld()
        return super().render(jsonld, accepted_media_type, renderer_context)


class BrowserableJSONLDRenderer(BrowsableAPIRenderer):
    """ Renderer for Browserable API with JSONLD format. """
    format = 'browse-json-ld'

    def get_default_renderer(self, view):
        return JSONLDRenderer()
