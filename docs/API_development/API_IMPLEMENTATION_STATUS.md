# API Implementation Status

## Overview
The Meal Planner API has been successfully implemented using Django REST Framework (DRF) and drf-spectacular for OpenAPI documentation. The API now supports **dual authentication**: both session-based (for web browsers) and token-based JWT (for mobile apps, CLI tools, and third-party services).

## Completed Phases

### ✅ Phase 1: Setup and Configuration
- [x] Installed Django REST Framework (`djangorestframework>=3.17.1`)
- [x] Installed drf-spectacular (`drf-spectacular>=0.29.0`)
- [x] Installed djangorestframework-simplejwt (`djangorestframework-simplejwt>=5.3.0`)
- [x] Added `rest_framework`, `rest_framework_simplejwt`, and `drf_spectacular` to `INSTALLED_APPS`
- [x] Configured DRF settings:
  - SessionAuthentication (for web browsers)
  - JWTAuthentication (for API clients)
  - IsAuthenticated permission (all endpoints require auth)
  - PageNumberPagination with page_size=20
  - JSON and BrowsableAPI renderers
- [x] Configured drf-spectacular settings for Swagger/OpenAPI
- [x] Configured SimpleJWT settings:
  - Access token lifetime: 5 minutes
  - Refresh token lifetime: 1 day
  - Token rotation enabled
  - Blacklist after rotation enabled
- [x] Dependencies added to `pyproject.toml`

### ✅ Phase 2: Create API Infrastructure
- [x] Created `core/api/` directory
- [x] Created `core/api/__init__.py`
- [x] Created `core/api/urls.py` with DefaultRouter
- [x] Created `core/api/pagination.py` (StandardResultsSetPagination)
- [x] Created `core/api/permissions.py` (IsAuthenticatedOrReadOnly)

### ✅ Phase 3: Create Serializers
All serializers implemented in `core/api/serializers.py`:
- [x] MealTypeSerializer
- [x] ShoppingCategorySerializer
- [x] StoreSerializer
- [x] StoreCategoryOrderSerializer
- [x] IngredientSerializer
- [x] RecipeIngredientSerializer
- [x] RecipeSerializer (with nested recipe_ingredients)
- [x] WeekPlanSerializer
- [x] PlannedMealSerializer
- [x] ShoppingListSerializer
- [x] ShoppingListItemSerializer

### ✅ Phase 4: Create Views
All viewsets implemented in `core/api/views.py`:
- [x] MealTypeViewSet (full CRUD)
- [x] ShoppingCategoryViewSet (full CRUD)
- [x] StoreViewSet (full CRUD)
- [x] StoreCategoryOrderViewSet (full CRUD)
- [x] IngredientViewSet (full CRUD)
- [x] RecipeIngredientViewSet (full CRUD)
- [x] RecipeViewSet (full CRUD with filtering by meal_type, difficulty, ace_tag, search)
- [x] WeekPlanViewSet (full CRUD)
  - [x] Custom `shuffle` action (POST /api/v1/week-plans/{id}/shuffle/)
  - [x] Custom `planned_meals` action (GET /api/v1/week-plans/{id}/planned_meals/)
- [x] PlannedMealViewSet (full CRUD)
  - [x] Custom `toggle_pin` action (POST /api/v1/planned-meals/{id}/toggle_pin/)
- [x] ShoppingListViewSet (full CRUD)
  - [x] Custom `generate` action (POST /api/v1/shopping-lists/{id}/generate/)
  - [x] Custom `items` action (GET /api/v1/shopping-lists/{id}/items/)
- [x] ShoppingListItemViewSet (full CRUD)
  - [x] Custom `toggle_check` action (POST /api/v1/shopping-list-items/{id}/toggle_check/)

### ✅ Phase 5: Integrate with Main URLs
- [x] Updated `mealplanner/urls.py` to include API URLs at `/api/v1/`
- [x] Added drf-spectacular schema URLs:
  - `/api/v1/schema/` - OpenAPI JSON schema
  - `/api/v1/schema/swagger-ui/` - Swagger UI

### ✅ Phase 6: Create API Tests
All tests created in `core/api/tests/`:
- [x] `test_auth.py` - Authentication tests (15 tests)
  - Session authentication tests (4 tests)
  - Token authentication tests (8 tests)
  - Dual authentication tests (3 tests)
- [x] `test_serializers.py` - Serializer tests (11 tests)
- [x] `test_views.py` - View tests (25 tests)

**Total: 51 API tests, all passing ✅**

Test coverage includes:
- Session authentication required for all endpoints
- Token (JWT) authentication for all endpoints
- Dual authentication (both methods work simultaneously)
- CRUD operations for all models
- Custom actions (shuffle, generate, toggle_pin, toggle_check)
- Filtering (recipes by meal_type, difficulty, ace_tag, search)
- Pagination
- Serialization and deserialization
- Token obtain, refresh, and verify endpoints

### ✅ Phase 7: Documentation
- [x] drf-spectacular configured with:
  - Title: "Meal Planner API"
  - Description: "API for the Meal Planner Django application"
  - Version: "1.0.0"
- [x] Swagger UI accessible at `/api/v1/schema/swagger-ui/`
- [x] OpenAPI JSON schema accessible at `/api/v1/schema/`

## API Endpoints

All endpoints are under `/api/v1/` and require authentication (session or token).

### Authentication Endpoints
- `POST /api/v1/token/` - Obtain JWT access and refresh tokens
- `POST /api/v1/token/refresh/` - Refresh access token using refresh token
- `POST /api/v1/token/verify/` - Verify token validity

### Authentication Methods
The API supports **both** authentication methods:

1. **Session Authentication** (for web browsers/HTMX):
   - POST to `/accounts/login/` to establish session
   - Include `sessionid` cookie in requests

2. **Token Authentication** (for mobile apps, CLI, third-party services):
   - POST to `/api/v1/token/` to get access/refresh tokens
   - Include `Authorization: Bearer <token>` header in requests
   - Access tokens expire after 5 minutes
   - Refresh tokens expire after 1 day

### Core Resources
- `GET, POST, PUT, PATCH, DELETE /api/v1/meal-types/`
- `GET, POST, PUT, PATCH, DELETE /api/v1/shopping-categories/`
- `GET, POST, PUT, PATCH, DELETE /api/v1/stores/`
- `GET, POST, PUT, PATCH, DELETE /api/v1/store-category-orders/`
- `GET, POST, PUT, PATCH, DELETE /api/v1/ingredients/`
- `GET, POST, PUT, PATCH, DELETE /api/v1/recipe-ingredients/`

### Recipes
- `GET, POST, PUT, PATCH, DELETE /api/v1/recipes/`
  - Filtering: `?meal_type=`, `?difficulty=`, `?ace_tag=`, `?search=`

### Week Plans
- `GET, POST, PUT, PATCH, DELETE /api/v1/week-plans/`
- `POST /api/v1/week-plans/{id}/shuffle/` - Shuffle meals
- `GET /api/v1/week-plans/{id}/planned_meals/` - List planned meals

### Planned Meals
- `GET, POST, PUT, PATCH, DELETE /api/v1/planned-meals/`
- `POST /api/v1/planned-meals/{id}/toggle_pin/` - Toggle pinned status

### Shopping Lists
- `GET, POST, PUT, PATCH, DELETE /api/v1/shopping-lists/`
- `POST /api/v1/shopping-lists/{id}/generate/` - Generate from week plan
- `GET /api/v1/shopping-lists/{id}/items/` - List items

### Shopping List Items
- `GET, POST, PUT, PATCH, DELETE /api/v1/shopping-list-items/`
- `POST /api/v1/shopping-list-items/{id}/toggle_check/` - Toggle checked status

## Issues Fixed

During implementation, the following issues were identified and fixed:

1. **URL Action Naming**: The `toggle_check` action was being accessed with `toggle-check` in tests, but DRF uses underscores for action names. Fixed by updating the test to use `toggle_check`.

2. **Test Data Requirements**: The `shuffle` and `generate` actions require existing recipes with ingredients and planned meals to work correctly. Fixed by adding proper test data setup in the test classes.

## Test Results

```bash
$ uv run python manage.py test core.api.tests
Ran 51 tests in 18.033s
OK

$ uv run python manage.py test
Ran 174 tests in 42.069s
OK
```

All tests pass, including the existing 123 tests and the new 51 API tests (15 authentication tests + 11 serializer tests + 25 view tests).

## Next Steps

The API implementation is complete and fully functional. You can:

1. Start the development server: `uv run python manage.py runserver`
2. Access Swagger UI: `http://localhost:8000/api/v1/schema/swagger-ui/`
3. Access OpenAPI schema: `http://localhost:8000/api/v1/schema/`
4. Test endpoints with curl or any HTTP client

### Example Usage

The API supports **both session-based and token-based authentication**:

#### Session Authentication (Web Browsers)
```bash
# Login to establish session
curl -X POST http://localhost:8000/accounts/login/ \
  -d "username=youruser&password=yourpass" \
  --cookie-jar cookies.txt

# List all recipes using session cookie
curl http://localhost:8000/api/v1/recipes/ \
  --cookie cookies.txt

# Create a recipe using session cookie
curl -X POST http://localhost:8000/api/v1/recipes/ \
  --cookie cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Recipe", "meal_type": 1, "instructions": "Test"}'
```

#### Token Authentication (Mobile Apps, CLI, Third-Party Services)
```bash
# Get JWT tokens
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"youruser","password":"yourpass"}'

# Response:
# {
#   "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
# }

# List all recipes using access token
curl http://localhost:8000/api/v1/recipes/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Create a recipe using access token
curl -X POST http://localhost:8000/api/v1/recipes/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Recipe", "meal_type": 1, "instructions": "Test"}'

# Refresh access token when expired
curl -X POST http://localhost:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'

# Shuffle a week plan using token
curl -X POST http://localhost:8000/api/v1/week-plans/1/shuffle/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Generate shopping list using token
curl -X POST http://localhost:8000/api/v1/shopping-lists/1/generate/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Files Modified/Created

### Modified
- `mealplanner/settings.py` - Added DRF, drf-spectacular, and SimpleJWT configuration
- `mealplanner/urls.py` - Added API URL routing and JWT token endpoints
- `pyproject.toml` - Added dependencies (djangorestframework-simplejwt, pyjwt)

### Created
- `core/api/__init__.py`
- `core/api/pagination.py`
- `core/api/permissions.py`
- `core/api/serializers.py`
- `core/api/urls.py`
- `core/api/views.py`
- `core/api/tests/__init__.py`
- `core/api/tests/test_auth.py`
- `core/api/tests/test_serializers.py`
- `core/api/tests/test_views.py`
