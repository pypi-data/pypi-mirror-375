"""
Auto-REST Filter Backend

Provides PostgREST-like filtering with advanced query operators.
"""

import re
import json
from django.db import models
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ValidationError


class AutoRestFilterBackend(BaseFilterBackend):
    """
    Filter backend that implements PostgREST-like query operators.

    Supported operators:
    - eq: equals
    - neq: not equals
    - gt/gte: greater than / greater than or equal
    - lt/lte: less than / less than or equal
    - like/ilike: pattern matching (case sensitive/insensitive)
    - in: in list
    - is: is null/true/false
    - range: in range [low,high]
    - or: logical OR
    - not: logical NOT
    """

    RESERVED_PARAMS = {
        "select",
        "embed",
        "order",
        "limit",
        "offset",
        "page",
        "page_size",
        "group_by",
        "having",
        "or",
        "not",
    }

    def filter_queryset(self, request, queryset, view):
        """
        Apply filters to the queryset based on query parameters.
        """
        if not request:
            return queryset

        # Handle logical operators first
        queryset = self._apply_logical_filters(request, queryset)

        # Apply regular filters
        for param_name, param_value in request.query_params.items():
            if param_name not in self.RESERVED_PARAMS and param_value:
                queryset = self._apply_filter(queryset, param_name, param_value)

        # Apply ordering
        order_param = request.query_params.get("order")
        if order_param:
            queryset = self._apply_ordering(queryset, order_param)

        return queryset

    def _apply_logical_filters(self, request, queryset):
        """
        Apply logical operators (OR, NOT) to the queryset.
        """
        # Handle OR filters: ?or=(field1.eq.value1,field2.eq.value2)
        or_param = request.query_params.get("or")
        if or_param:
            queryset = self._apply_or_filter(queryset, or_param)

        # Handle NOT filters: ?not.field.eq.value
        not_filters = []
        for param_name, param_value in request.query_params.items():
            if param_name.startswith("not."):
                # Extract field name after 'not.'
                field_part = param_name[4:]  # Remove 'not.' prefix
                not_filters.append((field_part, param_value))

        for field_part, param_value in not_filters:
            field_name, operator, value = self._parse_filter_param(
                field_part, param_value
            )
            filter_kwargs = self._build_filter_kwargs(field_name, operator, value)
            if filter_kwargs:
                # Apply NOT logic using exclude
                queryset = queryset.exclude(**filter_kwargs)

        return queryset

    def _apply_or_filter(self, queryset, or_param):
        """
        Apply OR logic to multiple filters.
        Format: ?or=(field1.eq.value1,field2.eq.value2,field3.gt.100)
        """
        if not or_param.startswith("(") or not or_param.endswith(")"):
            return queryset

        # Parse OR conditions
        conditions_str = or_param[1:-1]  # Remove parentheses
        conditions = [cond.strip() for cond in conditions_str.split(",")]

        q_objects = []
        for condition in conditions:
            if "." in condition:
                # Split into parts: field.operator.value
                parts = condition.split(".")
                if len(parts) >= 3:
                    field_name = parts[0]
                    operator = parts[1]
                    value = ".".join(parts[2:])  # Handle values with dots

                    filter_kwargs = self._build_filter_kwargs(
                        field_name, operator, value
                    )
                    if filter_kwargs:
                        q_objects.append(Q(**filter_kwargs))

        # Apply OR logic
        if q_objects:
            combined_q = q_objects[0]
            for q_obj in q_objects[1:]:
                combined_q |= q_obj
            queryset = queryset.filter(combined_q)

        return queryset

    def _apply_filter(self, queryset, param_name, param_value):
        """
        Apply a single filter to the queryset.
        """
        try:
            field_name, operator, value = self._parse_filter_param(
                param_name, param_value
            )
            filter_kwargs = self._build_filter_kwargs(field_name, operator, value)

            if filter_kwargs:
                queryset = queryset.filter(**filter_kwargs)

        except (ValueError, TypeError, ValidationError):
            # Skip invalid filters gracefully
            pass

        return queryset

    def _parse_filter_param(self, param_name, param_value):
        """
        Parse a filter parameter to extract field name, operator, and value.

        Supports both PostgREST styles:
        - ?field=operator.value (e.g., ?name=eq.John)
        - ?field.operator=value (e.g., ?name.eq=John)
        - ?field=value (defaults to eq operator)

        Examples:
        - price=gt.100 -> ('price', 'gt', '100')
        - price.gt=100 -> ('price', 'gt', '100')
        - name=like.*test* -> ('name', 'like', '*test*')
        - status=pending -> ('status', 'eq', 'pending')
        """
        # Style 1: Operator in parameter name: ?field.operator=value
        if "." in param_name:
            parts = param_name.split(".")
            if len(parts) >= 2:
                field_name = parts[0]
                operator = parts[1]
                # Handle cases where field name might contain dots (rare)
                if len(parts) > 2:
                    # If there are more parts, it might be a field name with dots
                    # For now, assume the last part is the operator
                    field_name = ".".join(parts[:-1])
                    operator = parts[-1]
                return field_name, operator, param_value

        # Style 2: Operator in parameter value: ?field=operator.value
        if "." in param_value:
            parts = param_value.split(".", 1)  # Split only on first dot
            if len(parts) == 2:
                operator, value = parts
                # Check if this looks like a valid operator
                valid_operators = {
                    "eq",
                    "neq",
                    "gt",
                    "gte",
                    "lt",
                    "lte",
                    "like",
                    "ilike",
                    "in",
                    "is",
                    "range",
                }
                if operator in valid_operators:
                    return param_name, operator, value

        # Style 3: Default to equality if no operator specified
        return param_name, "eq", param_value

    def _build_filter_kwargs(self, field_name, operator, value):
        """
        Build Django ORM filter kwargs based on operator and value.
        """
        if operator == "eq":
            return {field_name: self._convert_value(value)}

        elif operator == "neq":
            return {f"{field_name}__ne": self._convert_value(value)}

        elif operator == "gt":
            return {f"{field_name}__gt": self._convert_value(value)}

        elif operator == "gte":
            return {f"{field_name}__gte": self._convert_value(value)}

        elif operator == "lt":
            return {f"{field_name}__lt": self._convert_value(value)}

        elif operator == "lte":
            return {f"{field_name}__lte": self._convert_value(value)}

        elif operator == "like":
            # Convert PostgREST wildcards to Django format
            django_pattern = value.replace("*", "")
            return {f"{field_name}__icontains": django_pattern}

        elif operator == "ilike":
            # Case-insensitive like (same as like in Django)
            django_pattern = value.replace("*", "")
            return {f"{field_name}__icontains": django_pattern}

        elif operator == "in":
            # Parse list values: in.(1,2,3)
            if value.startswith("(") and value.endswith(")"):
                list_values = [
                    self._convert_value(v.strip()) for v in value[1:-1].split(",")
                ]
                return {f"{field_name}__in": list_values}

        elif operator == "is":
            if value.lower() == "null":
                return {f"{field_name}__isnull": True}
            elif value.lower() == "true":
                return {field_name: True}
            elif value.lower() == "false":
                return {field_name: False}

        elif operator == "range":
            # Parse range values: range.[100,200]
            if value.startswith("[") and value.endswith("]"):
                try:
                    range_values = value[1:-1].split(",")
                    if len(range_values) == 2:
                        low_val = self._convert_value(range_values[0].strip())
                        high_val = self._convert_value(range_values[1].strip())
                        return {
                            f"{field_name}__gte": low_val,
                            f"{field_name}__lte": high_val,
                        }
                except (ValueError, IndexError):
                    pass

        # Return empty dict for unsupported operators
        return {}

    def _convert_value(self, value):
        """
        Convert string values to appropriate Python types.
        """
        if isinstance(value, str):
            # Try boolean conversion first
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            elif value.lower() == "null":
                return None

            # Try numeric conversion
            try:
                # Try integer first
                if "." not in value:
                    return int(value)
                else:
                    return float(value)
            except ValueError:
                # Return as string if conversion fails
                return value

        return value

    def _apply_ordering(self, queryset, order_param):
        """
        Apply ordering to the queryset.

        Examples:
        - order=created_at -> ORDER BY created_at ASC
        - order=price.desc -> ORDER BY price DESC
        - order=name.asc,price.desc -> ORDER BY name ASC, price DESC
        """
        order_fields = []

        for field_spec in order_param.split(","):
            field_spec = field_spec.strip()
            if not field_spec:
                continue

            if "." in field_spec:
                field_name, direction = field_spec.split(".", 1)
                if direction.lower() == "desc":
                    order_fields.append(f"-{field_name}")
                else:
                    order_fields.append(field_name)
            else:
                order_fields.append(field_spec)

        if order_fields:
            queryset = queryset.order_by(*order_fields)

        return queryset
