---
title: FastAPI Mason — Build REST APIs with Django Patterns in FastAPI
description: FastAPI Mason brings Django REST Framework patterns to FastAPI. Build robust APIs with ViewSets, automatic CRUD, permissions, and pagination using Tortoise ORM.
keywords: FastAPI, Django REST Framework, ViewSets, REST API, Tortoise ORM, Python Backend, API Development, CRUD operations, FastAPI Mason
---
<p align="center">
  <h1 align="center">FastAPI Mason</h1>
</p>
<p align="center">
  <img align="center" src="assets/logo.png" alt="FastAPI Mason - Django REST Framework for FastAPI" width="250"/>
</p>
<p align="center">
  <span>Build REST APIs with Django REST Framework patterns in FastAPI</span>
</p>
<p align="center">
<a href="https://pypi.org/project/fastapi-mason/">
  <img src="https://img.shields.io/pypi/v/fastapi-mason?color=%2334D058&label=version" alt="Version"/>
</a>
<a href="https://pypi.org/project/fastapi-mason/">
  <img src="https://img.shields.io/pypi/pyversions/fastapi-mason.svg?color=%2334D058" alt="Python versions"/>
</a>
<a href="https://github.com/bubaley/fastapi-mason/blob/main/LICENSE">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"/>
</a>
</p>

---

**Transform your FastAPI development with familiar Django REST Framework patterns.**

If you've worked with Django REST Framework, you'll love FastAPI Mason. It brings the same powerful patterns—ViewSets, automatic CRUD, permissions, and pagination—to FastAPI's high-performance foundation.

<div align="center" style="margin: 2rem 0;">
  <a href="quick-start/" class="get-started-btn">
    🚀 Get Started in 5 Minutes
  </a>
</div>

## 📦 Installation

```bash
uv add fastapi-mason
```

## 🚀 Quick Example

Here's a complete example showing how to build a REST API with FastAPI Mason:

```python
# main.py - Complete FastAPI Mason application
from fastapi import APIRouter, FastAPI
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
from tortoise.models import Model

from fastapi_mason.decorators import action, viewset
from fastapi_mason.pagination import PageNumberPagination
from fastapi_mason.schemas import SchemaMeta, build_schema, rebuild_schema
from fastapi_mason.viewsets import ModelViewSet
from fastapi_mason.wrappers import PaginatedResponseDataWrapper, ResponseDataWrapper


# Database setup
def register_database(app: FastAPI):
    register_tortoise(
        app,
        db_url='sqlite://db.sqlite3',
        modules={'models': ['main']},
        generate_schemas=True,
        add_exception_handlers=True,
    )


# Models
class Company(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    full_name = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


# Schema meta
class CompanyMeta(SchemaMeta):
    include = ('id', 'name', 'full_name', 'created_at', 'updated_at')


# Schemas
CompanySchema = build_schema(Company, meta=CompanyMeta)
CompanyCreateSchema = rebuild_schema(CompanySchema, exclude_readonly=True)

# Views
router = APIRouter(prefix='/companies', tags=['companies'])

@viewset(router)
class CompanyViewSet(ModelViewSet[Company]):
    model = Company
    read_schema = CompanySchema
    create_schema = CompanyCreateSchema

    pagination = PageNumberPagination
    list_wrapper = PaginatedResponseDataWrapper
    single_wrapper = ResponseDataWrapper

    # permission_classes = [IsAuthenticatedOrReadOnly]

    @action(methods=['GET'], detail=False, response_model=dict[str, int])
    async def stats(self):
        return {'total': await Company.all().count()}


# Application
app = FastAPI(title='My API')
register_database(app)
app.include_router(router)
```

Start server:

```bash
uvicorn main:app --reload
```

 Try API Endpoints:

```json
"""
This creates the following endpoints:
- GET /companies/ - List companies with pagination
- POST /companies/ - Create new company
- GET /companies/{item_id}/ - Get specific company
- PUT /companies/{item_id}/ - Update company
- DELETE /companies/{item_id}/ - Delete company
- GET /companies/stats/ - Custom stats endpoint

Example API Responses:

GET /companies/ (with pagination wrapper):
{
  "data": [
    {
      "id": 1,
      "name": "Acme Corp",
      "full_name": "Acme Corporation Ltd.",
      "created_at": "2023-01-01T10:00:00Z",
      "updated_at": "2023-01-01T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_pages": 5,
    "total_items": 47
  }
}

GET /companies/1/ (with single wrapper):
{
  "data": {
    "id": 1,
    "name": "Acme Corp",
    "full_name": "Acme Corporation Ltd.",
    "created_at": "2023-01-01T10:00:00Z",
    "updated_at": "2023-01-01T10:00:00Z"
  }
}

GET /companies/stats/ (custom action):
{
  "total": 123
}
"""
```
See the [Quick Start guide](quick-start.md) for a complete working example

## ✨ Key Features

<div class="feature-card">
  <h3>🎯 ViewSets</h3>
Django-like ViewSets with automatic CRUD operations and custom actions. Build complete REST APIs with minimal boilerplate code.
</div>

<div class="feature-card">
<h3>🔒 Permissions</h3>
Built-in permission system with customizable access control. Protect your endpoints with authentication and authorization rules.
</div>

<div class="feature-card">
<h3>📄 Pagination</h3>
Multiple pagination strategies out of the box: Limit/Offset and Page Number. Easily customizable for your needs.
</div>

<div class="feature-card">
<h3>📋 Schema Generation</h3>
Intelligent schema generation with meta classes for fine-grained control over API serialization.
</div>

<div class="feature-card">
<h3>🔄 Response Wrappers</h3>
Consistent API response formatting with customizable wrapper classes.
</div>

<div class="feature-card">
<h3>⚡ State Management</h3>
Request-scoped state management for sharing data across middleware and view components.
</div>

## 🎯 Philosophy

FastAPI Mason is designed with these principles:

- **Familiar**: If you know Django REST Framework, you already know FastAPI Mason
- **Flexible**: Customize every aspect while maintaining sensible defaults
- **Fast**: Built on FastAPI's high-performance foundation
- **Modular**: Use only what you need, when you need it

## 📚 Getting Started

Ready to build amazing APIs? Start with our [Quick Start guide](quick-start.md) to get up and running in minutes.

Want to dive deeper? Explore our comprehensive guides:

- [ViewSets](viewsets/index.md) - Learn about the core ViewSet concepts
- [Schemas & Meta](schemas.md) - Master schema generation and meta classes
- [Permissions](permissions.md) - Secure your APIs with permission classes
- [Pagination](pagination.md) - Implement efficient data pagination
- [State Management](state.md) - Manage request-scoped state
- [Response Wrappers](wrappers.md) - Format consistent API responses

## 🤝 Community

FastAPI Mason is open source and welcomes contributions! Whether you're reporting bugs, suggesting features, or submitting pull requests, your involvement helps make the library better for everyone.

- **GitHub**: [github.com/bubaley/fastapi-mason](https://github.com/bubaley/fastapi-mason)
- **Issues**: Report bugs and request features
- **Discussions**: Get help and share ideas

## 📄 License

FastAPI Mason is released under the [MIT License](https://github.com/bubaley/fastapi-mason/blob/main/LICENSE).
