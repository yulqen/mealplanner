# Architecture & Data Models

## App Structure

Single `core` app with modular organization:

```
core/
├── models.py
├── views/
│   ├── recipes.py         # Recipe CRUD and listing
│   ├── ingredients.py     # Ingredient management
│   ├── plans.py           # WeekPlan and meal shuffling
│   ├── shopping.py        # Shopping list generation and updates
│   └── settings_views.py  # App settings/stores
├── services/
│   ├── shuffle.py         # Meal plan generation algorithm
│   └── shopping.py        # Shopping list aggregation
├── templates/core/
│   └── *.html             # Full page templates
└── templates/components/
    └── *.html             # HTMX partials for swaps
```

## Key Data Models

### Recipes & Ingredients

- **Recipe** → has many RecipeIngredients → references Ingredients
- **Ingredient** → belongs to ShoppingCategory, can be marked as pantry staple (excluded from shopping lists)
- **RecipeIngredient** → join model with quantity and unit

### Meal Planning

- **MealType** — Categories: Rice, Pasta, Potato (used for shuffle algorithm diversity)
- **WeekPlan** → has 7 PlannedMeals (one per day, day_offset 0-6)
- **PlannedMeal** → links Recipe to a day in the WeekPlan

### Shopping

- **ShoppingList** → has items, references Store for category ordering
- **ShoppingListItem** → individual ingredient with quantity, unit, is_checked status
- **ShoppingCategory** — Fruit & Veg, Dairy, Tinned, Cereals, Bread, Baking, Household, Frozen
- **Store** → supermarket with custom aisle ordering
- **StoreCategoryOrder** — defines the aisle sequence per category per store

## Business Logic

### Shuffle Algorithm (`services/shuffle.py`)

Generates a random week plan ensuring:
- No consecutive days have recipes of the same MealType
- All selected recipes are used evenly
- Algorithm respects meal type distribution

### Shopping List Generation (`services/shopping.py`)

1. Aggregates all ingredients from the current WeekPlan's recipes
2. Deduplicates by ingredient (sums quantities)
3. Excludes pantry staple ingredients
4. Orders items by store-specific StoreCategoryOrder

**Real-time sync**: Shopping list updates (checkbox toggles) are polled every 5 seconds via HTMX, allowing multi-device synchronization.

## Database Design Notes

- **SQLite** — sufficient for family use, no complex queries
- **Timestamps** — Most models include `created_at` and `updated_at`
- **Soft deletes** — Consider for audit trails (recipes, ingredients)
- **Indexing** — Keep category lookups fast for shopping list generation

## Relationships at a Glance

```
MealType (Rice, Pasta, Potato)
    ↓ (categorizes)
Recipe ← RecipeIngredient → Ingredient → ShoppingCategory
    ↓ (used in)
PlannedMeal ← WeekPlan
    ↓ (ingredients become)
ShoppingListItem ← ShoppingList → Store → StoreCategoryOrder
```
