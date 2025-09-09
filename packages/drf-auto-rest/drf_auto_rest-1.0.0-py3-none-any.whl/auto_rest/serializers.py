"""
Auto-REST Serializers

Provides dynamic serializer generation based on models and request parameters.
"""

import hashlib
from rest_framework import serializers
from django.db import models
from django.core.exceptions import FieldDoesNotExist


class AutoRestSerializer(serializers.ModelSerializer):
    """
    Dynamic serializer that adapts based on request parameters.

    Features:
    - Field selection via ?select=field1,field2
    - Relationship embedding via ?embed=relation1,relation2
    - Automatic query optimization for embedded relationships
    """

    # Class-level cache to store serializer classes
    _serializer_cache = {}

    @classmethod
    def clear_cache(cls):
        """Clear the serializer cache. Useful for testing or development."""
        cls._serializer_cache.clear()

    @classmethod
    def for_model(cls, model_class, request=None, **kwargs):
        """
        Factory method to create a serializer for a specific model.

        Args:
            model_class: The Django model class
            request: The current request (optional)
            **kwargs: Additional serializer options

        Returns:
            A configured AutoRestSerializer class
        """
        # Parse request parameters
        selected_fields = None
        embed_fields = []

        if request:
            selected_fields = cls._parse_select_param(
                request.query_params.get("select", "")
            )
            embed_fields = cls._parse_embed_param(request.query_params.get("embed", ""))

        # Get excluded fields from model configuration
        excluded_fields = cls._get_excluded_fields(model_class)

        # Create cache key based on configuration
        cache_key_data = {
            "model": f"{model_class._meta.app_label}.{model_class.__name__}",
            "selected_fields": tuple(sorted(selected_fields))
            if selected_fields
            else None,
            "embed_fields": tuple(sorted(embed_fields)) if embed_fields else (),
            "excluded_fields": tuple(sorted(excluded_fields))
            if excluded_fields
            else (),
        }
        cache_key = str(sorted(cache_key_data.items()))

        # Check if we already have a serializer class for this configuration
        if cache_key in cls._serializer_cache:
            return cls._serializer_cache[cache_key]

        # Create dynamic Meta class based on exclusions
        meta_attrs = {"model": model_class}

        if excluded_fields and not selected_fields:
            # Use exclude when no specific fields selected but have exclusions
            meta_attrs["exclude"] = excluded_fields
        else:
            # Use fields (either selected fields or filtered selected fields)
            final_fields = cls._determine_final_fields(
                model_class, selected_fields, excluded_fields
            )
            meta_attrs["fields"] = final_fields

        # Create unique serializer class name based on configuration
        class_name_parts = [model_class.__name__, "AutoRest"]

        # Add simple suffixes for different configurations
        if selected_fields and embed_fields:
            class_name_parts.append("SelectEmbed")
        elif selected_fields:
            class_name_parts.append("Select")
        elif embed_fields:
            class_name_parts.append("Embed")
        else:
            # Default serializer - no suffix needed for cleaner names
            pass

        class_name = "".join(class_name_parts) + "Serializer"

        # Create the serializer class
        attrs = {
            "Meta": type("Meta", (), meta_attrs),
            "_embed_fields": embed_fields,
            "_model_class": model_class,
        }

        # Add embedded field serializers
        for embed_field in embed_fields:
            embed_attrs = cls._create_embed_fields(model_class, embed_field, request)
            attrs.update(embed_attrs)

        # Handle HashID fields - they require explicit declaration
        attrs = cls._handle_hashid_fields(model_class, attrs)

        # If we have embedded fields and selected fields, add them to the fields list
        if embed_fields and selected_fields:
            # Add embed fields to selected fields if not already present
            all_fields = list(selected_fields) if selected_fields else []
            for embed_field in embed_fields:
                if embed_field not in all_fields:
                    all_fields.append(embed_field)
            attrs["Meta"].fields = all_fields

        # Create and cache the serializer class
        serializer_class = type(class_name, (cls,), attrs)
        cls._serializer_cache[cache_key] = serializer_class

        return serializer_class

    @classmethod
    def _handle_hashid_fields(cls, model_class, attrs):
        """
        Detect and explicitly declare HashID fields in the serializer.

        HashID fields require explicit declaration when using ModelSerializer.
        """
        try:
            # Try to import HashIDField to check for HashID fields
            from hashid_field import HashidField, HashidAutoField
            from hashid_field.rest import HashidSerializerCharField
        except ImportError:
            # hashid_field not installed, skip this handling
            return attrs

        # Check all fields in the model for HashID fields
        for field in model_class._meta.get_fields():
            if isinstance(field, (HashidField, HashidAutoField)):
                # Explicitly declare the HashID field
                attrs[field.name] = HashidSerializerCharField(
                    source_field=field.name, read_only=True
                )

        return attrs

    @staticmethod
    def _parse_select_param(select_param):
        """
        Parse the select parameter to determine which fields to include.

        Args:
            select_param: The select query parameter value

        Returns:
            List of field names or None for all fields
        """
        if not select_param:
            return None

        # Handle aggregation queries (will be processed differently)
        if any(
            func in select_param.lower()
            for func in ["count()", "sum(", "avg(", "min(", "max("]
        ):
            return None

        # Split by comma and clean up field names
        fields = [field.strip() for field in select_param.split(",") if field.strip()]
        return fields if fields else None

    @staticmethod
    def _parse_embed_param(embed_param):
        """
        Parse the embed parameter to determine which relationships to include.

        Args:
            embed_param: The embed query parameter value

        Returns:
            List of relationship field names to embed
        """
        if not embed_param:
            return []

        # Split by comma and clean up field names
        embed_fields = [
            field.strip() for field in embed_param.split(",") if field.strip()
        ]
        return embed_fields

    @classmethod
    def _create_embed_fields(cls, model_class, embed_field, request=None):
        """
        Create serializer fields for embedded relationships.

        Args:
            model_class: The Django model class
            embed_field: The relationship field name to embed
            request: The current request (for nested serializer creation)

        Returns:
            Dictionary of field name to serializer field
        """
        attrs = {}

        # Check if embedding is allowed for this model
        if hasattr(model_class, "AutoRestMeta"):
            auto_rest_meta = model_class.AutoRestMeta
            if hasattr(auto_rest_meta, "embed_allowed"):
                if embed_field not in auto_rest_meta.embed_allowed:
                    # Skip this field if not in allowed list
                    return attrs
            
            # Also check if this field is excluded
            if hasattr(auto_rest_meta, "exclude_fields"):
                if embed_field in auto_rest_meta.exclude_fields:
                    # Skip this field if it's excluded
                    return attrs

        try:
            # Try to get the field (could be direct or reverse relationship)
            field = model_class._meta.get_field(embed_field)

            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                # Forward relationship: ForeignKey/OneToOne
                related_model = field.related_model
                # Don't pass request to nested serializers to avoid field selection conflicts
                nested_serializer_class = cls.for_model(related_model, request=None)
                attrs[embed_field] = nested_serializer_class(read_only=True)

            elif isinstance(field, models.ManyToManyField):
                # Forward relationship: ManyToMany
                related_model = field.related_model
                # Don't pass request to nested serializers to avoid field selection conflicts
                nested_serializer_class = cls.for_model(related_model, request=None)
                attrs[embed_field] = nested_serializer_class(many=True, read_only=True)

            elif hasattr(field, "related_model"):
                # Reverse relationship (ManyToOneRel, OneToOneRel, ManyToManyRel)
                related_model = field.related_model
                # Don't pass request to nested serializers to avoid field selection conflicts
                nested_serializer_class = cls.for_model(related_model, request=None)

                # Check if it's a multiple relationship
                is_many = getattr(
                    field, "multiple", True
                )  # Default to True for reverse ForeignKey

                if is_many:
                    attrs[embed_field] = nested_serializer_class(
                        many=True, read_only=True
                    )
                else:
                    attrs[embed_field] = nested_serializer_class(read_only=True)

        except FieldDoesNotExist:
            # Fallback: check for reverse relationships using the old method
            reverse_relation = cls._get_reverse_relation(model_class, embed_field)
            if reverse_relation:
                related_model = reverse_relation["model"]
                is_many = reverse_relation["many"]

                # Don't pass request to nested serializers to avoid field selection conflicts
                nested_serializer_class = cls.for_model(related_model, request=None)
                if is_many:
                    attrs[embed_field] = nested_serializer_class(
                        many=True, read_only=True
                    )
                else:
                    attrs[embed_field] = nested_serializer_class(read_only=True)

        return attrs

    @staticmethod
    def _get_reverse_relation(model_class, field_name):
        """
        Get information about a reverse relationship.

        Args:
            model_class: The Django model class
            field_name: The field name to check

        Returns:
            Dictionary with 'model' and 'many' keys, or None if not found
        """
        # Check all related objects for this model
        for related_object in model_class._meta.related_objects:
            if related_object.get_accessor_name() == field_name:
                return {
                    "model": related_object.related_model,
                    "many": related_object.multiple,
                }

        # Check for related managers (like reverse ForeignKey)
        try:
            related_manager = getattr(model_class, field_name, None)
            if related_manager and hasattr(related_manager, "related"):
                related_field = related_manager.related
                return {
                    "model": related_field.related_model,
                    "many": related_field.multiple,
                }
        except (AttributeError, TypeError):
            pass

        return None

    @classmethod
    def _get_excluded_fields(cls, model_class):
        """
        Get fields that should be excluded from serialization based on model configuration.

        Args:
            model_class: The Django model class

        Returns:
            List of field names to exclude
        """
        excluded_fields = []

        # Check if model has AutoRestMeta configuration
        if hasattr(model_class, "AutoRestMeta"):
            auto_rest_meta = model_class.AutoRestMeta

            # Get excluded fields list
            if hasattr(auto_rest_meta, "exclude_fields"):
                excluded_fields.extend(auto_rest_meta.exclude_fields)

        return excluded_fields

    @classmethod
    def _determine_final_fields(cls, model_class, selected_fields, excluded_fields):
        """
        Determine the final list of fields to include in the serializer.
        This is only called when we're using the 'fields' approach (not 'exclude').

        Args:
            model_class: The Django model class
            selected_fields: Fields explicitly selected via ?select parameter
            excluded_fields: Fields to exclude based on configuration

        Returns:
            Final fields list or "__all__"
        """
        # If no exclusions, use selected fields or all
        if not excluded_fields:
            return selected_fields or "__all__"

        # If we have selected fields, filter out excluded ones
        if selected_fields:
            final_fields = [f for f in selected_fields if f not in excluded_fields]
            # Always include at least ID if all fields were excluded
            return final_fields if final_fields else ["id"]

        # This case should not happen since we use 'exclude' when no selected fields
        return "__all__"

    def to_representation(self, instance):
        """
        Convert the model instance to a dictionary representation.
        """
        ret = super().to_representation(instance)

        # Handle any custom transformations here
        return ret


class AutoRestListSerializer(serializers.ListSerializer):
    """
    Custom list serializer for handling collection responses.
    """

    def to_representation(self, data):
        """
        Convert the queryset to a list representation.
        """
        return super().to_representation(data)


def get_serializer_for_model(model_class, **kwargs):
    """
    Convenience function to get a serializer for a model.

    Args:
        model_class: The Django model class
        **kwargs: Additional serializer options

    Returns:
        A configured AutoRestSerializer class
    """
    return AutoRestSerializer.for_model(model_class, **kwargs)
