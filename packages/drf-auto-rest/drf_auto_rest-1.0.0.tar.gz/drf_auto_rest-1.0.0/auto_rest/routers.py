"""
Auto-REST Routers

Automatic model discovery and viewset registration.
"""

from rest_framework.routers import DefaultRouter
from django.apps import apps
from django.conf import settings
from django.db import models
from django.urls import path

from .viewsets import create_viewset_for_model

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


class AutoRestSpectacularAPIView(SpectacularAPIView):
    # generator_class = "drf_spectacular.generators.SchemaGenerator"
    custom_settings = {
        "TITLE": "DRF Auto-REST API",
        "DESCRIPTION": """
    ## PostgREST-like API for Django REST Framework

    A powerful Django REST Framework extension that automatically generates PostgREST-like APIs from your Django models. 
    Get advanced querying, filtering, aggregation, and relationship embedding with zero boilerplate code.

    ### 🚀 Key Features

    - **Zero Configuration APIs**: Automatic model discovery and REST endpoint generation
    - **Advanced PostgREST Querying**: Rich operators (`eq`, `gt`, `like`, `in`, `range`, `is.null`)
    - **Complex Logical Operations**: `OR` and `NOT` conditions for sophisticated filtering
    - **Business Intelligence**: Aggregation functions (`count()`, `sum()`, `avg()`, `min()`, `max()`) with grouping
    - **Relationship Embedding**: Include related data with automatic query optimization
    - **Flexible Pagination**: Support for both PostgREST and Django pagination styles

    ### 📊 Query Examples

    #### Basic Filtering
    - Products over $500: `?price=gt.500`
    - Active products: `?is_active=eq.true`
    - Pattern matching: `?name=like.*laptop*`

    #### Complex Logical Operations
    - OR logic: `?or=(price.lt.100,is_featured.eq.true)`
    - NOT logic: `?not.is_featured=eq.true`

    #### Aggregation & Analytics
    - Count all: `?select=count()`
    - Group by category: `?select=count(),avg(price)&group_by=category`
    - Having clause: `?select=count()&group_by=category&having=count.gt.5`

    #### Relationship Embedding
    - Embed related data: `?embed=category,reviews`
    - Field selection: `?select=name,price&embed=category`

    ### 🔍 Supported Operators

    | Operator | Example | Description |
    |----------|---------|-------------|
    | `eq` | `?status=eq.published` | Equals |
    | `neq` | `?status=neq.draft` | Not equals |
    | `gt/gte` | `?price=gt.100` | Greater than (or equal) |
    | `lt/lte` | `?price=lt.1000` | Less than (or equal) |
    | `like/ilike` | `?name=like.*laptop*` | Pattern matching |
    | `in` | `?id=in.(1,2,3)` | Value in list |
    | `range` | `?price=range.[100,500]` | Value in range |
    | `is` | `?description=is.null` | Null/boolean check |
    | `or` | `?or=(cond1,cond2)` | Logical OR |
    | `not` | `?not.field=value` | Logical NOT |

    ### 📄 Special Parameters

    | Parameter | Description | Example |
    |-----------|-------------|---------|
    | `select` | Field selection | `?select=name,price` |
    | `embed` | Relationship embedding | `?embed=category,reviews` |
    | `order` | Sorting | `?order=price.desc,name.asc` |
    | `group_by` | Aggregation grouping | `?group_by=category` |
    | `having` | Aggregation filtering | `?having=count.gt.5` |
    | `limit/offset` | Pagination | `?limit=10&offset=20` |
    | `page/page_size` | Django pagination | `?page=2&page_size=25` |

    Transform your Django models into powerful APIs with zero boilerplate! 🚀
    """,
        "VERSION": "1.0.0",
        "COMPONENT_SPLIT_REQUEST": True,
        "SCHEMA_PATH_PREFIX": "/api/",
        # Custom extensions for Auto-REST features
        "POSTPROCESSING_HOOKS": [
            "auto_rest.openapi.preprocess_auto_rest_operations",
            "auto_rest.openapi.postprocess_auto_rest_schema",
        ],
        "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    }


class AutoRestRouter(DefaultRouter):
    """
    Router that automatically discovers models and registers appropriate viewsets.

    Features:
    - Automatic model discovery
    - Configurable inclusion/exclusion
    - Custom viewset mapping
    - URL pattern generation
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_rest_config = getattr(settings, "AUTO_REST", {})
        self._auto_registered_models = set()

    def auto_register_models(self, app_labels=None):
        """
        Automatically register viewsets for all discovered models.

        Args:
            app_labels: List of app labels to include. If None, all apps are considered.
        """
        models_to_register = self._discover_models(app_labels)

        for model_class in models_to_register:
            self._register_model(model_class)

    def _discover_models(self, app_labels=None):
        """
        Discover models that should be auto-registered.
        """
        models_to_register = []

        # Get configuration
        allowed_models = self.auto_rest_config.get("ALLOWED_MODELS", [])
        excluded_models = self.auto_rest_config.get("EXCLUDED_MODELS", [])

        # If allowed_models is specified, only include those
        if allowed_models:
            for model_spec in allowed_models:
                model_class = self._get_model_from_spec(model_spec)
                if model_class:
                    models_to_register.append(model_class)
            return models_to_register

        # Otherwise, discover all models
        for app_config in apps.get_app_configs():
            # Skip if app_labels specified and this app not included
            if app_labels and app_config.label not in app_labels:
                continue

            for model_class in app_config.get_models():
                model_spec = f"{app_config.label}.{model_class.__name__}"

                # Skip excluded models
                if model_spec in excluded_models:
                    continue

                # Skip abstract models
                if model_class._meta.abstract:
                    continue

                # Skip proxy models (for now)
                if model_class._meta.proxy:
                    continue

                models_to_register.append(model_class)

        return models_to_register

    def _get_model_from_spec(self, model_spec):
        """
        Get a model class from a string specification like 'app.ModelName'.
        """
        try:
            app_label, model_name = model_spec.split(".")
            return apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            return None

    def _register_model(self, model_class):
        """
        Register a viewset for a specific model.
        """
        if model_class in self._auto_registered_models:
            return

        # Create viewset for the model
        viewset_class = self._create_viewset_for_model(model_class)

        # Generate URL basename
        basename = self._get_basename_for_model(model_class)

        # Register with router
        self.register(basename, viewset_class, basename=basename)

        # Track that we've registered this model
        self._auto_registered_models.add(model_class)

    def _create_viewset_for_model(self, model_class):
        """
        Create a viewset class for a model.
        """
        # Check if model has custom Auto-REST configuration
        auto_rest_meta = getattr(model_class, "AutoRestMeta", None)
        viewset_attrs = {}

        if auto_rest_meta:
            # Apply custom configuration
            if hasattr(auto_rest_meta, "permission_classes"):
                viewset_attrs["permission_classes"] = auto_rest_meta.permission_classes

            if hasattr(auto_rest_meta, "filterable_fields"):
                viewset_attrs["filterable_fields"] = auto_rest_meta.filterable_fields

            if hasattr(auto_rest_meta, "searchable_fields"):
                viewset_attrs["search_fields"] = auto_rest_meta.searchable_fields

            if hasattr(auto_rest_meta, "orderable_fields"):
                viewset_attrs["ordering_fields"] = auto_rest_meta.orderable_fields

        return create_viewset_for_model(model_class, **viewset_attrs)

    def _get_basename_for_model(self, model_class):
        """
        Generate a URL basename for a model.
        """
        # Convert CamelCase to lowercase with underscores
        model_name = model_class.__name__
        basename = ""
        for i, char in enumerate(model_name):
            if char.isupper() and i > 0:
                basename += "_"
            basename += char.lower()

        # Include app label to avoid conflicts
        app_label = model_class._meta.app_label
        return f"{app_label}_{basename}"

    def register_model(self, model_class, viewset_class=None, **kwargs):
        """
        Manually register a specific model with optional custom viewset.

        Args:
            model_class: The Django model class
            viewset_class: Custom viewset class (optional)
            **kwargs: Additional arguments for registration
        """
        if viewset_class is None:
            viewset_class = self._create_viewset_for_model(model_class)

        basename = kwargs.get("basename", self._get_basename_for_model(model_class))
        prefix = kwargs.get("prefix", basename)

        self.register(prefix, viewset_class, basename=basename)
        self._auto_registered_models.add(model_class)

    @property
    def documentation_urls(self):
        """
        Return URL patterns for Auto-REST documentation.

        Returns:
            List of URL patterns for API documentation (schema, swagger, redoc).
            Returns empty list if drf-spectacular is not installed.
        """
        # The key fix: Pass patterns directly to AutoRestSpectacularAPIView
        # This limits schema generation to ONLY Auto-REST patterns

        schema_view = AutoRestSpectacularAPIView.as_view(
            patterns=self.urls,  # ONLY Auto-REST patterns - this is the key!
        )

        return [
            path("api/schema/", schema_view, name="auto-rest-schema"),
            path(
                "api/docs/",
                SpectacularSwaggerView.as_view(url_name="auto-rest-schema"),
                name="auto-rest-docs",
            ),
            path(
                "api/redoc/",
                SpectacularRedocView.as_view(url_name="auto-rest-schema"),
                name="auto-rest-redoc",
            ),
        ]

    @property
    def all_urls(self):
        """
        Return both API and documentation URLs.

        Returns:
            List combining API endpoints and documentation URLs.
        """
        return self.urls + self.documentation_urls


def create_auto_router():
    """
    Convenience function to create and configure an AutoRestRouter.
    """
    router = AutoRestRouter()
    router.auto_register_models()
    return router
