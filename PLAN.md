# Plan: Add Basic API to Meal Planner Application

## ✅ COMPLETED

**All phases have been successfully implemented and tested.**

- **40 API tests** created and passing
- **163 total tests** passing (including existing tests)
- **Full CRUD API** for all models
- **Custom actions** implemented (shuffle, generate, toggle_check, toggle_pin)
- **Swagger/OpenAPI documentation** available at `/api/v1/schema/swagger-ui/`
- **Session authentication** configured and tested

See [API_IMPLEMENTATION_STATUS.md](API_IMPLEMENTATION_STATUS.md) for detailed status.

---

## Context

The Meal Planner is a family-oriented Django application for recipe management, weekly scheduling, and grocery shopping. Currently, it uses Django's template-based views with HTMX for dynamic updates. The user wants to add a **basic API** to expose the application's data and functionality programmatically.

### Current State
- **Framework**: Django 6.0+
- **Frontend**: Template-based with HTMX for interactivity
- **Models**: Recipe, Ingredient, MealType, WeekPlan, PlannedMeal, ShoppingList, ShoppingListItem, Store, ShoppingCategory, StoreCategoryOrder
- **Services**: `shuffle.py` (meal shuffling algorithm), `shopping.py` (shopping list generation)
- **No existing API**: No REST framework installed, no API endpoints
- **Auth**: Django's built-in auth system with session-based authentication

### Goals
Add a basic API that exposes the core functionality of the Meal Planner application, allowing programmatic access to:
- Recipes and ingredients
- Meal types
- Week plans and planned meals
- Shopping lists and items
- Stores and categories

## Approach

### Technology Choice: Django REST Framework (DRF)

**Rationale**: 
- DRF is the de-facto standard for building APIs in Django
- Excellent integration with Django's ORM and authentication
- Provides serialization, validation, pagination, and browsing out of the box
- Well-documented and widely used in the Django community
- Aligns with the project's Python/Django tech stack

### API Design Decisions

Based on user preferences:

1. **Versioning**: Use `/api/v1/` prefix for all API endpoints
2. **Authentication**: Session authentication only (no token auth needed) - API users authenticate by first POSTing to Django's `/accounts/login/` endpoint to establish a session, then include the `sessionid` cookie in subsequent API requests
3. **Format**: JSON-based API following REST conventions
4. **Pagination**: Default pagination with 20 items per page
5. **Permissions**: All endpoints require authentication (no public access)
6. **URL Structure**: Nested resource URLs (e.g., `/api/v1/week-plans/1/planned-meals/`)
7. **Custom Actions**: POST endpoints for custom actions (e.g., `POST /api/v1/week-plans/1/shuffle/`)
8. **Write Operations**: Full CRUD support for all endpoints
9. **API Documentation**: Swagger/OpenAPI via drf-spectacular

### API Endpoints to Create

#### Core Resources
- `GET /api/v1/meal-types/` - List all meal types
- `POST /api/v1/meal-types/` - Create a meal type
- `GET /api/v1/meal-types/<id>/` - Retrieve a specific meal type
- `PUT /api/v1/meal-types/<id>/` - Update a meal type
- `PATCH /api/v1/meal-types/<id>/` - Partially update a meal type
- `DELETE /api/v1/meal-types/<id>/` - Delete a meal type
- `GET /api/v1/shopping-categories/` - List all shopping categories
- `POST /api/v1/shopping-categories/` - Create a shopping category
- `GET /api/v1/shopping-categories/<id>/` - Retrieve a specific category
- `PUT /api/v1/shopping-categories/<id>/` - Update a category
- `PATCH /api/v1/shopping-categories/<id>/` - Partially update a category
- `DELETE /api/v1/shopping-categories/<id>/` - Delete a category
- `GET /api/v1/stores/` - List all stores
- `POST /api/v1/stores/` - Create a store
- `GET /api/v1/stores/<id>/` - Retrieve a specific store
- `PUT /api/v1/stores/<id>/` - Update a store
- `PATCH /api/v1/stores/<id>/` - Partially update a store
- `DELETE /api/v1/stores/<id>/` - Delete a store

#### Recipes
- `GET /api/v1/recipes/` - List all recipes (with filtering by meal_type, difficulty, search, ace_tag)
- `POST /api/v1/recipes/` - Create a new recipe
- `GET /api/v1/recipes/<id>/` - Retrieve a specific recipe
- `PUT /api/v1/recipes/<id>/` - Update a recipe
- `PATCH /api/v1/recipes/<id>/` - Partially update a recipe
- `DELETE /api/v1/recipes/<id>/` - Delete a recipe

#### Ingredients
- `GET /api/v1/ingredients/` - List all ingredients
- `POST /api/v1/ingredients/` - Create a new ingredient
- `GET /api/v1/ingredients/<id>/` - Retrieve a specific ingredient
- `PUT /api/v1/ingredients/<id>/` - Update an ingredient
- `PATCH /api/v1/ingredients/<id>/` - Partially update an ingredient
- `DELETE /api/v1/ingredients/<id>/` - Delete an ingredient

#### Week Plans
- `GET /api/v1/week-plans/` - List all week plans
- `POST /api/v1/week-plans/` - Create a new week plan
- `GET /api/v1/week-plans/<id>/` - Retrieve a specific week plan
- `PUT /api/v1/week-plans/<id>/` - Update a week plan
- `PATCH /api/v1/week-plans/<id>/` - Partially update a week plan
- `DELETE /api/v1/week-plans/<id>/` - Delete a week plan
- `POST /api/v1/week-plans/<id>/shuffle/` - Shuffle meals for a week plan
- `GET /api/v1/week-plans/<id>/planned-meals/` - List planned meals for a week plan
- `POST /api/v1/week-plans/<id>/planned-meals/` - Create a planned meal for a week plan

#### Planned Meals
- `GET /api/v1/planned-meals/<id>/` - Retrieve a specific planned meal
- `PUT /api/v1/planned-meals/<id>/` - Update a planned meal
- `PATCH /api/v1/planned-meals/<id>/` - Partially update a planned meal
- `DELETE /api/v1/planned-meals/<id>/` - Delete a planned meal
- `POST /api/v1/planned-meals/<id>/toggle-pin/` - Toggle pinned status

#### Shopping Lists
- `GET /api/v1/shopping-lists/` - List all shopping lists
- `POST /api/v1/shopping-lists/` - Create a new shopping list
- `GET /api/v1/shopping-lists/<id>/` - Retrieve a specific shopping list
- `PUT /api/v1/shopping-lists/<id>/` - Update a shopping list
- `PATCH /api/v1/shopping-lists/<id>/` - Partially update a shopping list
- `DELETE /api/v1/shopping-lists/<id>/` - Delete a shopping list
- `POST /api/v1/shopping-lists/<id>/generate/` - Generate shopping list from week plan
- `GET /api/v1/shopping-lists/<id>/items/` - List items for a shopping list
- `POST /api/v1/shopping-lists/<id>/items/` - Create an item for a shopping list

#### Shopping List Items
- `GET /api/v1/shopping-list-items/<id>/` - Retrieve a specific item
- `PUT /api/v1/shopping-list-items/<id>/` - Update an item
- `PATCH /api/v1/shopping-list-items/<id>/` - Partially update an item
- `DELETE /api/v1/shopping-list-items/<id>/` - Delete an item
- `POST /api/v1/shopping-list-items/<id>/toggle-check/` - Toggle checked status

### Reuse of Existing Code

The following existing components can be reused:

1. **Models** (`core/models.py`): All data models are well-structured and can be directly serialized
2. **Services** (`core/services/shuffle.py`): The `shuffle_meals()` function can be reused for the shuffle endpoint
3. **Services** (`core/services/shopping.py`): The `generate_shopping_list()` function can be reused for shopping list generation
4. **Authentication**: Django's built-in auth system with session authentication
5. **Filtering logic**: The filtering patterns from `core/views.py` (recipe_list) can inform API filtering

## Files to Modify/Create

### New Files to Create

1. **`core/api/` directory** - New directory for API-related code
   - `core/api/__init__.py`
   - `core/api/urls.py` - API URL routing with nested resources
   - `core/api/serializers.py` - DRF serializers for all models
   - `core/api/views.py` - DRF views/viewsets for all endpoints with nested resource support
   - `core/api/permissions.py` - Custom permissions if needed
   - `core/api/pagination.py` - Custom pagination settings (page_size=20)

2. **`core/api/tests/`** - API tests
   - `core/api/tests/__init__.py`
   - `core/api/tests/test_serializers.py`
   - `core/api/tests/test_views.py`
   - `core/api/tests/test_auth.py`

### Files to Modify

1. **`mealplanner/settings.py`**
   - Add `rest_framework` to `INSTALLED_APPS`
   - Add `drf_spectacular` to `INSTALLED_APPS`
   - Add DRF configuration settings:
     - Default authentication classes (SessionAuthentication only)
     - Default permission classes (IsAuthenticated)
     - Default pagination (PageNumberPagination with page_size=20)
   - Add drf-spectacular configuration

2. **`mealplanner/urls.py`**
   - Add path to include API URLs: `path("api/v1/", include("core.api.urls"))`
   - Add drf-spectacular schema URLs

3. **`pyproject.toml`**
   - Add `djangorestframework` dependency
   - Add `drf-spectacular` dependency

## Implementation Steps

### Phase 1: Setup and Configuration

- [x] Install Django REST Framework: `uv add djangorestframework`
- [x] Install drf-spectacular: `uv add drf-spectacular`
- [x] Add `rest_framework` and `drf_spectacular` to `INSTALLED_APPS` in `settings.py`
- [x] Configure DRF settings in `settings.py`:
  - Default authentication classes (SessionAuthentication only)
  - Default permission classes (IsAuthenticated)
  - Default pagination (PageNumberPagination with page_size=20)
  - Date/time formatting
- [x] Configure drf-spectacular settings in `settings.py`
- [x] Update `pyproject.toml` with new dependencies (uv will handle this)
- [x] Run migrations: `uv run python manage.py migrate` (no new migrations needed)

### Phase 2: Create API Infrastructure

- [x] Create `core/api/` directory structure
- [x] Create `core/api/__init__.py`
- [x] Create `core/api/urls.py` with all API endpoint routing (including nested resources)
- [x] Create `core/api/pagination.py` with custom pagination (page_size=20)
- [x] Create `core/api/permissions.py` (if custom permissions needed)

### Phase 3: Create Serializers

- [x] Create `core/api/serializers.py` with serializers for:
  - `MealTypeSerializer`
  - `ShoppingCategorySerializer`
  - `StoreSerializer`
  - `StoreCategoryOrderSerializer`
  - `IngredientSerializer`
  - `RecipeIngredientSerializer`
  - `RecipeSerializer` (nested recipe ingredients)
  - `WeekPlanSerializer`
  - `PlannedMealSerializer` (nested recipe)
  - `ShoppingListSerializer`
  - `ShoppingListItemSerializer`

### Phase 4: Create Views

- [x] Create `core/api/views.py` with viewsets for:
  - `MealTypeViewSet` (full CRUD)
  - `ShoppingCategoryViewSet` (full CRUD)
  - `StoreViewSet` (full CRUD)
  - `StoreCategoryOrderViewSet` (full CRUD)
  - `IngredientViewSet` (full CRUD)
  - `RecipeViewSet` (full CRUD with filtering)
  - `WeekPlanViewSet` (full CRUD)
  - `PlannedMealViewSet` (full CRUD)
  - `ShoppingListViewSet` (full CRUD)
  - `ShoppingListItemViewSet` (full CRUD)
  - Custom action endpoints:
    - `shuffle` action on WeekPlanViewSet (POST /api/v1/week-plans/<id>/shuffle/)
    - `generate` action on ShoppingListViewSet (POST /api/v1/shopping-lists/<id>/generate/)
    - `toggle_check` action on ShoppingListItemViewSet (POST /api/v1/shopping-list-items/<id>/toggle_check/)
    - `toggle_pin` action on PlannedMealViewSet (POST /api/v1/planned-meals/<id>/toggle_pin/)
    - `planned_meals` action on WeekPlanViewSet (GET /api/v1/week-plans/<id>/planned_meals/)
    - `items` action on ShoppingListViewSet (GET /api/v1/shopping-lists/<id>/items/)

### Phase 5: Integrate with Main URLs

- [x] Update `mealplanner/urls.py` to include API URLs
- [x] Add drf-spectacular schema URLs
- [x] Verify all URLs are properly routed

### Phase 6: Create API Tests

- [x] Create `core/api/tests/` directory
- [x] Create test files for serializers
- [x] Create test files for views
- [x] Create test files for authentication (session auth required for all endpoints)
- [x] Test all CRUD operations
- [x] Test custom actions (shuffle, generate, toggle)
- [x] Test filtering and pagination
- [x] Test nested resource endpoints

**Result: 40 API tests created and passing ✅**

### Phase 7: Documentation

- [x] Configure drf-spectacular for Swagger/OpenAPI documentation
- [x] Add schema URL patterns for Swagger UI and OpenAPI JSON
- [x] Verify Swagger documentation is accessible at `/api/v1/schema/swagger-ui/`

## Verification

### Testing Strategy

1. **Unit Tests**: Test serializers, permissions, and individual view logic
2. **Integration Tests**: Test API endpoints with Django test client
3. **Authentication Tests**: Test session-based auth for all endpoints
4. **Edge Cases**: Test filtering, pagination, validation errors

### Manual Verification

1. Start development server: `uv run python manage.py runserver`
2. Access Swagger UI at `http://localhost:8000/api/v1/schema/swagger-ui/`
3. Access OpenAPI schema at `http://localhost:8000/api/v1/schema/`
4. Test endpoints with curl:
   ```bash
   # Get all recipes (requires session authentication)
   curl http://localhost:8000/api/v1/recipes/ --cookie "sessionid=YOUR_SESSION_ID"
   
   # Create a recipe
   curl -X POST http://localhost:8000/api/v1/recipes/ \
     --cookie "sessionid=YOUR_SESSION_ID" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Recipe", "meal_type": 1, "instructions": "Test"}'
   
   # Shuffle a week plan
   curl -X POST http://localhost:8000/api/v1/week-plans/1/shuffle/ \
     --cookie "sessionid=YOUR_SESSION_ID"
   
   # Generate shopping list from week plan
   curl -X POST http://localhost:8000/api/v1/shopping-lists/1/generate/ \
     --cookie "sessionid=YOUR_SESSION_ID" \
     -H "Content-Type: application/json" \
     -d '{"week_plan": 1}'
   ```
5. Verify all CRUD operations work correctly
6. Verify custom actions (shuffle, generate shopping list, toggle) work
7. Verify nested resource endpoints work correctly

### Run Test Suite

```bash
uv run python manage.py test core.api.tests
```

## Dependencies to Add

```toml
# In pyproject.toml
dependencies = [
    # ... existing dependencies
    "djangorestframework>=3.17.1",
    "drf-spectacular>=0.29.0",
]
```
