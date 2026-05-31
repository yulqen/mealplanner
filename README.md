# Meal Planner

A family meal planning application built with Django, HTMX, and Tailwind CSS.

## Local Development

### Prerequisites
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- **Tailwind CLI binary**: Download via:
  ```bash
  curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 && chmod +x tailwindcss-linux-x64 && mv tailwindcss-linux-x64 tailwindcss
  ```
  *(Note: Adjust URL for non-Linux platforms)*

### Running the Application

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Database setup**:
   ```bash
   uv run manage.py migrate
   uv run manage.py seed_data
   ```

3. **Start the development server**:
   ```bash
   uv run manage.py runserver
   ```

4. **Watch for CSS changes** (in a separate terminal):
   ```bash
   make css-watch
   ```

### CSS Build Commands

- `make css`: Performs a one-time minified build of `styles.css`.
- `make css-watch`: Watches `input.css` and all templates for changes and rebuilds CSS automatically.

## API Access

The Meal Planner includes a RESTful API with comprehensive endpoints for all models.

### Authentication

The API supports **both session-based and token-based (JWT) authentication**:

#### Session Authentication (Web Browsers)
```bash
# Login to establish session
curl -X POST http://localhost:8000/accounts/login/ \
  -d "username=youruser&password=yourpass" \
  --cookie-jar cookies.txt

# Use session cookie for API requests
curl http://localhost:8000/api/v1/recipes/ \
  --cookie cookies.txt
```

#### Token Authentication (Mobile Apps, CLI, Third-Party Services)

**Important**: Always include `-H "Accept: application/json"` to get JSON responses instead of HTML.

```bash
# Get JWT tokens (note: Accept header is required for JSON response)
curl -s -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"username":"youruser","password":"yourpass"}'

# Response includes access and refresh tokens:
# {
#   "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
# }

# Use access token for API requests
curl -s http://localhost:8000/api/v1/recipes/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Accept: application/json"

# Refresh access token when expired
curl -s -X POST http://localhost:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

### CLI Usage Examples (Bash)

For convenient CLI usage, save the token in a variable and reuse it:

```bash
# Login and save token to variable
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"username":"matt","password":"euShuuZog1ahfaiVa2"}' | jq -r '.access')

# Now use $TOKEN for subsequent requests
curl -s http://localhost:8000/api/v1/recipes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"

# List all recipes with pretty printing
curl -s http://localhost:8000/api/v1/recipes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'

# Create a new recipe
curl -s -X POST http://localhost:8000/api/v1/recipes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "name": "My New Recipe",
    "meal_type": 1,
    "difficulty": 2,
    "instructions": "Step 1: Do this. Step 2: Do that."
  }'

# Get a specific recipe
curl -s http://localhost:8000/api/v1/recipes/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'

# Update a recipe
curl -s -X PUT http://localhost:8000/api/v1/recipes/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"name": "Updated Recipe Name"}'

# Delete a recipe
curl -s -X DELETE http://localhost:8000/api/v1/recipes/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"
```

### Week Plan Examples

```bash
# Assuming $TOKEN is set from login above

# List all week plans
curl -s http://localhost:8000/api/v1/week-plans/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'

# Create a new week plan
curl -s -X POST http://localhost:8000/api/v1/week-plans/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"start_date": "2026-06-01"}'

# Shuffle meals for a week plan (custom action)
curl -s -X POST http://localhost:8000/api/v1/week-plans/1/shuffle/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"

# Get planned meals for a week plan
curl -s http://localhost:8000/api/v1/week-plans/1/planned_meals/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'
```

### Shopping List Examples

```bash
# Assuming $TOKEN is set from login above

# List all shopping lists
curl -s http://localhost:8000/api/v1/shopping-lists/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'

# Generate shopping list from a week plan
curl -s -X POST http://localhost:8000/api/v1/shopping-lists/1/generate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"week_plan": 1, "store": 1}'

# Get items for a shopping list
curl -s http://localhost:8000/api/v1/shopping-lists/1/items/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'

# Toggle check status on an item
curl -s -X POST http://localhost:8000/api/v1/shopping-list-items/1/toggle_check/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"
```

### Filtering Examples

```bash
# Filter recipes by meal type
curl -s "http://localhost:8000/api/v1/recipes/?meal_type=1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'

# Filter recipes by difficulty
curl -s "http://localhost:8000/api/v1/recipes/?difficulty=2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'

# Search recipes by name
curl -s "http://localhost:8000/api/v1/recipes/?search=chicken" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'

# Combine filters
curl -s "http://localhost:8000/api/v1/recipes/?meal_type=1&difficulty=2&search=pasta" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.'
```

### Token Management Examples

```bash
# Get both access and refresh tokens
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"username":"matt","password":"euShuuZog1ahfaiVa2"}')

# Extract both tokens
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access')
REFRESH_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.refresh')

# Use access token
curl -s http://localhost:8000/api/v1/recipes/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/json"

# When access token expires, refresh it
NEW_ACCESS_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{\"refresh\":\"$REFRESH_TOKEN\"}" | jq -r '.access')

# Verify a token is valid
curl -s -X POST http://localhost:8000/api/v1/token/verify/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{\"token\":\"$ACCESS_TOKEN\"}"
```

### API Documentation

- **Swagger UI**: `http://localhost:8000/api/v1/schema/swagger-ui/`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/schema/`

### API Endpoints

All endpoints are under `/api/v1/` and require authentication. See [API_IMPLEMENTATION_STATUS.md](API_IMPLEMENTATION_STATUS.md) for complete endpoint documentation.

#### Quick Reference

| Resource | Endpoint | Methods |
|----------|----------|---------|
| Meal Types | `/api/v1/meal-types/` | GET, POST, PUT, PATCH, DELETE |
| Shopping Categories | `/api/v1/shopping-categories/` | GET, POST, PUT, PATCH, DELETE |
| Stores | `/api/v1/stores/` | GET, POST, PUT, PATCH, DELETE |
| Ingredients | `/api/v1/ingredients/` | GET, POST, PUT, PATCH, DELETE |
| Recipes | `/api/v1/recipes/` | GET, POST, PUT, PATCH, DELETE |
| Week Plans | `/api/v1/week-plans/` | GET, POST, PUT, PATCH, DELETE |
| Planned Meals | `/api/v1/planned-meals/` | GET, POST, PUT, PATCH, DELETE |
| Shopping Lists | `/api/v1/shopping-lists/` | GET, POST, PUT, PATCH, DELETE |
| Shopping List Items | `/api/v1/shopping-list-items/` | GET, POST, PUT, PATCH, DELETE |

#### Custom Actions

| Action | Endpoint | Method |
|--------|----------|--------|
| Shuffle week plan | `/api/v1/week-plans/{id}/shuffle/` | POST |
| Generate shopping list | `/api/v1/shopping-lists/{id}/generate/` | POST |
| Toggle pin on meal | `/api/v1/planned-meals/{id}/toggle_pin/` | POST |
| Toggle check on item | `/api/v1/shopping-list-items/{id}/toggle_check/` | POST |
| List planned meals | `/api/v1/week-plans/{id}/planned_meals/` | GET |
| List shopping items | `/api/v1/shopping-lists/{id}/items/` | GET |

#### Token Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/token/` | POST | Obtain access and refresh tokens |
| `/api/v1/token/refresh/` | POST | Refresh access token |
| `/api/v1/token/verify/` | POST | Verify token validity |
