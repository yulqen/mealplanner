# Shopping List Item Enhancement: Auto-Create Ingredients

## Overview

When adding items to the shopping list, if the user types an item name that doesn't exist in the database, automatically create it as an Ingredient instead of adding it as an ad hoc item. This will improve data consistency and prevent duplicate items with slight name variations.

## Current Implementation

### Files Involved
- `core/views.py` - `shopping_add()` function (line 732)
- `core/templates/core/shopping_list.html` - Add item form (lines 74-122)
- `core/templates/components/shopping_item_autocomplete.html` - Autocomplete dropdown
- `core/services/shopping.py` - `generate_shopping_list()` function

### Current Behavior
When a user adds an item to the shopping list:
1. If `ingredient_id` is provided → Uses existing Ingredient
2. If no `ingredient_id` → Creates `ShoppingListItem` with `ingredient=None` (ad hoc item)

## Problem Statement

Ad hoc items (those with `ingredient=None`) have several issues:
1. Cannot aggregate quantities properly in `generate_shopping_list()` (lines 143-147 filter by `ingredient__isnull=False`)
2. Create potential for duplicates with slight name variations (e.g., "Milk" vs "milk")
3. Break the intended data model where all items reference Ingredients
4. Cannot benefit from Ingredient metadata (default_unit, category, is_pantry_staple)
5. May appear in wrong category if category is not selected

## Proposed Solutions

### Approach 1: Category Required (Simpler)

**Implementation:**
- Make category field required in shopping list form
- Add case-insensitive ingredient lookup
- If ingredient doesn't exist, create it with provided category
- Set default values: `is_pantry_staple=False`, `default_unit=""`

**Pros:**
- Simpler implementation
- No new UI components needed
- Follows Django best practices (required fields)

**Cons:**
- Requires user to always select category (may be annoying)
- No validation feedback if similar ingredients exist

**Code Changes:**
```python
# core/views.py:shopping_add()
name = request.POST.get("name", "").strip()
category_id = request.POST.get("category")
quantities = request.POST.get("quantities", "").strip()

if name and category_id:
    # Case-insensitive lookup
    ingredient = Ingredient.objects.filter(
        name__iexact=name
    ).first()

    if not ingredient:
        category = ShoppingCategory.objects.get(pk=category_id)
        ingredient = Ingredient.objects.create(
            name=name,
            category=category,
            is_pantry_staple=False,
        )

    ShoppingListItem.objects.create(
        shopping_list=shopping_list_obj,
        ingredient=ingredient,
        name=ingredient.name,
        category=ingredient.category,
        quantities=quantities,
        is_manual=True,
    )
```

---

### Approach 2: Modal for Missing Category (Better UX)

**Implementation:**
- If category is empty and ingredient doesn't exist, show inline creation modal
- Modal allows user to select required category
- Similar to existing ingredient creation flow in recipe forms
- Case-insensitive ingredient lookup
- Show warning if similar ingredient exists

**Pros:**
- Follows existing pattern (recipe form ingredient creation)
- Better UX - only ask for category when needed
- Can show validation warnings for near-duplicates
- More discoverable for users

**Cons:**
- More complex implementation
- Requires new modal component
- More JavaScript to handle

**Code Changes Required:**

1. **New View: `shopping_item_create_inline()`**
   ```python
   @login_required
   def shopping_item_create_inline(request, pk):
       """Create new ingredient inline from shopping list form."""
       shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)

       if request.method == "POST":
           name = request.POST.get("name", "").strip()
           category_id = request.POST.get("category")

           # Check for similar ingredients (case-insensitive)
           similar = Ingredient.objects.filter(name__iexact=name)

           if similar.exists():
               context = {
                   "name": name,
                   "similar_ingredients": similar,
               }
               return render(request, "components/shopping_item_duplicate_warning.html", context)

           if name and category_id:
               category = get_object_or_404(ShoppingCategory, pk=category_id)
               ingredient = Ingredient.objects.create(
                   name=name,
                   category=category,
                   is_pantry_staple=False,
               )
               # Return JavaScript to update form
               return render(
                   request,
                   "components/shopping_item_created.html",
                   {"ingredient": ingredient}
               )

       # GET request - show form
       name = request.GET.get("name", "")
       context = {
           "name": name,
           "categories": ShoppingCategory.objects.all(),
           "shopping_list_pk": pk,
       }
       return render(request, "components/shopping_item_inline_form.html", context)
   ```

2. **Update `shopping_add()` view:**
   ```python
   if name:
       ingredient = None
       category = None

       # Try to find existing ingredient (case-insensitive)
       if ingredient_id:
           ingredient = Ingredient.objects.filter(pk=ingredient_id).first()
       else:
           ingredient = Ingredient.objects.filter(name__iexact=name).first()

       # If no ingredient and no category, return modal
       if not ingredient:
           if not category_id:
               # Return inline creation form
               context = {
                   "name": name,
                   "categories": ShoppingCategory.objects.all(),
                   "quantities": quantities,
                   "shopping_list": shopping_list_obj,
               }
               return render(request, "components/shopping_item_inline_form.html", context)
           else:
               # Create new ingredient
               category = ShoppingCategory.objects.get(pk=category_id)
               ingredient = Ingredient.objects.create(
                   name=name,
                   category=category,
                   is_pantry_staple=False,
               )
       else:
           category = ingredient.category

       ShoppingListItem.objects.create(
           shopping_list=shopping_list_obj,
           ingredient=ingredient,
           name=ingredient.name,
           category=category,
           quantities=quantities,
           is_manual=True,
       )
   ```

3. **New Templates:**
   - `components/shopping_item_inline_form.html` - Modal form for creating ingredient
   - `components/shopping_item_created.html` - JavaScript to update form with new ingredient
   - `components/shopping_item_duplicate_warning.html` - Warning if similar ingredient exists

4. **New URL:**
   ```python
   path(
       "shopping/<int:pk>/create-item-inline/",
       views.shopping_item_create_inline,
       name="shopping_item_create_inline",
   ),
   ```

5. **JavaScript Updates in `shopping_list.html`:**
   - Handle HTMX responses from inline form
   - Update hidden `ingredient_id` field after creation
   - Show duplicate warnings

---

## Edge Cases & Considerations

### 1. Case Sensitivity
**Issue:** "Milk" vs "milk" vs "MILK"

**Solution:** Use `name__iexact` for case-insensitive lookups. When creating new ingredient, preserve user's input case but check for existing with case-insensitive match.

### 2. Category Requirement
**Issue:** `Ingredient.category` is required (PROTECT constraint), but shopping list form currently allows empty category

**Solution:**
- Approach 1: Make category required in form (HTML5 `required`)
- Approach 2: Show modal when category is needed

### 3. Duplicate Prevention
**Issue:** Users might create "milk" when "Milk" already exists

**Solution:** Show warning modal with list of similar ingredients before creating new one.

### 4. Backward Compatibility
**Issue:** Existing `ShoppingListItem` records with `ingredient=None`

**Solution:** No migration needed. These records will continue to work. Future items will always have ingredient.

### 5. Pantry Staple Flag
**Issue:** New ingredients need `is_pantry_staple` value

**Solution:** Default to `False` for user-created ingredients. Can be edited later in ingredient management.

### 6. Default Unit
**Issue:** `default_unit` can be blank

**Solution:** Leave blank for user-created ingredients. Not critical for shopping list functionality.

### 7. Shopping List Regeneration
**Issue:** When regenerating list with `generate_shopping_list()`, newly created ingredients must work correctly

**Solution:** The function already handles ingredients correctly (lines 133-156). New ingredients work the same way.

### 8. Autocomplete Behavior
**Issue:** Autocomplete should find newly created ingredients

**Solution:** Autocomplete uses `name__icontains` query (line 788), so new ingredients will appear immediately.

### 9. Multiple Shopping Lists
**Issue:** Same ingredient might exist on multiple lists

**Solution:** This is the desired behavior. Ingredients are shared across shopping lists, items are per-list.

### 10. Ingredient Deletion
**Issue:** If an ingredient used in shopping lists is deleted, `ShoppingListItem.ingredient` becomes NULL (SET_NULL constraint)

**Solution:** This is already handled by `on_delete=SET_NULL`. The item remains in the list with just the name.

### 11. Concurrency Issues
**Issue:** Two users create "milk" ingredient simultaneously

**Solution:** Wrap in transaction, use `get_or_create()` with case-insensitive lookup:
```python
ingredient, created = Ingredient.objects.get_or_create(
    name__iexact=name,
    defaults={'name': name, 'category': category, 'is_pantry_staple': False}
)
```

### 12. Character Encoding
**Issue:** Special characters in ingredient names

**Solution:** Django ORM handles Unicode properly. No special handling needed.

---

## Testing Requirements

### Unit Tests (`core/tests/test_shopping.py`)

1. **Test auto-creation of ingredient when adding to shopping list**
   ```python
   def test_auto_create_ingredient_when_adding_to_shopping_list(self):
       """Adding a non-existent ingredient creates it in the database."""
       # Count ingredients before
       initial_count = Ingredient.objects.count()

       # Add item to shopping list
       response = self.client.post(
           reverse('shopping_add', args=[self.shopping_list.pk]),
           {'name': 'Butter', 'category': self.category.pk, 'quantities': '1 pack'}
       )

       # Ingredient should be created
       self.assertEqual(Ingredient.objects.count(), initial_count + 1)
       self.assertTrue(Ingredient.objects.filter(name='Butter').exists())

       # Shopping list item should reference the ingredient
       item = self.shopping_list.items.get(name='Butter')
       self.assertIsNotNone(item.ingredient)
       self.assertEqual(item.ingredient.name, 'Butter')
   ```

2. **Test case-insensitive ingredient lookup**
   ```python
   def test_case_insensitive_ingredient_lookup(self):
       """Ingredient lookup should be case-insensitive."""
       # Create ingredient "Milk"
       Ingredient.objects.create(name='Milk', category=self.category)

       # Add "milk" to shopping list
       self.client.post(
           reverse('shopping_add', args=[self.shopping_list.pk]),
           {'name': 'milk', 'category': self.category.pk, 'quantities': '1L'}
       )

       # Should use existing "Milk", not create new "milk"
       self.assertEqual(Ingredient.objects.filter(name='Milk').count(), 1)
       self.assertFalse(Ingredient.objects.filter(name='milk').exists())

       item = self.shopping_list.items.get(name='Milk')
       self.assertEqual(item.ingredient.name, 'Milk')
   ```

3. **Test duplicate prevention warning** (Approach 2)
   ```python
   def test_duplicate_warning_when_similar_ingredient_exists(self):
       """Should warn when creating ingredient similar to existing."""
       Ingredient.objects.create(name='Milk', category=self.category)

       # Try to create "milk"
       response = self.client.get(
           reverse('shopping_item_create_inline', args=[self.shopping_list.pk]),
           {'name': 'milk'}
       )

       self.assertContains(response, 'Similar ingredients already exist')
       self.assertContains(response, 'Milk')
   ```

4. **Test shopping list regeneration with newly created ingredients**
   ```python
   def test_regeneration_with_newly_created_ingredients(self):
       """Generate shopping list with manually added items works correctly."""
       # Add item manually (creates ingredient)
       self.client.post(
           reverse('shopping_add', args=[self.shopping_list.pk]),
           {'name': 'Cheese', 'category': self.category.pk, 'quantities': '2 blocks'}
       )

       # Add recipe with same ingredient
       cheese = Ingredient.objects.get(name='Cheese')
       self.recipe.ingredients.add(
           RecipeIngredient.objects.create(recipe=self.recipe, ingredient=cheese, quantity='1 block')
       )

       # Regenerate shopping list
       shopping_list = generate_shopping_list(
           week_plan=self.week_plan,
           shopping_list=self.shopping_list
       )

       # Should aggregate quantities: 2 (manual) + 1 (recipe) = 3
       cheese_item = shopping_list.items.get(ingredient=cheese)
       self.assertEqual(cheese_item.quantities, '3')
   ```

5. **Test category required** (Approach 1)
   ```python
   def test_category_required_when_adding_item(self):
       """Category should be required when adding new ingredient."""
       response = self.client.post(
           reverse('shopping_add', args=[self.shopping_list.pk]),
           {'name': 'Sugar', 'category': '', 'quantities': '1kg'}
       )

       # Should not create item or ingredient
       self.assertEqual(self.shopping_list.items.count(), 0)
       self.assertFalse(Ingredient.objects.filter(name='Sugar').exists())
   ```

### Integration Tests

1. **Test full flow: autocomplete → select/add → verify ingredient created**
2. **Test shopping list page after multiple adds**
3. **Test HTMX responses and form clearing**
4. **Test error handling and validation messages**

---

## Migration Requirements

No database migration required. This is purely application logic change.

However, consider adding a data migration if you want to clean up existing ad hoc items:

```python
# Optional: Convert existing ad hoc items to ingredients
def convert_ad_hoc_items(apps, schema_editor):
    ShoppingListItem = apps.get_model('core', 'ShoppingListItem')
    Ingredient = apps.get_model('core', 'Ingredient')
    ShoppingCategory = apps.get_model('core', 'ShoppingCategory')

    # Get "Other" category or create it
    other_category, _ = ShoppingCategory.objects.get_or_create(name='Other')

    for item in ShoppingListItem.objects.filter(ingredient=None):
        # Create ingredient if it doesn't exist
        ingredient, created = Ingredient.objects.get_or_create(
            name=item.name,
            defaults={
                'category': item.category or other_category,
                'is_pantry_staple': False,
            }
        )
        item.ingredient = ingredient
        item.save()
```

---

## Performance Considerations

1. **Autocomplete queries** (line 788): Already uses `select_related("category")` and limits to 8 results. No change needed.

2. **Ingredient lookup in `shopping_add()`:** Use `get_or_create()` to handle concurrent requests safely.

3. **Shopping list regeneration:** No performance impact. Already optimized with bulk operations.

---

## Recommended Approach

**Recommendation: Approach 2 (Modal for Missing Category)**

**Reasons:**
1. Follows existing patterns in the codebase (recipe form ingredient creation)
2. Better user experience - only interrupt when necessary
3. Allows for duplicate prevention warnings
4. More extensible for future enhancements
5. Provides better data quality through validation

**Implementation Priority:**
1. High: Case-insensitive ingredient lookup
2. High: Auto-create ingredient when doesn't exist
3. Medium: Duplicate warning modal
4. Low: Clean up existing ad hoc items (optional)

---

## Success Criteria

- ✅ All new shopping list items reference an Ingredient (no `ingredient=None`)
- ✅ Case-insensitive ingredient lookup prevents duplicates
- ✅ Users are prompted to select category for new ingredients
- ✅ Existing functionality continues to work (backward compatible)
- ✅ Shopping list regeneration correctly aggregates quantities
- ✅ All tests pass (unit and integration)

---

## Related Files

- `core/views.py:732` - `shopping_add()` function
- `core/services/shopping.py:79` - `generate_shopping_list()` function
- `core/templates/core/shopping_list.html:74` - Add item form
- `core/templates/components/shopping_item_autocomplete.html` - Autocomplete dropdown
- `core/models.py:264` - `ShoppingListItem` model
- `core/models.py:66` - `Ingredient` model
- `core/tests/test_shopping.py` - Test file
- `core/urls.py:70` - URL patterns
