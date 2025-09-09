# DRF Auto-REST: PostgREST for Django REST Framework

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/djangorestframework-3.14+-orange.svg)](https://django-rest-framework.org)

A powerful Django REST Framework extension that automatically generates PostgREST-like APIs from your Django models. Get advanced querying, filtering, aggregation, and relationship embedding with zero boilerplate code.

## 🚀 Quick Start

```python
# 1. Define your model with Auto-REST configuration
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_featured = models.BooleanField(default=False)
    
    class AutoRestMeta:
        filterable_fields = ['name', 'price', 'category', 'is_featured']
        searchable_fields = ['name', 'description']
        orderable_fields = ['name', 'price', 'created_at']
        embed_allowed = ['category', 'reviews']  # Relationship embedding

# 2. Auto-register in urls.py (one line!)
auto_router = AutoRestRouter()
auto_router.auto_register_models(['your_app'])

# 3. Start querying with powerful PostgREST syntax
GET /api/product/?price=gt.500&is_featured=eq.true
GET /api/product/?or=(price.lt.100,is_featured.eq.true)
GET /api/product/?select=count()&group_by=category
GET /api/product/?embed=category,reviews&select=name,price
```

## ✨ Key Features

### 🔄 **Zero Configuration APIs**
- **Automatic Discovery**: All models auto-registered as REST endpoints
- **Dynamic Serialization**: Field selection based on request parameters  
- **Smart Routing**: Conflict-free URL generation with app namespacing

### 🔍 **Advanced PostgREST Querying**
- **Rich Operators**: `eq`, `gt`, `like`, `in`, `range`, `is.null` and more
- **Logical Operations**: Complex `OR` and `NOT` conditions
- **Pattern Matching**: Wildcard text search with `like` and `ilike`
- **Type Safety**: Automatic value conversion (strings, numbers, booleans)

### 📊 **Business Intelligence & Analytics**
- **Aggregation Functions**: `count()`, `sum()`, `avg()`, `min()`, `max()`
- **Grouping**: Multi-field grouping with `group_by`
- **Having Clauses**: Filter aggregated results
- **Pre-filtering**: Combine aggregations with WHERE conditions

### 🔗 **Relationship Embedding**
- **Deep Embedding**: Include related data in single requests
- **Query Optimization**: Automatic `select_related` and `prefetch_related`
- **Permission Control**: Fine-grained embedding permissions
- **Performance**: Eliminates N+1 query problems

### 🔒 **Field Exclusion & Security**
- **Sensitive Data Protection**: Exclude internal/sensitive fields from all API responses
- **Aggregation Blocking**: Prevent aggregation operations on excluded fields
- **Embedding Filtering**: Excluded fields are omitted from embedded relationships
- **Override Protection**: Excluded fields remain hidden even with explicit `?select`

### 📄 **Flexible Pagination & Ordering**
- **Dual Pagination**: PostgREST (`?limit=10&offset=20`) and Django (`?page=2`) styles
- **Multi-field Sorting**: `?order=created_at.desc,name.asc`
- **Configurable Limits**: Per-model pagination controls

## 🎯 Live API Examples

Start the included e-commerce demo:

```bash
python manage.py runserver
curl http://localhost:8000/api/
```

### Basic Filtering & Selection
```bash
# Products over $500
GET /api/ecommerce_product/?price=gt.500

# Select specific fields only
GET /api/ecommerce_product/?select=name,price,is_featured

# Featured products under $100  
GET /api/ecommerce_product/?price=lt.100&is_featured=eq.true

# Pattern matching
GET /api/ecommerce_product/?name=like.*laptop*
```

### Complex Logical Operations
```bash
# OR logic: cheap OR featured products
GET /api/ecommerce_product/?or=(price.lt.100,is_featured.eq.true)

# NOT logic: non-featured products
GET /api/ecommerce_product/?not.is_featured=eq.true

# Complex combinations with pattern matching
GET /api/ecommerce_product/?or=(name.like.*Laptop*,name.like.*Desktop*)
```

### Range & List Operations
```bash
# Price range filtering
GET /api/ecommerce_product/?price=range.[100,500]

# Multiple ID selection
GET /api/ecommerce_product/?id=in.(1,2,3,5,8)

# Null checks
GET /api/ecommerce_product/?sale_price=is.null
```

### Relationship Embedding
```bash
# Embed category data
GET /api/ecommerce_product/?embed=category

# Multiple relationships + field selection
GET /api/ecommerce_product/?embed=category,reviews&select=name,price,category,reviews

# Nested data with filtering
GET /api/ecommerce_order/?embed=customer&status=eq.pending
```

### Field Exclusion & Security
```bash
# Excluded fields are automatically hidden from all responses
GET /api/ecommerce_product/?select=name,price,cost_price
# Result: Only name and price returned (cost_price is excluded)

# Excluded fields cannot be used in aggregations
GET /api/ecommerce_product/?select=avg(cost_price)
# Result: Error - "Cannot resolve keyword 'cost_price' into field"

# Embedded relationships respect their own exclusions
GET /api/ecommerce_order/?embed=customer
# Result: Customer data excludes internal_notes and credit_score fields
```

### Aggregation & Business Intelligence
```bash
# Count all products
GET /api/ecommerce_product/?select=count()

# Product count per category
GET /api/ecommerce_product/?select=count()&group_by=category

# Comprehensive product analytics by category
GET /api/ecommerce_product/?select=count(),sum(price),avg(price),min(price),max(price)&group_by=category

# Filter aggregated results (HAVING clause)
GET /api/ecommerce_product/?select=count()&group_by=is_featured&having=count.gt.1

# Inventory analytics with pre-filtering
GET /api/ecommerce_product/?select=count(),min(stock_quantity),max(stock_quantity)&group_by=category&is_active=eq.true
```

### Advanced Multi-Parameter Queries
```bash
# Complex business query: expensive active products with stats
GET /api/ecommerce_product/?select=count(),avg(price)&group_by=category&price=gt.1000&is_active=eq.true

# Sales analytics with relationships
GET /api/ecommerce_order/?embed=customer&select=count(),sum(total_amount)&group_by=status
```

## 📊 Complete Query Reference

### Comparison Operators
| Operator | Syntax | Example | Description |
|----------|--------|---------|-------------|
| `eq` | `field=eq.value` | `?status=eq.published` | Equals |
| `neq` | `field=neq.value` | `?status=neq.draft` | Not equals |
| `gt` | `field=gt.value` | `?price=gt.100` | Greater than |
| `gte` | `field=gte.value` | `?price=gte.100` | Greater than or equal |
| `lt` | `field=lt.value` | `?price=lt.1000` | Less than |
| `lte` | `field=lte.value` | `?price=lte.1000` | Less than or equal |

### Pattern & List Operators
| Operator | Syntax | Example | Description |
|----------|--------|---------|-------------|
| `like` | `field=like.*pattern*` | `?name=like.*laptop*` | Case-sensitive pattern |
| `ilike` | `field=ilike.*pattern*` | `?name=ilike.*LAPTOP*` | Case-insensitive pattern |
| `in` | `field=in.(v1,v2,v3)` | `?id=in.(1,2,3)` | Value in list |
| `range` | `field=range.[min,max]` | `?price=range.[100,500]` | Value in range |
| `is` | `field=is.null/true/false` | `?description=is.null` | Null/boolean check |

### Logical Operators
| Operator | Syntax | Example | Description |
|----------|--------|---------|-------------|
| `or` | `or=(cond1,cond2,...)` | `?or=(price.lt.100,is_featured.eq.true)` | Logical OR |
| `not` | `not.field=operator.value` | `?not.is_featured=eq.true` | Logical NOT |

### Aggregation Functions
| Function | Syntax | Example | Description |
|----------|--------|---------|-------------|
| `count()` | `select=count()` | `?select=count()` | Row count |
| `sum(field)` | `select=sum(field)` | `?select=sum(price)` | Sum of values |
| `avg(field)` | `select=avg(field)` | `?select=avg(price)` | Average value |
| `min(field)` | `select=min(field)` | `?select=min(price)` | Minimum value |
| `max(field)` | `select=max(field)` | `?select=max(price)` | Maximum value |

### Special Parameters
| Parameter | Syntax | Example | Description |
|-----------|--------|---------|-------------|
| `select` | `select=field1,field2` | `?select=name,price` | Field selection |
| `embed` | `embed=rel1,rel2` | `?embed=category,reviews` | Relationship embedding |
| `order` | `order=field.dir` | `?order=price.desc` | Sorting |
| `group_by` | `group_by=field1,field2` | `?group_by=category` | Aggregation grouping |
| `having` | `having=agg.op.value` | `?having=count.gt.5` | Aggregation filtering |
| `limit` | `limit=n` | `?limit=10` | Result limit |
| `offset` | `offset=n` | `?offset=20` | Result offset |

## 🏗️ Architecture & Configuration

### Model Configuration

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)  # Internal cost
    supplier_id = models.CharField(max_length=50)  # Sensitive business data
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    class AutoRestMeta:
        # Filtering permissions
        filterable_fields = ['name', 'category', 'price', 'is_active']
        
        # Text search capabilities  
        searchable_fields = ['name', 'description', 'sku']
        
        # Sorting permissions
        orderable_fields = ['name', 'price', 'created_at', 'stock_quantity']
        
        # Relationship embedding permissions
        embed_allowed = ['category', 'reviews', 'order_items']
        
        # Security: Exclude sensitive fields from ALL API responses
        exclude_fields = ['cost_price', 'supplier_id']
        
        # Performance & security limits
        max_page_size = 100
        
        # Read-only API (optional)
        read_only = False
        
        # Custom permission classes (optional)
        permission_classes = ['rest_framework.permissions.IsAuthenticated']
```

### Settings Configuration

```python
# settings.py
AUTO_REST = {
    'DEFAULT_PAGINATION_CLASS': 'auto_rest.pagination.AutoRestPagination',
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': [
        'auto_rest.filters.AutoRestFilterBackend',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'ENABLE_AGGREGATION': True,
    'MAX_EMBED_DEPTH': 3,
    'ALLOWED_MODELS': [],  # Empty = all models allowed
    'EXCLUDED_MODELS': ['auth.User', 'sessions.Session'],
}
```

### URL Registration

```python
# urls.py - Automatic model discovery
from auto_rest.routers import AutoRestRouter

auto_router = AutoRestRouter()
auto_router.auto_register_models(['your_app1', 'your_app2'])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(auto_router.urls)),
]
```

## 🎯 Core Components

### 1. **AutoRestViewSet**
- Inherits from `ModelViewSet` with PostgREST querying
- Automatic aggregation detection and handling
- Optimized queryset generation for embedded relationships
- Full CRUD operations with advanced filtering

### 2. **AutoRestFilterBackend** 
- Translates PostgREST operators to Django ORM queries
- Supports complex logical operations (OR, NOT)
- Type-safe value conversion and validation
- Graceful error handling for invalid queries

### 3. **AutoRestSerializer**
- Dynamic field selection based on `?select` parameter
- Automatic relationship embedding with `?embed`
- Nested serializer generation with permission checks
- Performance-optimized to prevent N+1 queries

### 4. **AutoRestRouter**
- Automatic model discovery across Django apps
- Conflict-free URL basename generation
- Support for both inclusion and exclusion model lists
- Integration with Django's URL system

### 5. **AutoRestPagination**
- Dual pagination style support (PostgREST + Django)
- Configurable per-model pagination limits
- Optimized count queries for large datasets
- Consistent response formatting


## 📝 Example Use Cases

### E-commerce Analytics
```bash
# Revenue by category for active products
GET /api/product/?select=sum(price),count()&group_by=category&is_active=eq.true

# Top-selling categories (with having clause)
GET /api/order_item/?select=sum(quantity),count()&group_by=product.category&having=sum_quantity.gt.100
```

### Inventory Management
```bash
# Low stock alerts
GET /api/product/?stock_quantity=lt.10&is_active=eq.true

# Category inventory summary
GET /api/product/?select=count(),min(stock_quantity),max(stock_quantity),avg(stock_quantity)&group_by=category
```

### Customer Insights
```bash
# High-value customers
GET /api/order/?select=sum(total_amount),count()&group_by=customer&having=sum_total_amount.gt.1000

# Customer order patterns with embedded data
GET /api/order/?embed=customer,order_items&order=created_at.desc&limit=100
```

## 📖 Interactive API Documentation

We provide three comprehensive documentation interfaces:

### 🔗 **Documentation URLs**

```bash
# Start the development server
python manage.py runserver

# Access documentation interfaces:
```

- **📊 Swagger UI**: [`http://localhost:8000/api/docs/`](http://localhost:8000/api/docs/)
  - Interactive API testing interface
  - Try queries directly in your browser
  - Test all PostgREST-like operators live

- **📚 ReDoc**: [`http://localhost:8000/api/redoc/`](http://localhost:8000/api/redoc/)
  - Beautiful, clean documentation interface
  - Perfect for sharing with team members
  - Comprehensive query examples

- **⚙️ OpenAPI Schema**: [`http://localhost:8000/api/schema/`](http://localhost:8000/api/schema/)
  - Raw OpenAPI 3.0 JSON schema
  - Use for API client generation
  - Integration with development tools

### 🎯 **What's Documented**
