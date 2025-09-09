"""
DRF Auto-REST: PostgREST-like system for Django REST Framework

This package provides automatic REST API generation from Django models
with advanced querying capabilities similar to PostgREST.
"""

from .viewsets import AutoRestViewSet
from .serializers import AutoRestSerializer
from .routers import AutoRestRouter

__all__ = [
    "AutoRestViewSet",
    "AutoRestSerializer",
    "AutoRestRouter",
]
