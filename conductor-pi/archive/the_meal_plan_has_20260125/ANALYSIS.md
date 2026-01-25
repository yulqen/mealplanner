# Analysis: Meal Plan Update Notification

## Notification Location
- **Template**: `core/templates/core/shopping_list.html` (lines 8-24)
- **Context**: Shown on the shopping list page when `is_stale` is True

## Current HTML Structure

```html
<!-- Stale List Warning -->
{% if is_stale and shopping_list.week_plan %}
<div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md shadow-sm">
    <div class="flex">
        <div class="flex-shrink-0">
            <!-- Warning SVG icon -->
        </div>
        <div class="ml-3 flex-1">
            <p class="text-sm text-yellow-700">
                <strong>Meal plan has been updated.</strong>
                Your shopping list may be out of date.
            </p>
        </div>
        <div class="ml-3">
            <a href="{% url 'shopping_generate' shopping_list.week_plan.pk %}"
               class="...">
                Regenerate List
            </a>
        </div>
    </div>
</div>
{% endif %}
```

## HTMX Patterns in the Application

The template uses these HTMX patterns:
- `hx-post` - For form submissions
- `hx-get` - For fetching content
- `hx-target` - Specifies where to swap content
- `hx-swap` - Specifies how to swap (innerHTML, outerHTML, etc.)
- `hx-trigger` - Triggers actions (e.g., `every 5s` for polling)
- `hx-on::after-request` - Event handling after requests

## Notification State Tracking Mechanism

### Server-side Tracking (Current Implementation)

The notification state is computed **dynamically** on each page load:

1. **is_stale property** (`ShoppingList` model, line 276):
   ```python
   @property
   def is_stale(self):
       """Check if the shopping list is stale (meal plan was modified after list was generated)."""
       if not self.week_plan or not self.generated_at:
           return False
       return self.week_plan.modified_at > self.generated_at
   ```

2. **WeekPlan.modified_at** field:
   - Uses `auto_now=True` to automatically update on save
   - Represents when the plan was last modified

3. **Signal-based updates** (lines 322-365):
   - Recipe saves/deletes trigger updates to affected WeekPlans
   - RecipeIngredient saves/deletes trigger updates to affected WeekPlans

### Key Finding

**There is NO session-based dismissal tracking.** The notification visibility is purely computed from:
- `shopping_list.generated_at` (when list was last generated)
- `week_plan.modified_at` (when plan was last changed)

### Implications for Dismiss Functionality

To implement dismissal, we need to:
1. Add a mechanism to track dismissed state (likely session-based)
2. Modify the `is_stale` check or add a separate `should_show_notification` check
3. Ensure the dismissed state is reset when the meal plan changes

### When modified_at Updates

The `WeekPlan.modified_at` is updated when:
1. Any PlannedMeal is saved (via auto_now on WeekPlan when related objects trigger cascades)
2. Recipe is saved/deleted (via signal)
3. RecipeIngredient is saved/deleted (via signal)

### Triggering Actions

The following user actions should trigger notification re-appearance:
- Shuffling meals (`plan_shuffle` view)
- Assigning a recipe (`plan_assign` view)
- Assigning supplementary meals (`plan_assign_supplementary` view)
- Editing/deleting recipes
- Editing/deleting recipe ingredients
