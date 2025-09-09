"""
Auto-REST Pagination

Custom pagination classes that support PostgREST-like pagination parameters.
"""

from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict
from django.conf import settings


class AutoRestPagination(PageNumberPagination):
    """
    Custom pagination class that supports both Django-style and PostgREST-style parameters.

    Supports:
    - ?page=2&page_size=20 (Django style)
    - ?limit=20&offset=40 (PostgREST style)
    """

    page_size_query_param = "page_size"
    max_page_size = 100

    def __init__(self):
        super().__init__()
        # Get configuration from settings
        auto_rest_config = getattr(settings, "AUTO_REST", {})
        self.page_size = auto_rest_config.get("PAGE_SIZE", 20)
        self.max_page_size = auto_rest_config.get("MAX_PAGE_SIZE", 100)

    def get_page_size(self, request):
        """
        Get the page size from request parameters.
        Supports both 'page_size' and 'limit' parameters.
        """
        # Try PostgREST-style 'limit' parameter first
        if "limit" in request.query_params:
            try:
                limit = int(request.query_params["limit"])
                return min(limit, self.max_page_size)
            except (ValueError, TypeError):
                pass

        # Fall back to Django-style pagination
        return super().get_page_size(request)

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset and return a page of results.
        Supports PostgREST-style offset parameter.
        """
        # Handle PostgREST-style offset pagination
        if "offset" in request.query_params and "limit" in request.query_params:
            return self._paginate_with_offset(queryset, request)

        # Use standard page-based pagination
        return super().paginate_queryset(queryset, request, view)

    def _paginate_with_offset(self, queryset, request):
        """
        Handle PostgREST-style offset/limit pagination.
        """
        try:
            offset = int(request.query_params.get("offset", 0))
            limit = int(request.query_params.get("limit", self.page_size))

            # Enforce max page size
            limit = min(limit, self.max_page_size)

            # Store pagination info for response
            self.offset = offset
            self.limit = limit
            self.count = queryset.count()

            # Return the slice of results
            return list(queryset[offset : offset + limit])

        except (ValueError, TypeError):
            return super().paginate_queryset(queryset, request)

    def get_paginated_response(self, data):
        """
        Return a paginated response.
        """
        # If using offset/limit pagination
        if hasattr(self, "offset"):
            return Response(
                OrderedDict(
                    [
                        ("count", self.count),
                        ("offset", self.offset),
                        ("limit", self.limit),
                        ("results", data),
                    ]
                )
            )

        # Use standard page-based response
        return super().get_paginated_response(data)


class AutoRestLimitOffsetPagination(LimitOffsetPagination):
    """
    Alternative pagination class using limit/offset by default.
    """

    default_limit = 20
    max_limit = 100

    def __init__(self):
        super().__init__()
        # Get configuration from settings
        auto_rest_config = getattr(settings, "AUTO_REST", {})
        self.default_limit = auto_rest_config.get("PAGE_SIZE", 20)
        self.max_limit = auto_rest_config.get("MAX_PAGE_SIZE", 100)


class AutoRestCursorPagination(PageNumberPagination):
    """
    Cursor-based pagination for very large datasets.
    This is a placeholder for future implementation.
    """

    pass
