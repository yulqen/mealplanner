# AGENTS.md

Guidance for coding agents working on this repository.

## Quick Facts

- **Project**: Django web app for family meal planning (recipes, weekly plans, shopping lists)
- **Target**: Self-hosted on Debian with nginx
- **Package Manager**: `uv`

## Essential Commands

```bash
# Start development
uv run manage.py runserver

# Run tests
uv run manage.py test

# Database migrations
uv run manage.py makemigrations && uv run manage.py migrate

# Seed initial data
uv run manage.py seed_data
```

## Documentation

For detailed guidance, see:

- **[Quick Start & Common Commands](docs/QUICK_START.md)** — Full list of development tasks
- **[Architecture & Data Models](docs/ARCHITECTURE.md)** — App structure, models, business logic
- **[Frontend & HTMX Patterns](docs/FRONTEND.md)** — Template organization, dynamic updates
- **[Implementation Spec](mealplanner-spec.md)** — Complete requirements and tech stack

## Key Principles

1. **Single `core` app** with views split by domain (recipes, ingredients, plans, shopping)
2. **HTMX for interactivity** — no JavaScript build step
3. **Tailwind CSS via standalone CLI** — see `make css` and `make css-watch`
4. **Database-driven**: SQLite with Django ORM

## Before You Start

Reference `mealplanner-spec.md` for full requirements. If you're adding features, check the implementation phases to understand current scope.
