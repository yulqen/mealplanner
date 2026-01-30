# Quick Start & Common Commands

## Development Server

```bash
uv run manage.py runserver
```

Access at `http://localhost:8000`

## Testing

```bash
# All tests
uv run manage.py test

# Specific test file
uv run manage.py test core.tests.test_recipes

# Single test
uv run manage.py test core.tests.test_recipes.RecipeViewTests.test_recipe_list
```

## Database

```bash
# Create migrations after model changes
uv run manage.py makemigrations

# Apply migrations
uv run migrate

# Load seed data (MealTypes, ShoppingCategories, Stores)
uv run manage.py seed_data

# Reset database (destructive!)
uv run manage.py flush
```

## Dependencies

```bash
# Add a new dependency
uv add <package>

# Sync dependencies to local environment
uv sync

# See what's installed
uv pip list
```

## CSS

```bash
# Production build
make css

# Watch mode (for development)
make css-watch
```

## Static Files

```bash
# For production deployment
uv run manage.py collectstatic
```

## Deployment

```bash
# Collect static files (required before deployment)
uv run manage.py collectstatic

# Run with gunicorn (used in production)
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Useful Django Shell

```bash
uv run manage.py shell

# Then in the shell:
from core.models import Recipe
Recipe.objects.count()
```
