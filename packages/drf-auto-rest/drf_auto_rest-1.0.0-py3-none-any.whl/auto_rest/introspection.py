"""
Auto-REST Introspection

Database and model introspection utilities.
"""

from django.db import models, connection
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist


class ModelIntrospector:
    """
    Utility class for introspecting Django models and their relationships.
    """

    @classmethod
    def get_model_fields(cls, model_class):
        """
        Get all fields for a model including relationships.

        Returns:
            Dictionary with field information
        """
        fields_info = {}

        for field in model_class._meta.get_fields():
            field_info = {
                "name": field.name,
                "type": field.__class__.__name__,
                "nullable": getattr(field, "null", False),
                "blank": getattr(field, "blank", False),
                "default": getattr(field, "default", models.NOT_PROVIDED),
            }

            # Add relationship information
            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                field_info.update(
                    {
                        "is_relation": True,
                        "relation_type": "foreign_key",
                        "related_model": field.related_model.__name__,
                        "related_app": field.related_model._meta.app_label,
                    }
                )
            elif isinstance(field, models.ManyToManyField):
                field_info.update(
                    {
                        "is_relation": True,
                        "relation_type": "many_to_many",
                        "related_model": field.related_model.__name__,
                        "related_app": field.related_model._meta.app_label,
                    }
                )
            elif hasattr(field, "related_model"):
                # Reverse relationships
                field_info.update(
                    {
                        "is_relation": True,
                        "relation_type": "reverse",
                        "related_model": field.related_model.__name__,
                        "related_app": field.related_model._meta.app_label,
                    }
                )
            else:
                field_info["is_relation"] = False

            fields_info[field.name] = field_info

        return fields_info

    @classmethod
    def get_filterable_fields(cls, model_class):
        """
        Get fields that can be used for filtering.
        """
        filterable = []

        for field in model_class._meta.get_fields():
            # Skip reverse relationships for now
            if hasattr(field, "related_model") and not hasattr(field, "null"):
                continue

            # Include most field types
            if isinstance(
                field,
                (
                    models.CharField,
                    models.TextField,
                    models.IntegerField,
                    models.FloatField,
                    models.DecimalField,
                    models.BooleanField,
                    models.DateField,
                    models.DateTimeField,
                    models.TimeField,
                    models.ForeignKey,
                    models.OneToOneField,
                ),
            ):
                filterable.append(field.name)

        return filterable

    @classmethod
    def get_orderable_fields(cls, model_class):
        """
        Get fields that can be used for ordering.
        """
        orderable = []

        for field in model_class._meta.get_fields():
            # Skip reverse relationships
            if hasattr(field, "related_model") and not hasattr(field, "null"):
                continue

            # Include fields that make sense for ordering
            if isinstance(
                field,
                (
                    models.CharField,
                    models.IntegerField,
                    models.FloatField,
                    models.DecimalField,
                    models.DateField,
                    models.DateTimeField,
                    models.TimeField,
                    models.ForeignKey,
                    models.OneToOneField,
                ),
            ):
                orderable.append(field.name)

        return orderable

    @classmethod
    def get_searchable_fields(cls, model_class):
        """
        Get fields that can be used for text search.
        """
        searchable = []

        for field in model_class._meta.get_fields():
            # Only text fields are searchable
            if isinstance(field, (models.CharField, models.TextField)):
                searchable.append(field.name)

        return searchable

    @classmethod
    def get_related_fields(cls, model_class):
        """
        Get all relationship fields that can be embedded.
        """
        related = []

        for field in model_class._meta.get_fields():
            if isinstance(
                field, (models.ForeignKey, models.OneToOneField, models.ManyToManyField)
            ):
                related.append(field.name)

        return related


class DatabaseIntrospector:
    """
    Utility class for database-level introspection.
    """

    @classmethod
    def get_table_info(cls, model_class):
        """
        Get database table information for a model.
        """
        table_name = model_class._meta.db_table

        with connection.cursor() as cursor:
            # This is database-specific, here's a basic version
            table_info = {
                "table_name": table_name,
                "model_name": model_class.__name__,
                "app_label": model_class._meta.app_label,
            }

            # Get column information
            columns = connection.introspection.get_table_description(cursor, table_name)
            table_info["columns"] = [
                {
                    "name": col.name,
                    "type": col.type_code,
                    "nullable": col.null_ok,
                    "default": col.default,
                }
                for col in columns
            ]

        return table_info

    @classmethod
    def get_indexes(cls, model_class):
        """
        Get index information for a model's table.
        """
        table_name = model_class._meta.db_table

        with connection.cursor() as cursor:
            indexes = connection.introspection.get_indexes(cursor, table_name)

        return indexes


def get_model_schema(model_class):
    """
    Get complete schema information for a model.

    Args:
        model_class: Django model class

    Returns:
        Dictionary with complete model schema information
    """
    return {
        "model_name": model_class.__name__,
        "app_label": model_class._meta.app_label,
        "table_name": model_class._meta.db_table,
        "fields": ModelIntrospector.get_model_fields(model_class),
        "filterable_fields": ModelIntrospector.get_filterable_fields(model_class),
        "orderable_fields": ModelIntrospector.get_orderable_fields(model_class),
        "searchable_fields": ModelIntrospector.get_searchable_fields(model_class),
        "related_fields": ModelIntrospector.get_related_fields(model_class),
        "table_info": DatabaseIntrospector.get_table_info(model_class),
    }
