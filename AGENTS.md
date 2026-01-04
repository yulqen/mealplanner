# AGENTS.md

This file provides guidance for agentic coding agents operating in this repository.

## Project Overview

Family meal planning Django web application: recipes, weekly meal plans, store-specific shopping lists. Self-hosted on Debian with nginx.

**Tech Stack**: Django 6.x, SQLite, Django templates + HTMX, Tailwind CSS (standalone CLI), nginx + gunicorn, uv package manager.

## Build / Test Commands

```bash
# Development server
uv run manage.py runserver

# Run all tests
uv run manage.py test

# Run specific test file
uv run manage.py test core.tests.test_recipes

# Run single test
uv run manage.py test core.tests.test_recipes.RecipeViewTests.test_recipe_list

# Database migrations
uv run manage.py makemigrations
uv run manage.py migrate

# Load initial data (meal types, categories, stores)
uv run manage.py seed_data

# Add a dependency
uv add <package>

# Sync dependencies
uv sync

# Tailwind CSS (standalone binary)
./tailwindcss -i core/static/core/css/input.css -o core/static/core/css/styles.css --watch

# Collect static files for production
uv run manage.py collectstatic
```

## Code Style Guidelines

### General Principles

Write clean, readable code. Prefer explicitness over cleverness. Follow Django conventions. When editing, match the existing style in the file.

### Python Style

**Formatting**: Use 4 spaces for indentation. Keep line length reasonable (120 chars max). Use blank lines to separate logical sections within functions and between class/function definitions.

**Imports**: Group imports in this order: standard library, third-party, Django, local app. Sort alphabetically within groups. Use explicit relative imports for local modules.

```python
from pathlib import Path

from django.contrib import admin
from django.urls import path

from core import views
```

**Naming**: Use `PascalCase` for classes, `snake_case` for functions/variables, `SCREAMING_SNAKE_CASE` for constants. Use descriptive names: `get_or_create` not `goc`, `weekly_shopping_list` not `wsl`.

**Types**: Use type hints for function signatures. Prefer explicit types over `Any`. Use `Optional[X]` instead of `X | None`.

```python
def get_recipe_ingredients(recipe: Recipe) -> list[RecipeIngredient]:
    ...
```

**Error Handling**: Let exceptions propagate for unexpected errors. Use Django's `get_object_or_404` for view logic. Validate form data with Django forms. Log errors using Python's `logging` module.

**Django Patterns**: Put business logic in `services/` directory. Split views by domain (`views/recipes.py`, `views/shopping.py`, etc.). Use HTMX for dynamic updates with polling for sync. Keep templates in `templates/core/` for full pages, `templates/components/` for partials.

### HTML/Templates

Use Django template syntax. Keep templates simple—complex logic belongs in views or template tags. Include CSRF tokens for HTMX forms. Use Tailwind classes for styling.

### Database

Use Django migrations for all schema changes. Keep models in `core/models.py`. Use descriptive related_name values. Add `__str__` methods to all models.

## Testing

**Important**: This codebase currently has very few tests. ALL new code must be accompanied by new, passing tests. When adding features, fixing bugs, or refactoring, write tests that cover the changes. Run tests with `uv run manage.py test` before submitting changes.

### Git

Create focused commits with clear messages. Don't commit generated files or sensitive data. Reference issue numbers when relevant.
