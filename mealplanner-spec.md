# Meal Planner Application Specification

## Overview

A family meal planning web application to replace a decade-old Trello workflow. The app manages recipes, generates weekly meal plans, and produces store-specific shopping lists.

**Target users**: A family of four (two adults, two children) with equal permissions.

**Hosting**: Self-hosted on Debian server with nginx.

---

## Core Requirements Summary

1. **Recipe database** with meal type categorisation (Rice, Pasta, Potato) and optional difficulty rating (1-3)
2. **Weekly meal planning** with manual assignment and random "shuffle" feature
3. **Shopping list generation** with ingredient aggregation, store-specific ordering, and real-time tick-off sync
4. **User authentication** for four family members with equal permissions
5. **Recipe statistics** showing usage history (times made, last made date)

---

## Technology Stack

| Component | Technology | Notes |
|-----------|------------|-------|
| Backend | Django 5.x | Python, built-in auth |
| Database | SQLite | Simple, sufficient for family use |
| Frontend | Django templates + HTMX + Tailwind CSS | No JS build step |
| Real-time sync | HTMX polling | Simple polling every 5s, no WebSockets |
| CSS | Tailwind CLI | Standalone binary, no Node.js required |
| Hosting | nginx + gunicorn | Standard Django deployment |

---

## Data Models

### MealType

Categorises recipes by their primary carbohydrate/base.

```python
class MealType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    colour = models.CharField(max_length=7, default="#6B7280")  # Hex colour for UI
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
```

**Initial data**: Rice, Pasta, Potato

---

### ShoppingCategory

Intrinsic category for ingredients (what type of product it is).

```python
class ShoppingCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Shopping categories"
    
    def __str__(self):
        return self.name
```

**Initial data**: Fruit & Veg, Dairy, Tinned, Cereals, Bread, Baking, Household, Frozen

---

### Store

Represents a supermarket with its own aisle ordering.

```python
class Store(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Ensure only one default store
        if self.is_default:
            Store.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
```

**Initial data**: Tesco (default), Morrisons

---

### StoreCategoryOrder

Maps shopping categories to sort order for each store.

```python
class StoreCategoryOrder(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='category_orders')
    category = models.ForeignKey(ShoppingCategory, on_delete=models.CASCADE)
    sort_order = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ['store', 'category']
        ordering = ['store', 'sort_order']
    
    def __str__(self):
        return f"{self.store.name}: {self.category.name} ({self.sort_order})"
```

**Initial data for Tesco**: Fruit & Veg=1, Dairy=2, Tinned=3, Cereals=4, Bread=5, Baking=6, Household=7, Frozen=8

**Initial data for Morrisons**: Define based on actual store layout (can be configured later).

---

### Ingredient

A distinct ingredient that can be used in recipes.

```python
class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(ShoppingCategory, on_delete=models.PROTECT, related_name='ingredients')
    is_pantry_staple = models.BooleanField(default=False, help_text="If true, excluded from shopping lists by default")
    default_unit = models.CharField(max_length=30, blank=True, help_text="e.g., 'g', 'ml', 'medium', 'tin'")
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
```

---

### Recipe

A meal recipe with ingredients and instructions.

```python
class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
    ]
    
    name = models.CharField(max_length=200)
    meal_type = models.ForeignKey(MealType, on_delete=models.PROTECT, related_name='recipes')
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, null=True, blank=True)
    instructions = models.TextField(help_text="Markdown supported")
    is_archived = models.BooleanField(default=False, help_text="Hidden from active recipe lists")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def times_made(self):
        """Count how many times this recipe has been in a meal plan."""
        return self.planned_meals.count()
    
    def last_made(self):
        """Return the most recent date this recipe was planned."""
        last_plan = self.planned_meals.select_related('week_plan').order_by('-week_plan__start_date').first()
        if last_plan:
            return last_plan.actual_date()
        return None
```

---

### RecipeIngredient

Join table linking recipes to ingredients with quantities.

```python
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name='recipe_ingredients')
    quantity = models.CharField(max_length=50, help_text="Free text, e.g., '2', '400g', 'a handful'")
    
    class Meta:
        unique_together = ['recipe', 'ingredient']
        ordering = ['ingredient__name']
    
    def __str__(self):
        return f"{self.quantity} {self.ingredient.name}"
```

---

### WeekPlan

A meal plan for a specific week.

```python
class WeekPlan(models.Model):
    start_date = models.DateField(unique=True, help_text="Should be a Sunday or Monday depending on preference")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Week of {self.start_date.strftime('%d %b %Y')}"
```

---

### PlannedMeal

A single meal assigned to a day within a week plan.

```python
class PlannedMeal(models.Model):
    week_plan = models.ForeignKey(WeekPlan, on_delete=models.CASCADE, related_name='planned_meals')
    day_offset = models.PositiveSmallIntegerField(help_text="0=start_date, 1=start_date+1 day, etc.")
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True, related_name='planned_meals')
    note = models.CharField(max_length=200, blank=True, help_text="e.g., 'Eating out', 'Leftovers'")
    
    class Meta:
        unique_together = ['week_plan', 'day_offset']
        ordering = ['week_plan', 'day_offset']
    
    def actual_date(self):
        """Return the actual date for this planned meal."""
        from datetime import timedelta
        return self.week_plan.start_date + timedelta(days=self.day_offset)
    
    def __str__(self):
        date_str = self.actual_date().strftime('%a %d %b')
        if self.recipe:
            return f"{date_str}: {self.recipe.name}"
        return f"{date_str}: {self.note or 'No meal'}"
```

---

### ShoppingList

A shopping list generated from a week plan (or manual).

```python
class ShoppingList(models.Model):
    name = models.CharField(max_length=100, default="Shopping List")
    week_plan = models.ForeignKey(WeekPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='shopping_lists')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="The current shopping list in use")
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Ensure only one active shopping list
        if self.is_active:
            ShoppingList.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.created_at.strftime('%d %b %Y')})"
```

---

### ShoppingListItem

An item on a shopping list.

```python
class ShoppingListItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, help_text="For manual items without an ingredient link")
    category = models.ForeignKey(ShoppingCategory, on_delete=models.SET_NULL, null=True)
    quantities = models.TextField(help_text="Aggregated quantities, e.g., '400g, 200g' or '2, 1'")
    is_checked = models.BooleanField(default=False)
    is_pantry_override = models.BooleanField(default=False, help_text="Manually added despite being a pantry staple")
    
    class Meta:
        ordering = ['shopping_list', 'category', 'name']
    
    def __str__(self):
        return f"{self.name}: {self.quantities}"
```

---

## URL Structure

```
/                               # Home - redirect to current week plan or recipe list
/accounts/login/                # Django auth login
/accounts/logout/               # Django auth logout

/recipes/                       # Recipe list with filters (meal type, difficulty, search)
/recipes/new/                   # Create new recipe
/recipes/<id>/                  # View recipe (clean, mobile-friendly cooking view)
/recipes/<id>/edit/             # Edit recipe
/recipes/<id>/delete/           # Delete recipe (confirmation)

/ingredients/                   # Ingredient list with category management
/ingredients/new/               # Create ingredient (inline/modal preferred)
/ingredients/<id>/edit/         # Edit ingredient

/plans/                         # List of week plans (history)
/plans/new/                     # Create new week plan (pick start date)
/plans/<id>/                    # View/edit week plan
/plans/<id>/shuffle/            # HTMX endpoint: shuffle meals for this plan
/plans/<id>/assign/<day>/       # HTMX endpoint: assign recipe to day

/shopping/                      # Current active shopping list
/shopping/generate/<plan_id>/   # Generate shopping list from week plan
/shopping/add/                  # HTMX endpoint: add manual item
/shopping/check/<item_id>/      # HTMX endpoint: toggle item checked (WebSocket broadcast)
/shopping/clear/                # Clear all items (with confirmation)

/settings/                      # App settings
/settings/stores/               # Manage stores and category ordering
/settings/categories/           # Manage shopping categories
/settings/meal-types/           # Manage meal types
```

---

## Key Views and Logic

### Recipe List View (`/recipes/`)

**Features**:
- Filter by meal type (dropdown or pills)
- Filter by difficulty (1-3 or "any")
- Search by name
- Show stats: times made, last made date
- Sort options: name, times made, last made
- "Add Recipe" button prominent

**HTMX**: Filters update the list without full page reload.

---

### Recipe Detail View (`/recipes/<id>/`)

**Purpose**: Clean, mobile-optimised cooking view.

**Layout**:
- Recipe name as heading
- Meal type badge, difficulty indicator
- Ingredients list (clear, readable)
- Instructions rendered from Markdown to HTML
- Stats at bottom: times made, last made
- Edit button (icon, not prominent)

**Mobile considerations**:
- Large, readable text
- No unnecessary chrome
- Ingredients should be easy to reference while cooking

---

### Recipe Create/Edit View (`/recipes/new/`, `/recipes/<id>/edit/`)

**Fields**:
- Name (text input)
- Meal type (dropdown)
- Difficulty (optional dropdown: Easy/Medium/Hard)
- Instructions (textarea, Markdown supported, with preview toggle)
- Ingredients (dynamic list):
  - Ingredient (autocomplete from existing, or create new inline)
  - Quantity (free text)
  - Add/remove buttons

**Ingredient autocomplete with inline creation**:
- As user types, show matching ingredients via HTMX (debounced, ~300ms)
- Dropdown appears below input showing matches
- If no match, show "Create '[typed text]' as new ingredient" option
- Selecting "Create new" expands an inline form:
  - Ingredient name (pre-filled with typed text)
  - Category (dropdown, required)
  - Is pantry staple (checkbox)
  - Default unit (optional text)
  - [Save] [Cancel] buttons
- On save, ingredient is created and immediately selected for the recipe
- No page navigation required - stays in recipe edit flow

---

### Week Plan View (`/plans/<id>/`)

**Layout**:
- Week header showing date range
- 7 rows (or 6, depending on how many days), one per day:
  - Day name and date
  - Assigned recipe (or empty/note)
  - Meal type badge if recipe assigned
  - "Change" button to pick different recipe
  - "Clear" button to remove recipe
- "Shuffle" button (prominent) - regenerates all meals randomly
- "Generate Shopping List" button

**HTMX interactions**:
- Shuffle button replaces meal assignments via HTMX
- Change/Clear buttons update individual days
- Recipe picker appears as modal or inline dropdown

**Recipe picker**:
- Searchable list of recipes
- Filtered by meal type if enforcing variety (optional)
- Shows meal type badge for each

---

### Shuffle Algorithm

```python
def shuffle_meals(week_plan, num_days=7):
    """
    Assign random recipes to each day, ensuring no consecutive days
    have the same meal type.
    
    Args:
        week_plan: WeekPlan instance
        num_days: Number of days to fill (default 7)
    
    Returns:
        List of PlannedMeal instances (not yet saved)
    """
    from random import choice
    
    # Get all active recipes grouped by meal type
    recipes_by_type = {}
    for meal_type in MealType.objects.all():
        recipes = list(Recipe.objects.filter(meal_type=meal_type, is_archived=False))
        if recipes:
            recipes_by_type[meal_type.id] = recipes
    
    if not recipes_by_type:
        return []
    
    planned_meals = []
    previous_type_id = None
    
    for day_offset in range(num_days):
        # Get available types (excluding previous day's type)
        available_type_ids = [
            type_id for type_id in recipes_by_type.keys()
            if type_id != previous_type_id
        ]
        
        if not available_type_ids:
            # Fallback: only one meal type exists, allow repeat
            available_type_ids = list(recipes_by_type.keys())
        
        # Pick random type, then random recipe from that type
        chosen_type_id = choice(available_type_ids)
        chosen_recipe = choice(recipes_by_type[chosen_type_id])
        
        planned_meal = PlannedMeal(
            week_plan=week_plan,
            day_offset=day_offset,
            recipe=chosen_recipe
        )
        planned_meals.append(planned_meal)
        previous_type_id = chosen_type_id
    
    return planned_meals
```

---

### Shopping List Generation

```python
def generate_shopping_list(week_plan, store):
    """
    Generate a shopping list from a week plan.
    
    Aggregates ingredients across all recipes, respects pantry staples,
    and orders by store-specific category order.
    
    Args:
        week_plan: WeekPlan instance
        store: Store instance
    
    Returns:
        ShoppingList instance with items
    """
    # Collect all recipe ingredients from planned meals
    ingredient_quantities = {}  # {ingredient_id: [list of quantity strings]}
    
    for planned_meal in week_plan.planned_meals.select_related('recipe').all():
        if not planned_meal.recipe:
            continue
        
        for ri in planned_meal.recipe.recipe_ingredients.select_related('ingredient').all():
            ing = ri.ingredient
            
            # Skip pantry staples
            if ing.is_pantry_staple:
                continue
            
            if ing.id not in ingredient_quantities:
                ingredient_quantities[ing.id] = {
                    'ingredient': ing,
                    'quantities': []
                }
            ingredient_quantities[ing.id]['quantities'].append(ri.quantity)
    
    # Create shopping list
    shopping_list = ShoppingList.objects.create(
        name=f"Shopping for {week_plan}",
        week_plan=week_plan,
        store=store,
        is_active=True
    )
    
    # Get store category ordering
    category_order = {
        sco.category_id: sco.sort_order
        for sco in store.category_orders.all()
    }
    
    # Create items
    items = []
    for data in ingredient_quantities.values():
        ing = data['ingredient']
        quantities = data['quantities']
        
        # Aggregate quantities as comma-separated string
        aggregated = ', '.join(quantities)
        
        item = ShoppingListItem(
            shopping_list=shopping_list,
            ingredient=ing,
            name=ing.name,
            category=ing.category,
            quantities=aggregated
        )
        items.append(item)
    
    # Bulk create
    ShoppingListItem.objects.bulk_create(items)
    
    return shopping_list
```

---

### Shopping List View (`/shopping/`)

**Layout**:
- Store selector at top (switches ordering)
- Grouped by category (in store order)
- Each item shows:
  - Checkbox (large, touch-friendly)
  - Ingredient name
  - Quantities
- Checked items: struck through, moved to bottom or greyed out
- "Add item" input at bottom
- "Clear all" button (with confirmation)

**Near-real-time sync via HTMX polling**:
- Shopping list view polls for updates every 3-5 seconds
- Use `hx-trigger="every 5s"` on the list container
- Check/uncheck sends HTMX request, updates local view immediately
- Other clients pick up changes on next poll cycle
- Simple, no WebSocket infrastructure required
- Acceptable latency for in-store use (both users typically shopping together)

---

### Add Manual Shopping Item

When adding a manual item:
1. Show autocomplete for existing ingredients
2. If ingredient selected, use its category
3. If new text (not an ingredient), prompt for category
4. Add to list immediately

This allows adding things like "Birthday cake" that aren't recipe ingredients.

---

## Wireframe Descriptions

### Recipe List Page

```
┌─────────────────────────────────────────────────────────┐
│  🍽️ Meal Planner                    [User ▼] [Logout]  │
├─────────────────────────────────────────────────────────┤
│  Recipes   Plans   Shopping   Settings                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [+ Add Recipe]                                         │
│                                                         │
│  Filters: [All Types ▼] [Any Difficulty ▼] [Search...] │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🍝 Spaghetti Bolognese              Pasta | ●●○ │   │
│  │ Made 12 times · Last: 15 Dec 2024               │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🍚 Chicken Fried Rice                Rice | ●○○ │   │
│  │ Made 8 times · Last: 22 Dec 2024                │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🥔 Shepherd's Pie                  Potato | ●●● │   │
│  │ Made 5 times · Last: 1 Dec 2024                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Recipe Detail Page (Cooking View)

```
┌─────────────────────────────────────────────────────────┐
│  ← Back                                         [Edit]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Spaghetti Bolognese                                    │
│  ━━━━━━━━━━━━━━━━━━━                                    │
│  🍝 Pasta  ·  ●●○ Medium                                │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│  INGREDIENTS                                            │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  • 500g beef mince                                      │
│  • 1 onion, diced                                       │
│  • 2 cloves garlic                                      │
│  • 400g tinned tomatoes                                 │
│  • 2 tbsp tomato puree                                  │
│  • 300g spaghetti                                       │
│  • Salt and pepper                                      │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│  METHOD                                                 │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  1. Brown the mince in a large pan over high heat.     │
│     Break it up as it cooks.                           │
│                                                         │
│  2. Add the onion and garlic, cook until softened.     │
│                                                         │
│  3. Add the tinned tomatoes and tomato puree.          │
│     Simmer for 20 minutes.                             │
│                                                         │
│  4. Cook spaghetti according to packet instructions.   │
│                                                         │
│  5. Serve sauce over pasta. Season to taste.           │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│  Made 12 times · Last: 15 Dec 2024                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Week Plan Page

```
┌─────────────────────────────────────────────────────────┐
│  🍽️ Meal Planner                    [User ▼] [Logout]  │
├─────────────────────────────────────────────────────────┤
│  Recipes   Plans   Shopping   Settings                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Week of 29 Dec 2024 - 4 Jan 2025                       │
│                                                         │
│  [🎲 Shuffle All]    [🛒 Generate Shopping List]        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SUN 29 Dec                                      │   │
│  │ 🍝 Spaghetti Bolognese              [Change][✕] │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ MON 30 Dec                                      │   │
│  │ 🥔 Shepherd's Pie                   [Change][✕] │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ TUE 31 Dec                                      │   │
│  │ 🍚 Chicken Fried Rice               [Change][✕] │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ WED 1 Jan                                       │   │
│  │ (empty)                        [+ Assign meal]  │   │
│  └─────────────────────────────────────────────────┘   │
│  ...                                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Shopping List Page

```
┌─────────────────────────────────────────────────────────┐
│  🍽️ Meal Planner                    [User ▼] [Logout]  │
├─────────────────────────────────────────────────────────┤
│  Recipes   Plans   Shopping   Settings                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Shopping List                    Store: [Tesco ▼]      │
│  Week of 29 Dec 2024                                    │
│                                                         │
│  ─── 1. FRUIT & VEG ──────────────────────────────────  │
│                                                         │
│  [ ] Onion                                    1, 2      │
│  [ ] Garlic                             2 cloves, 3     │
│  [ ] Carrots                                  500g      │
│                                                         │
│  ─── 2. DAIRY ────────────────────────────────────────  │
│                                                         │
│  [ ] Butter                                   50g       │
│  [ ] Cheese, cheddar                         200g       │
│                                                         │
│  ─── 3. TINNED ───────────────────────────────────────  │
│                                                         │
│  [✓] Tomatoes, tinned                   400g, 400g      │
│                                                         │
│  ─── ✓ DONE ──────────────────────────────────────────  │
│                                                         │
│  [✓] ~~Milk~~                               1 pint      │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│  [Add item...                              ] [+ Add]    │
│                                                         │
│  [Clear All]                                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Foundation (MVP)

**Goal**: Basic recipe management and manual meal planning.

1. Django project setup with auth
2. Models: MealType, Recipe (without ingredients)
3. Views: Recipe list, create, edit, detail
4. Basic Tailwind styling
5. User accounts (create 4 users manually via admin)

**Deliverable**: Can add recipes, view them, basic auth works.

---

### Phase 2: Ingredients

**Goal**: Full recipe ingredient management.

1. Models: ShoppingCategory, Ingredient, RecipeIngredient
2. Ingredient CRUD views
3. Recipe edit with ingredient management (dynamic form)
4. Ingredient autocomplete (HTMX)

**Deliverable**: Recipes have structured ingredients.

---

### Phase 3: Meal Planning

**Goal**: Weekly meal plans with shuffle.

1. Models: WeekPlan, PlannedMeal
2. Week plan list and create views
3. Week plan detail with day assignments
4. Shuffle algorithm
5. HTMX for shuffle and assign actions
6. Recipe stats (times made, last made)

**Deliverable**: Can create meal plans, shuffle works, stats visible.

---

### Phase 4: Shopping Lists

**Goal**: Generate and use shopping lists with near-real-time sync.

1. Models: Store, StoreCategoryOrder, ShoppingList, ShoppingListItem
2. Shopping list generation from week plan
3. Shopping list view with category grouping
4. Check/uncheck items (HTMX)
5. HTMX polling for sync (every 5 seconds)
6. Manual item addition
7. Store switching (reorders categories)
8. Clear all functionality

**Deliverable**: Shopping lists work, store-specific ordering, sync between devices via polling.

---

### Phase 5: Polish

**Goal**: Production-ready refinements.

1. Mobile styling refinements
2. Empty states and helpful messages
3. Confirmation dialogs (delete, clear all)
4. Error handling
5. Performance (select_related, prefetch_related)
6. Deployment: gunicorn + nginx config

---

### Phase 6: Future - Real-time WebSocket Sync (Optional)

**Goal**: Upgrade from polling to instant sync (if polling feels too slow).

1. Install and configure Django Channels
2. WebSocket consumer for shopping list updates
3. Broadcast on check/uncheck
4. Client-side WebSocket handling
5. Reconnection logic
6. Update nginx config for WebSocket proxying (daphne)

**Note**: This is a future enhancement. HTMX polling in Phase 4 is likely sufficient for family use.

---

## Django Project Structure

```
mealplanner/
├── manage.py
├── mealplanner/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                     # Main app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── recipes.py
│   │   ├── ingredients.py
│   │   ├── plans.py
│   │   ├── shopping.py
│   │   └── settings_views.py
│   ├── forms.py
│   ├── urls.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── shuffle.py
│   │   └── shopping.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── core/
│   │   │   ├── recipe_list.html
│   │   │   ├── recipe_detail.html
│   │   │   ├── recipe_form.html
│   │   │   ├── week_plan.html
│   │   │   ├── shopping_list.html
│   │   │   └── ...
│   │   └── components/       # HTMX partials
│   │       ├── recipe_card.html
│   │       ├── meal_slot.html
│   │       ├── shopping_item.html
│   │       ├── ingredient_autocomplete.html
│   │       ├── ingredient_inline_form.html
│   │       └── ...
│   ├── static/
│   │   └── core/
│   │       └── css/
│   │           ├── input.css     # Tailwind input
│   │           └── styles.css    # Tailwind output (generated)
│   └── management/
│       └── commands/
│           └── seed_data.py  # Initial data command
├── templates/
│   └── registration/
│       └── login.html
├── staticfiles/              # Collected static files (production)
├── requirements.txt
└── tailwind.config.js        # Tailwind configuration
```

---

## Key Dependencies

```
# requirements.txt

Django>=5.0
whitenoise>=6.0
markdown>=3.5
python-dotenv>=1.0
gunicorn>=21.0
```

For Tailwind, use the **Tailwind CLI standalone binary** (no Node.js required):
- Download from: https://github.com/tailwindlabs/tailwindcss/releases
- Run: `./tailwindcss -i input.css -o output.css --watch`

This keeps the stack simple with no Node.js/npm dependencies.

---

## Security Considerations

1. **Authentication**: Django's built-in session auth is sufficient
2. **CSRF**: Django handles automatically with `{% csrf_token %}`
3. **HTTPS**: Configure nginx with Let's Encrypt
4. **Session security**: Set `SESSION_COOKIE_SECURE = True` in production
5. **Allowed hosts**: Configure `ALLOWED_HOSTS` properly
6. **WebSocket auth**: Channels middleware handles session auth

---

## Deployment Notes

**nginx configuration** proxies HTTP requests to gunicorn:

```nginx
server {
    listen 80;
    server_name mealplanner.yourdomain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Gunicorn systemd service** (example):

```ini
[Unit]
Description=Meal Planner Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/mealplanner
ExecStart=/path/to/venv/bin/gunicorn mealplanner.wsgi:application --bind 127.0.0.1:8000 --workers 2

[Install]
WantedBy=multi-user.target
```

**Note**: If you later add WebSocket support (Phase 6), you'll need to add daphne and configure nginx to proxy `/ws/` paths separately.

---

## Future Enhancements (Out of Scope for V1)

These are not part of the initial build but noted for future consideration:

- **WebSocket real-time sync** for shopping list (upgrade from polling)
- Recipe scaling (adjust quantities for different servings)
- Recipe photos
- Nutritional information
- Favourites/ratings
- Recipe import from URLs
- Shared family calendar integration
- Leftovers tracking
- Meal prep notes
- Cost tracking

---

## Summary

This specification defines a Django-based meal planning application with:

- **Recipe management** with meal types, difficulty, and structured ingredients
- **Inline ingredient creation** during recipe editing for smooth workflow
- **Flexible week planning** with random shuffle (no consecutive same-type)
- **Smart shopping lists** with store-specific ordering and near-real-time sync via HTMX polling
- **Simple, mobile-first UI** using HTMX and Tailwind CSS (no Node.js required)
- **Minimal infrastructure** - Django + SQLite + gunicorn, straightforward deployment

The phased implementation approach allows for early usability while building toward the complete feature set. WebSocket-based real-time sync is deferred to a future phase if polling proves insufficient.
