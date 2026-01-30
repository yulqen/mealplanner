# Frontend & HTMX Patterns

## Stack

- **Django Templates** — server-side rendering (Jinja2 syntax)
- **HTMX** — lightweight interactivity without JavaScript
- **Tailwind CSS** — utility-first styling via standalone CLI
- **No Node.js** — Tailwind runs as a binary, configured in `Makefile`

## Template Organization

```
templates/
├── core/
│   ├── base.html              # Root layout with nav, header
│   ├── recipe_list.html       # Recipe browse page
│   ├── recipe_detail.html     # Single recipe
│   ├── week_plan.html         # Weekly meal plan view
│   ├── shopping_list.html     # Shopping list page
│   └── settings.html          # Stores, categories config
└── components/
    ├── recipe_filters.html    # Filter form partial
    ├── recipe_card.html       # Card for list view
    ├── week_grid.html         # Meal grid partial
    ├── shopping_item.html     # Checkbox + quantity
    └── ...                    # Other reusable partials
```

## Common HTMX Patterns

### 1. Recipe List Filters (No Reload)

```html
<form hx-get="/recipes/" hx-target="#recipe-list" hx-trigger="change">
  <input type="text" name="search" placeholder="Search...">
  <select name="meal_type">
    <option value="">All Types</option>
    {% for mt in meal_types %}<option>{{ mt }}</option>{% endfor %}
  </select>
</form>

<div id="recipe-list">
  {% include "components/recipe_card.html" %}
</div>
```

View returns only the `#recipe-list` div contents.

### 2. Week Plan Shuffle & Assign

```html
<!-- Shuffle button (replaces entire week grid) -->
<button hx-post="/plans/shuffle/" 
        hx-target="#week-grid" 
        hx-swap="outerHTML">
  🔀 Shuffle Plan
</button>

<!-- Assign meal to specific day (replace single day cell) -->
<div id="day-1" class="day-cell">
  <button hx-get="/plans/assign/?day=1" 
          hx-target="#day-1" 
          hx-swap="outerHTML">
    {{ current_recipe }}
  </button>
</div>
```

### 3. Shopping List Checkbox Sync (Polling)

```html
<div id="shopping-items">
  {% for item in shopping_list.items.all %}
    <div class="item">
      <input type="checkbox" 
             name="item-{{ item.id }}"
             hx-post="/shopping/toggle/"
             hx-vals='{"item_id": {{ item.id }}}'
             hx-trigger="change"
             hx-target="this"
             hx-swap="outerHTML swap:1s"
             {% if item.is_checked %}checked{% endif %}>
      <span>{{ item.ingredient }} × {{ item.quantity }}</span>
    </div>
  {% endfor %}
</div>

<!-- Poll for updates every 5 seconds (multi-device sync) -->
<div hx-trigger="every 5s" 
     hx-get="/shopping/sync/" 
     hx-target="#shopping-items" 
     hx-swap="innerHTML">
</div>
```

### 4. Ingredient Autocomplete with Inline Creation

During recipe editing, ingredient autocomplete allows:

```html
<input type="text" 
       id="ingredient-search"
       hx-get="/ingredients/search/?q="
       hx-trigger="keyup changed delay:300ms"
       hx-target="#ingredient-suggestions"
       hx-include="[name='meal_type_filter']"
       name="ingredient_name">

<div id="ingredient-suggestions">
  <!-- Results populate here -->
</div>

<!-- Or create new if not found -->
<button hx-post="/ingredients/create/" 
        hx-vals='{"name": document.getElementById("ingredient-search").value}'>
  Create New
</button>
```

## Styling Conventions

### Tailwind Configuration

Edit `tailwind.config.js` for custom theme/colors. Run `make css-watch` during development.

### Component Classes

- Use Tailwind utilities directly in templates
- Extract repeated patterns into Django template includes
- Avoid custom CSS; use `@apply` in stylesheet only when necessary

Example:

```html
<!-- Instead of custom .btn class, use utilities -->
<button class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
  Action
</button>
```

## Response Strategies

- **Partial returns** — Return only the changed fragment (e.g., `#recipe-list`)
- **OOB swaps** — Use `hx-swap="innerHTML"` for batch updates
- **Polling** — Use `hx-trigger="every Ns"` for multi-device sync on shopping lists
- **Swap timing** — Use `hx-swap="outerHTML swap:1s"` to add visual feedback delays

## Performance Tips

1. **Minimize template includes** — Each include adds processing time
2. **Cache aggregate queries** — Shopping list generation queries ingredients; consider caching on the WeekPlan
3. **Lazy-load large lists** — Use HTMX pagination for 50+ items
4. **Index foreign keys** — Database queries for plan/shopping list generation need fast lookups

## Testing Frontend Logic

Frontend is mostly server-side rendering + HTMX attributes. Test:

- View responses return correct partial templates
- HTMX target/trigger attributes are correct
- State changes (e.g., is_checked) are persisted in DB

Use Django test client with assertions on response content.
