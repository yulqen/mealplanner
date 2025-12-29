# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A family meal planning Django web application that manages recipes, generates weekly meal plans, and produces store-specific shopping lists. Target: self-hosted on Debian with nginx.

## Technology Stack

- **Backend**: Django 6.x with SQLite
- **Frontend**: Django templates + HTMX + Tailwind CSS (standalone CLI, no Node.js)
- **Real-time**: HTMX polling (5s interval) for shopping list sync
- **Deployment**: nginx + gunicorn
- **Package Manager**: uv

## Common Commands

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

# Tailwind CSS (using standalone binary)
./tailwindcss -i core/static/core/css/input.css -o core/static/core/css/styles.css --watch

# Collect static files for production
uv run manage.py collectstatic
```

## Architecture

### App Structure

Single `core` app contains all functionality:
- `models.py` - All models (MealType, Recipe, Ingredient, WeekPlan, ShoppingList, etc.)
- `views/` - Split by domain: recipes.py, ingredients.py, plans.py, shopping.py, settings_views.py
- `services/` - Business logic: shuffle.py (meal plan generation), shopping.py (list generation)
- `templates/core/` - Full page templates
- `templates/components/` - HTMX partials for dynamic updates

### Key Data Models

- **Recipe** → has many RecipeIngredients → references Ingredients
- **Ingredient** → belongs to ShoppingCategory, can be pantry staple (excluded from lists)
- **WeekPlan** → has 7 PlannedMeals (day_offset 0-6)
- **ShoppingList** → has items, references Store for category ordering
- **Store** → has StoreCategoryOrders defining aisle sequence per category

### Business Logic

**Shuffle Algorithm** (`services/shuffle.py`): Assigns random recipes ensuring no consecutive days have the same MealType.

**Shopping List Generation** (`services/shopping.py`): Aggregates ingredients from week plan recipes, excludes pantry staples, orders by store-specific category sequence.

### HTMX Patterns

- Recipe list filters update without full reload
- Week plan shuffle/assign use HTMX swaps
- Shopping list checkbox toggles use HTMX with polling for multi-device sync
- Ingredient autocomplete with inline creation during recipe editing

## Implementation Phases

The spec defines 5 phases: Foundation (recipes + auth) → Ingredients → Meal Planning → Shopping Lists → Polish. Reference `mealplanner-spec.md` for detailed requirements.
