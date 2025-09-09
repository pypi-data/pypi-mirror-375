"""
OpenAPI Schema Extensions for DRF Auto-REST

This module provides custom preprocessing and postprocessing hooks for drf-spectacular
to properly document Auto-REST specific features like PostgREST query operators,
aggregation functions, and relationship embedding.
"""

from drf_spectacular.openapi import AutoSchema
from drf_spectacular import openapi
from rest_framework import serializers
from django.db import models


def preprocess_auto_rest_operations(result, generator, request, public):
    """
    Preprocessing hook to enhance Auto-REST operations with custom parameter documentation.
    """
    for path, path_methods in result.get("paths", {}).items():
        for method, operation in path_methods.items():
            if method.lower() in ["get", "post", "put", "patch", "delete"]:
                # Check if this is an Auto-REST endpoint
                if _is_auto_rest_operation(operation):
                    _enhance_auto_rest_operation(operation, method.lower())

    return result


def postprocess_auto_rest_schema(result, generator, request, public):
    """
    Postprocessing hook to add Auto-REST specific schema components.
    """
    # Add custom schema components for Auto-REST
    if "components" not in result:
        result["components"] = {}

    if "schemas" not in result["components"]:
        result["components"]["schemas"] = {}

    # Add aggregation response schema
    result["components"]["schemas"]["AggregationResponse"] = {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": True,
            "description": "Aggregation result with dynamic fields based on select and group_by parameters",
        },
        "description": "Response format for aggregation queries using ?select=count(),sum(field)&group_by=field",
    }

    # Add error response schemas
    result["components"]["schemas"]["AutoRestError"] = {
        "type": "object",
        "properties": {
            "error": {"type": "string", "description": "Error type"},
            "message": {
                "type": "string",
                "description": "Human-readable error message",
            },
            "details": {
                "type": "object",
                "additionalProperties": True,
                "description": "Additional error details",
            },
        },
        "required": ["error", "message"],
    }

    # Add field exclusion error schema
    result["components"]["schemas"]["FieldExclusionError"] = {
        "type": "object",
        "properties": {
            "error": {
                "type": "string",
                "example": "Aggregation query failed",
                "description": "Error type for excluded field operations",
            },
            "message": {
                "type": "string",
                "example": "Cannot resolve keyword 'cost_price' into field. Choices are: category, category_id, created_at, description, id, is_active, name, price, updated_at",
                "description": "Detailed error message listing available fields when excluded field is accessed",
            },
        },
        "required": ["error", "message"],
        "description": "Error returned when attempting to aggregate or access excluded fields",
    }

    return result


def _is_auto_rest_operation(operation):
    """
    Check if an operation is from an Auto-REST viewset.
    """
    # Check operation tags or other indicators
    tags = operation.get("tags", [])
    return any("auto-rest" in tag.lower() or "ecommerce" in tag.lower() for tag in tags)


def _enhance_auto_rest_operation(operation, method):
    """
    Enhance an Auto-REST operation with custom parameter documentation.
    """
    if method == "get":
        # Add Auto-REST specific parameters for GET operations
        parameters = operation.setdefault("parameters", [])

        # Basic filtering parameters
        parameters.extend(
            [
                {
                    "name": "select",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": """
                **Field Selection**: Choose specific fields to return or aggregation functions.
                
                **Examples:**
                - `select=name,price,category` - Select specific fields
                - `select=count()` - Count all records  
                - `select=count(),sum(price),avg(price)` - Multiple aggregations
                - `select=sum(price)&group_by=category` - Aggregation with grouping
                
                **Aggregation Functions:**
                - `count()` - Count records
                - `sum(field)` - Sum numeric field
                - `avg(field)` - Average of numeric field  
                - `min(field)` - Minimum value
                - `max(field)` - Maximum value
                
                **🔒 Field Exclusion Security:**
                - Excluded fields (defined in `AutoRestMeta.exclude_fields`) are automatically hidden
                - Excluded fields cannot be selected, even when explicitly requested
                - Aggregation operations on excluded fields return detailed error messages
                - This protects sensitive data like internal costs, supplier IDs, or personal information
                """,
                    "example": "name,price,stock_quantity",
                },
                {
                    "name": "embed",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": """
                **Relationship Embedding**: Include related model data in the response.
                
                **Examples:**
                - `embed=category` - Include category data
                - `embed=category,reviews` - Include multiple relationships
                - `embed=category&select=name,price,category` - Combine with field selection
                
                **Permissions:**
                - Only relationships listed in model's `AutoRestMeta.embed_allowed` are permitted
                - Excluded relationship fields (in `AutoRestMeta.exclude_fields`) are silently ignored
                
                **🔒 Field Exclusion in Embedded Data:**
                - Embedded models respect their own `exclude_fields` configuration
                - Sensitive fields are automatically filtered from all embedded data
                - Example: `?embed=customer` excludes customer's `internal_notes` and `credit_score`
                """,
                    "example": "category,reviews",
                },
                {
                    "name": "order",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": """
                **Sorting**: Order results by one or more fields.
                
                **Examples:**
                - `order=created_at` - Sort by creation date (ascending)
                - `order=price.desc` - Sort by price (descending)
                - `order=name.asc,price.desc` - Multi-field sorting
                
                **Directions:** `.asc` (ascending, default), `.desc` (descending)
                """,
                    "example": "price.desc,name.asc",
                },
                {
                    "name": "group_by",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": """
                **Aggregation Grouping**: Group results for aggregation functions.
                
                **Examples:**
                - `group_by=category` - Group by single field
                - `group_by=category,is_featured` - Group by multiple fields
                - `select=count(),avg(price)&group_by=category` - Combine with aggregations
                
                **Note:** Only works with aggregation functions in `select` parameter.
                """,
                    "example": "category",
                },
                {
                    "name": "having",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": """
                **Aggregation Filtering**: Filter aggregated results (HAVING clause).
                
                **Examples:**
                - `having=count.gt.5` - Groups with more than 5 items
                - `having=avg_price.gte.100` - Groups with average price >= 100
                - `having=sum_quantity.lt.1000` - Groups with total quantity < 1000
                
                **Operators:** `gt`, `gte`, `lt`, `lte`, `eq`, `neq`
                """,
                    "example": "count.gt.5",
                },
            ]
        )

        # PostgREST-style filtering parameters
        parameters.extend(
            [
                {
                    "name": "or",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": """
                **Logical OR**: Combine multiple conditions with OR logic.
                
                **Format:** `or=(condition1,condition2,condition3)`
                
                **Examples:**
                - `or=(price.lt.100,is_featured.eq.true)` - Cheap OR featured items
                - `or=(name.like.*Laptop*,name.like.*Desktop*)` - Name contains "Laptop" OR "Desktop"
                - `or=(category.eq.electronics,category.eq.computers)` - Multiple categories
                """,
                    "example": "(price.lt.100,is_featured.eq.true)",
                },
                {
                    "name": "not.*",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": """
                **Logical NOT**: Exclude records matching condition.
                
                **Format:** `not.field=operator.value`
                
                **Examples:**
                - `not.is_featured=eq.true` - Non-featured items only
                - `not.status=eq.draft` - Exclude draft items
                - `not.price=gt.1000` - Exclude expensive items
                """,
                    "example": "eq.true",
                },
            ]
        )

        # Pagination parameters
        parameters.extend(
            [
                {
                    "name": "limit",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer", "minimum": 1, "maximum": 1000},
                    "description": "**PostgREST Pagination**: Number of records to return (max 1000)",
                    "example": 20,
                },
                {
                    "name": "offset",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer", "minimum": 0},
                    "description": "**PostgREST Pagination**: Number of records to skip",
                    "example": 0,
                },
                {
                    "name": "page",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer", "minimum": 1},
                    "description": "**Django Pagination**: Page number (1-based)",
                    "example": 1,
                },
                {
                    "name": "page_size",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer", "minimum": 1, "maximum": 1000},
                    "description": "**Django Pagination**: Number of records per page",
                    "example": 20,
                },
            ]
        )

        # Add dynamic filtering parameter documentation
        _add_dynamic_filter_parameters(operation)

        # Update response documentation for aggregation
        _update_response_documentation(operation)


def _add_dynamic_filter_parameters(operation):
    """
    Add documentation for dynamic filtering parameters based on PostgREST operators.
    """
    operation.setdefault("description", "")
    operation["description"] += """

### 🔍 Dynamic Filtering

You can filter any field using PostgREST-style operators. Use either format:
- `?field=operator.value` (e.g., `?price=gt.100`)  
- `?field.operator=value` (e.g., `?price.gt=100`)

**Supported Operators:**

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `?status=eq.published` |
| `neq` | Not equals | `?status=neq.draft` |
| `gt` | Greater than | `?price=gt.100` |
| `gte` | Greater than or equal | `?price=gte.100` |
| `lt` | Less than | `?price=lt.1000` |
| `lte` | Less than or equal | `?price=lte.1000` |
| `like` | Pattern match (case-sensitive) | `?name=like.*laptop*` |
| `ilike` | Pattern match (case-insensitive) | `?name=ilike.*LAPTOP*` |
| `in` | Value in list | `?id=in.(1,2,3,5,8)` |
| `range` | Value in range | `?price=range.[100,500]` |
| `is` | Null/boolean check | `?description=is.null` |

**Pattern Matching:**
- Use `*` as wildcards: `?name=like.*laptop*`
- Case-insensitive: `?name=ilike.*LAPTOP*`

**List Values:**
- Format: `?field=in.(value1,value2,value3)`
- Example: `?id=in.(1,2,3,5,8)`

**Range Values:**
- Format: `?field=range.[min,max]`
- Example: `?price=range.[100,500]`

**Boolean/Null Checks:**
- `?field=is.true` - Field is true
- `?field=is.false` - Field is false  
- `?field=is.null` - Field is null

**Multiple Filters:**
Multiple parameters are combined with AND logic by default:
`?price=gt.100&is_active=eq.true&category=eq.electronics`
"""


def _update_response_documentation(operation):
    """
    Update response documentation to include aggregation response format.
    """
    responses = operation.setdefault("responses", {})

    # Add aggregation response documentation
    if "200" in responses:
        original_description = responses["200"].get("description", "")
        responses["200"]["description"] = f"""{original_description}

**Response Formats:**

1. **Standard List Response** (default):
   ```json
   {{
     "count": 123,
     "next": "http://api/endpoint/?page=2", 
     "previous": null,
     "results": [...]
   }}
   ```

2. **Aggregation Response** (when using `?select=count()`, etc.):
   ```json
   [
     {{ "count": 25, "sum_price": 1250.00 }},
     {{ "category": "Electronics", "count": 15, "avg_price": 299.99 }}
   ]
   ```

3. **Embedded Response** (when using `?embed=related_field`):
   ```json
   {{
     "results": [
       {{
         "id": 1,
         "name": "Product",
         "category": {{ "id": 1, "name": "Electronics" }},
         "reviews": [{{ "id": 1, "rating": 5, "comment": "Great!" }}]
       }}
     ]
   }}
   ```
"""

    # Add error response documentation
    responses["400"] = {
        "description": "Bad Request - Invalid query parameters or operators",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/AutoRestError"},
                "examples": {
                    "invalid_operator": {
                        "summary": "Invalid operator",
                        "value": {
                            "error": "Invalid operator",
                            "message": 'Operator "invalid" is not supported. Use: eq, neq, gt, gte, lt, lte, like, ilike, in, range, is',
                        },
                    },
                    "aggregation_error": {
                        "summary": "Aggregation query error",
                        "value": {
                            "error": "Aggregation query failed",
                            "message": 'Field "nonexistent_field" does not exist for sum() function',
                        },
                    },
                    "excluded_field_error": {
                        "summary": "Excluded field aggregation error",
                        "value": {
                            "error": "Aggregation query failed",
                            "message": "Cannot resolve keyword 'cost_price' into field. Choices are: category, category_id, created_at, description, id, is_active, name, price, updated_at",
                        },
                    },
                },
            }
        },
    }


class AutoRestAutoSchema(AutoSchema):
    """
    Custom AutoSchema for Auto-REST viewsets with enhanced parameter documentation.
    """

    def get_operation_id(self):
        """Generate more descriptive operation IDs for Auto-REST endpoints."""
        # Enhance operation ID for Auto-REST endpoints
        if hasattr(self.view, "model"):
            model_name = self.view.model.__name__.lower()
            app_label = self.view.model._meta.app_label

            # More reliable logic to distinguish between list and retrieve operations
            # Check the URL pattern directly
            is_detail_view = (
                # Path contains parameter placeholders like {id}, {pk}, etc.
                "{" in self.path and "}" in self.path
            )

            # Create unique operation IDs
            if self.method == "GET":
                if is_detail_view:
                    operation_id = f"{app_label}_{model_name}_retrieve"
                else:
                    operation_id = f"{app_label}_{model_name}_list"
            elif self.method == "POST":
                operation_id = f"{app_label}_{model_name}_create"
            elif self.method == "PUT":
                operation_id = f"{app_label}_{model_name}_update"
            elif self.method == "PATCH":
                operation_id = f"{app_label}_{model_name}_partial_update"
            elif self.method == "DELETE":
                operation_id = f"{app_label}_{model_name}_destroy"
            else:
                # Fallback to default for any other methods
                return super().get_operation_id()

            return operation_id

        # Fallback to default operation ID generation
        return super().get_operation_id()

    def get_tags(self):
        """Generate descriptive tags for Auto-REST endpoints."""
        if hasattr(self.view, "model"):
            model_name = self.view.model.__name__
            app_label = self.view.model._meta.app_label.title()

            # Replace default tags with our custom Auto-REST tag
            auto_rest_tag = f"{app_label} - {model_name} (Auto-REST)"
            return [auto_rest_tag]

        # Fallback to default tags for non-Auto-REST endpoints
        return super().get_tags()

    def get_description(self):
        """Generate enhanced descriptions for Auto-REST endpoints."""
        description = super().get_description()

        # Check if this is an Auto-REST viewset by class name (avoid circular import)
        if hasattr(self.view, "model") and "AutoRestViewSet" in str(type(self.view)):
            model_name = self.view.model.__name__
            app_label = self.view.model._meta.app_label

            # Add Auto-REST specific description
            auto_rest_description = f"""
**Auto-REST Endpoint for {model_name}**

This endpoint is automatically generated from the `{app_label}.{model_name}` Django model with full PostgREST-like querying capabilities.

**Available Features:**
- Advanced filtering with PostgREST operators
- Field selection and relationship embedding  
- Aggregation functions and grouping
- Complex logical operations (OR, NOT)
- Flexible pagination (PostgREST and Django styles)
- Automatic query optimization

**Model Configuration:**
"""

            # Add model-specific configuration info
            if hasattr(self.view.model, "AutoRestMeta"):
                meta = self.view.model.AutoRestMeta

                if hasattr(meta, "filterable_fields"):
                    auto_rest_description += f"\n- **Filterable Fields:** {', '.join(meta.filterable_fields)}"

                if hasattr(meta, "searchable_fields"):
                    auto_rest_description += f"\n- **Searchable Fields:** {', '.join(meta.searchable_fields)}"

                if hasattr(meta, "orderable_fields"):
                    auto_rest_description += (
                        f"\n- **Orderable Fields:** {', '.join(meta.orderable_fields)}"
                    )

                if hasattr(meta, "embed_allowed"):
                    auto_rest_description += f"\n- **Embeddable Relationships:** {', '.join(meta.embed_allowed)}"

                if hasattr(meta, "max_page_size"):
                    auto_rest_description += (
                        f"\n- **Max Page Size:** {meta.max_page_size}"
                    )

            return description + auto_rest_description

        return description
