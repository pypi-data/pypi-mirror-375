"""
Auto-REST ViewSets

Provides base viewset classes that automatically generate REST APIs
with PostgREST-like querying capabilities.
"""

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.conf import settings
from django.apps import apps
from django.db import models
from django.db.models import Count, Sum, Avg, Min, Max, Q
import re

from .serializers import AutoRestSerializer
from .filters import AutoRestFilterBackend
from .pagination import AutoRestPagination
from .openapi import AutoRestAutoSchema


class AutoRestViewSet(viewsets.ModelViewSet):
    """
    Auto-REST ViewSet providing PostgREST-like querying capabilities.

    Features:
    - Advanced filtering with PostgREST operators
    - Field selection and relationship embedding
    - Aggregation functions and grouping
    - Complex logical operations (OR, NOT)
    - Automatic query optimization
    """

    schema = AutoRestAutoSchema()
    serializer_class = None
    auto_rest_config = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auto_rest_config = getattr(settings, "AUTO_REST", {})

    def get_serializer_class(self):
        """
        Return the serializer class based on the model and request parameters.
        """
        if not hasattr(self, "model"):
            # If no model is set, fall back to a basic serializer
            return super().get_serializer_class()

        # Use our dynamic serializer factory
        return AutoRestSerializer.for_model(
            self.model, request=getattr(self, "request", None)
        )

    def get_queryset(self):
        """
        Get the base queryset for this viewset.
        """
        if not hasattr(self, "queryset") or self.queryset is None:
            model_class = getattr(self, "model", None)
            if model_class:
                queryset = model_class.objects.all()
            else:
                raise ValueError("Either 'queryset' or 'model' must be specified")
        else:
            queryset = self.queryset.all()

        # Optimize queryset for embedded relationships
        queryset = self._optimize_queryset_for_embeds(queryset)

        return queryset

    def _optimize_queryset_for_embeds(self, queryset):
        """
        Optimize queryset by adding select_related and prefetch_related
        for embedded relationships.
        """
        if not hasattr(self, "request") or not self.request:
            return queryset

        embed_param = self.request.query_params.get("embed", "")
        if not embed_param:
            return queryset

        embed_fields = [
            field.strip() for field in embed_param.split(",") if field.strip()
        ]
        if not embed_fields:
            return queryset

        model_class = queryset.model
        select_related_fields = []
        prefetch_related_fields = []

        for embed_field in embed_fields:
            # Check if this field should be embedded (permission check)
            if hasattr(model_class, "AutoRestMeta"):
                auto_rest_meta = model_class.AutoRestMeta
                if hasattr(auto_rest_meta, "embed_allowed"):
                    if embed_field not in auto_rest_meta.embed_allowed:
                        continue
                
                # Also check if this field is excluded
                if hasattr(auto_rest_meta, "exclude_fields"):
                    if embed_field in auto_rest_meta.exclude_fields:
                        continue

            try:
                # Try to get as direct field first
                field = model_class._meta.get_field(embed_field)

                if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                    # Use select_related for forward relationships
                    select_related_fields.append(embed_field)
                elif isinstance(field, models.ManyToManyField):
                    # Use prefetch_related for many-to-many
                    prefetch_related_fields.append(embed_field)

            except models.FieldDoesNotExist:
                # Check for reverse relationships
                for related_object in model_class._meta.related_objects:
                    if related_object.get_accessor_name() == embed_field:
                        # Use prefetch_related for reverse relationships
                        prefetch_related_fields.append(embed_field)
                        break

        # Apply optimizations
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)

        if prefetch_related_fields:
            queryset = queryset.prefetch_related(*prefetch_related_fields)

        return queryset

    def filter_queryset(self, queryset):
        """
        Apply filters to the queryset.
        """
        # Get filter backends from settings or use default
        filter_backends = self.auto_rest_config.get(
            "DEFAULT_FILTER_BACKENDS", [AutoRestFilterBackend]
        )

        for backend_class in filter_backends:
            if isinstance(backend_class, str):
                # Import the backend if it's a string
                module_name, class_name = backend_class.rsplit(".", 1)
                module = __import__(module_name, fromlist=[class_name])
                backend_class = getattr(module, class_name)

            backend = backend_class()
            queryset = backend.filter_queryset(self.request, queryset, self)

        return queryset

    def _get_excluded_fields(self, model_class):
        """
        Get fields that should be excluded based on model configuration.
        
        Args:
            model_class: The Django model class
            
        Returns:
            List of field names to exclude
        """
        excluded_fields = []
        
        if model_class and hasattr(model_class, 'AutoRestMeta'):
            auto_rest_meta = model_class.AutoRestMeta
            if hasattr(auto_rest_meta, 'exclude_fields'):
                excluded_fields.extend(auto_rest_meta.exclude_fields)
        
        return excluded_fields

    def _get_available_fields(self, model_class, excluded_fields):
        """
        Get list of available fields for the model (excluding the excluded ones).
        
        Args:
            model_class: The Django model class
            excluded_fields: List of fields to exclude
            
        Returns:
            List of available field names
        """
        if not model_class:
            return []
        
        # Get all model fields
        all_fields = []
        
        # Add regular model fields
        for field in model_class._meta.get_fields():
            if hasattr(field, 'name'):
                all_fields.append(field.name)
        
        # Add related field names (reverse relationships)
        for related_object in model_class._meta.related_objects:
            accessor_name = related_object.get_accessor_name()
            if accessor_name:
                all_fields.append(accessor_name)
        
        # Filter out excluded fields
        available_fields = [f for f in all_fields if f not in excluded_fields]
        
        return available_fields

    def list(self, request, *args, **kwargs):
        """
        Handle list requests with potential aggregation.
        """
        # Check if this is an aggregation query
        if self._is_aggregation_query(request):
            return self._handle_aggregation(request)

        # Standard list handling
        return super().list(request, *args, **kwargs)

    def _is_aggregation_query(self, request):
        """
        Check if the request contains aggregation parameters.
        """
        select_param = request.query_params.get("select", "")
        group_by_param = request.query_params.get("group_by", "")

        # Check for aggregation functions in select
        aggregation_functions = ["count()", "sum(", "avg(", "min(", "max("]
        has_aggregation = any(
            func in select_param.lower() for func in aggregation_functions
        )

        return has_aggregation or group_by_param

    def _handle_aggregation(self, request):
        """
        Handle aggregation queries with full PostgREST-like functionality.

        Supports:
        - ?select=count() - Total count
        - ?select=count()&group_by=category - Count per category
        - ?select=sum(price),avg(price)&group_by=category - Multiple aggregations
        - ?select=count()&group_by=category&having=count.gt.5 - Having clause
        """
        try:
            # Get base queryset and apply filters
            queryset = self.filter_queryset(self.get_queryset())

            select_param = request.query_params.get("select", "")
            group_by_param = request.query_params.get("group_by", "")
            having_param = request.query_params.get("having", "")

            # Parse aggregation functions
            aggregations = self._parse_aggregations(select_param)

            if not aggregations:
                return Response(
                    {
                        "error": "No valid aggregation functions found",
                        "message": "Use functions like count(), sum(field), avg(field), min(field), max(field)",
                    },
                    status=400,
                )

            # Handle grouping
            if group_by_param:
                result = self._handle_grouped_aggregation(
                    queryset, aggregations, group_by_param, having_param
                )
            else:
                result = self._handle_simple_aggregation(queryset, aggregations)

            return Response(result)

        except Exception as e:
            return Response(
                {"error": "Aggregation query failed", "message": str(e)}, status=400
            )

    def _parse_aggregations(self, select_param):
        """
        Parse aggregation functions from select parameter.

        Examples:
        - count() -> [{'func': 'count', 'field': None, 'alias': 'count'}]
        - sum(price) -> [{'func': 'sum', 'field': 'price', 'alias': 'sum_price'}]
        - count(),avg(price) -> [{'func': 'count', ...}, {'func': 'avg', ...}]
        """
        aggregations = []

        # Get excluded fields from model configuration
        model_class = getattr(self, 'model', None)
        excluded_fields = self._get_excluded_fields(model_class) if model_class else []

        # Split by comma and process each function
        parts = [part.strip() for part in select_param.split(",")]

        for part in parts:
            # Match aggregation function pattern: func(field) or func()
            match = re.match(r"(\w+)\(([^)]*)\)", part)
            if match:
                func_name = match.group(1).lower()
                field_name = match.group(2).strip() or None

                # Validate function name
                if func_name in ["count", "sum", "avg", "min", "max"]:
                    # Check if field is excluded (skip count() as it doesn't use specific fields)
                    if field_name and field_name in excluded_fields:
                        # Raise an error instead of silently skipping
                        available_fields = self._get_available_fields(model_class, excluded_fields)
                        raise ValueError(
                            f"Cannot resolve keyword '{field_name}' into field. "
                            f"Choices are: {', '.join(sorted(available_fields))}"
                        )

                    # Generate alias
                    if field_name:
                        alias = f"{func_name}_{field_name}"
                    else:
                        alias = func_name

                    aggregations.append(
                        {"func": func_name, "field": field_name, "alias": alias}
                    )

        return aggregations

    def _handle_simple_aggregation(self, queryset, aggregations):
        """
        Handle aggregation without grouping.
        Returns a single result object.
        """
        agg_kwargs = {}

        for agg in aggregations:
            if agg["func"] == "count":
                agg_kwargs[agg["alias"]] = Count("*")
            elif agg["func"] == "sum":
                if agg["field"]:
                    agg_kwargs[agg["alias"]] = Sum(agg["field"])
            elif agg["func"] == "avg":
                if agg["field"]:
                    agg_kwargs[agg["alias"]] = Avg(agg["field"])
            elif agg["func"] == "min":
                if agg["field"]:
                    agg_kwargs[agg["alias"]] = Min(agg["field"])
            elif agg["func"] == "max":
                if agg["field"]:
                    agg_kwargs[agg["alias"]] = Max(agg["field"])

        result = queryset.aggregate(**agg_kwargs)
        return [result]  # Return as list for consistency

    def _handle_grouped_aggregation(
        self, queryset, aggregations, group_by_param, having_param
    ):
        """
        Handle aggregation with grouping.
        Returns a list of grouped results.
        """
        # Parse group_by fields
        group_fields = [field.strip() for field in group_by_param.split(",")]

        # Apply grouping
        queryset = queryset.values(*group_fields)

        # Add aggregations
        agg_kwargs = {}
        for agg in aggregations:
            if agg["func"] == "count":
                agg_kwargs[agg["alias"]] = Count("*")
            elif agg["func"] == "sum":
                if agg["field"]:
                    agg_kwargs[agg["alias"]] = Sum(agg["field"])
            elif agg["func"] == "avg":
                if agg["field"]:
                    agg_kwargs[agg["alias"]] = Avg(agg["field"])
            elif agg["func"] == "min":
                if agg["field"]:
                    agg_kwargs[agg["alias"]] = Min(agg["field"])
            elif agg["func"] == "max":
                if agg["field"]:
                    agg_kwargs[agg["alias"]] = Max(agg["field"])

        queryset = queryset.annotate(**agg_kwargs)

        # Apply having clause if provided
        if having_param:
            queryset = self._apply_having_clause(queryset, having_param, aggregations)

        # Order by group fields for consistent results
        queryset = queryset.order_by(*group_fields)

        return list(queryset)

    def _apply_having_clause(self, queryset, having_param, aggregations):
        """
        Apply HAVING clause to aggregated queryset.

        Example: ?having=count.gt.5
        """
        try:
            # Parse having condition: alias.operator.value
            if "." in having_param:
                parts = having_param.split(".")
                if len(parts) >= 3:
                    alias = parts[0]
                    operator = parts[1]
                    value = ".".join(parts[2:])

                    # Find the aggregation alias
                    agg_field = None
                    for agg in aggregations:
                        if agg["alias"] == alias:
                            agg_field = alias
                            break

                    if agg_field:
                        # Convert value to appropriate type
                        try:
                            if "." in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except ValueError:
                            pass  # Keep as string

                        # Apply having filter
                        if operator == "gt":
                            queryset = queryset.filter(**{f"{agg_field}__gt": value})
                        elif operator == "gte":
                            queryset = queryset.filter(**{f"{agg_field}__gte": value})
                        elif operator == "lt":
                            queryset = queryset.filter(**{f"{agg_field}__lt": value})
                        elif operator == "lte":
                            queryset = queryset.filter(**{f"{agg_field}__lte": value})
                        elif operator == "eq":
                            queryset = queryset.filter(**{f"{agg_field}__exact": value})
                        elif operator == "neq":
                            queryset = queryset.exclude(
                                **{f"{agg_field}__exact": value}
                            )

        except Exception:
            # Skip invalid having clauses
            pass

        return queryset


class AutoRestReadOnlyViewSet(AutoRestViewSet):
    """
    Read-only version of AutoRestViewSet for immutable data access.

    Provides all the querying capabilities of AutoRestViewSet but restricts
    HTTP methods to read-only operations (GET, HEAD, OPTIONS).

    Features:
    - All AutoRestViewSet querying capabilities
    - Advanced filtering, aggregation, and embedding
    - Read-only access (no create, update, delete)
    - Custom OpenAPI documentation
    """

    schema = AutoRestAutoSchema()
    http_method_names = ["get", "head", "options"]


def create_viewset_for_model(model_class, **viewset_attrs):
    """
    Factory function to create a viewset for a specific model.
    """
    # Get permission classes as actual classes, not strings
    permission_classes = []
    default_permissions = getattr(settings, "AUTO_REST", {}).get(
        "DEFAULT_PERMISSION_CLASSES",
        ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
    )

    for perm in default_permissions:
        if isinstance(perm, str):
            # Import the permission class
            try:
                module_name, class_name = perm.rsplit(".", 1)
                module = __import__(module_name, fromlist=[class_name])
                permission_classes.append(getattr(module, class_name))
            except (ImportError, AttributeError):
                # Fall back to a safe default
                permission_classes.append(IsAuthenticatedOrReadOnly)
        else:
            permission_classes.append(perm)

    attrs = {
        "model": model_class,
        "queryset": model_class.objects.all(),
        "filter_backends": [AutoRestFilterBackend],
        "pagination_class": AutoRestPagination,
        "permission_classes": permission_classes,
        "schema": AutoRestAutoSchema(),  # Custom OpenAPI schema
        **viewset_attrs,
    }

    class_name = f"{model_class.__name__}AutoRestViewSet"

    base_class = AutoRestViewSet
    if hasattr(model_class, "AutoRestMeta"):
        auto_rest_meta = model_class.AutoRestMeta
        if getattr(auto_rest_meta, "read_only", False):
            base_class = AutoRestReadOnlyViewSet

    return type(class_name, (base_class,), attrs)
