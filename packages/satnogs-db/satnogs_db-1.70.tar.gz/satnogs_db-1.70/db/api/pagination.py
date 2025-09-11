"""
Custom pagination classes for REST framework
"""
from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response


class LinkedHeaderPageNumberPagination(PageNumberPagination):
    """
    This overrides the default PageNumberPagination so that it only
    returns the results as an array, not the pagination controls
    (eg number of results, etc)
    """
    page_size = 25

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        link = ''
        if next_url is not None and previous_url is not None:
            link = '<{next_url}>; rel="next", <{previous_url}>; rel="prev"'
        elif next_url is not None:
            link = '<{next_url}>; rel="next"'
        elif previous_url is not None:
            link = '<{previous_url}>; rel="prev"'
        link = link.format(next_url=next_url, previous_url=previous_url)
        headers = {'Link': link} if link else {}
        return Response(data, headers=headers)


class CursorPaginationWithLinkHeader(CursorPagination):
    """
    The default cursor pagination by django-rest-framework, but additionally
    the next/prev link is provided via the HTTP "Link" header.

    The next/prev keys in the response body are kept for backward-compatibility
    with existing API clients.
    """

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        if next_url is not None and previous_url is not None:
            link = '<{next_url}>; rel="next", <{previous_url}>; rel="prev"'
        elif next_url is not None:
            link = '<{next_url}>; rel="next"'
        elif previous_url is not None:
            link = '<{previous_url}>; rel="prev"'
        else:
            link = ""
        link = link.format(next_url=next_url, previous_url=previous_url)

        return Response(
            data={
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data,
            },
            headers={"Link": link} if link else {},
        )


class DemodDataCursorPagination(CursorPaginationWithLinkHeader):
    """
    This overrides the default CursorPagination for Telemetry endpoint
    """
    page_size = 25
    ordering = '-timestamp'
