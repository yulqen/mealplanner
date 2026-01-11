"""
Test shopping list generation functionality.
"""

from django.test import TestCase
from core.services.shopping import format_regeneration_message
from core.models import (
    Ingredient,
    MealType,
    PlannedMeal,
    Recipe,
    RecipeIngredient,
    ShoppingCategory,
    ShoppingList,
    ShoppingListItem,
    Store,
    StoreCategoryOrder,
    WeekPlan,
)
from core.services.shopping import generate_shopping_list
from django.utils import timezone
from datetime import timedelta


class ShoppingListRegenerationTests(TestCase):
    """Test shopping list regeneration (replace mode)."""

    def setUp(self):
        """Set up test data for regeneration tests."""
        # Create a store
        self.store = Store.objects.create(name="Test Store", is_default=True)

        # Create categories
        self.category = ShoppingCategory.objects.create(name="Produce")
        self.store_cat_order = StoreCategoryOrder.objects.create(
            store=self.store, category=self.category, sort_order=1
        )

        # Create ingredients
        self.eggs = Ingredient.objects.create(
            name="Eggs",
            category=self.category,
            default_unit="large",
            is_pantry_staple=False,
        )
        self.flour = Ingredient.objects.create(
            name="Flour",
            category=self.category,
            default_unit="g",
            is_pantry_staple=False,
        )
        self.milk = Ingredient.objects.create(
            name="Milk",
            category=self.category,
            default_unit="L",
            is_pantry_staple=False,
        )
        self.sugar = Ingredient.objects.create(
            name="Sugar",
            category=self.category,
            default_unit="g",
            is_pantry_staple=False,
        )

        # Create meal type and recipe
        self.meal_type = MealType.objects.create(name="Dinner")
        self.recipe = Recipe.objects.create(
            name="Pancakes", meal_type=self.meal_type, instructions="Cook them"
        )

        # Add ingredients to recipe - initial quantities
        self.ri_eggs = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.eggs, quantity="3"
        )
        self.ri_flour = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.flour, quantity="500g"
        )
        self.ri_sugar = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.sugar, quantity="100g"
        )

        # Create a week plan
        self.week_plan = WeekPlan.objects.create(
            start_date=timezone.now().date(), created_by=None
        )

        # Add meal to the plan
        PlannedMeal.objects.create(
            week_plan=self.week_plan, day_offset=0, recipe=self.recipe
        )

    def test_return_changes_parameter(self):
        """Test that return_changes=True returns changes dict."""
        shopping_list, changes = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, return_changes=True
        )

        # Check that we get a tuple
        self.assertIsInstance(shopping_list, ShoppingList)
        self.assertIsInstance(changes, dict)

        # Check structure of changes dict
        self.assertIn('updated', changes)
        self.assertIn('added', changes)
        self.assertIn('removed', changes)
        self.assertIn('counts', changes)

        # For initial generation, items should be tracked (may be added or not tracked)
        # Just verify structure is correct
        self.assertIsInstance(changes['counts'], tuple)

    def test_return_changes_with_replacement(self):
        """Test that return_changes tracks updates when regenerating."""
        # Generate initial shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Update recipe ingredient quantities
        self.ri_eggs.quantity = "2"
        self.ri_eggs.save()
        self.ri_flour.quantity = "400g"
        self.ri_flour.save()

        # Regenerate and get changes
        regenerated_list, changes = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list,
            replace=True, return_changes=True
        )

        # Check changes tracked correctly (quantities should be in updated dict)
        self.assertIn('Eggs', changes['updated'])
        self.assertIn('Flour', changes['updated'])
        self.assertEqual(changes['updated']['Eggs'], ('3', '2'))
        self.assertEqual(changes['updated']['Flour'], ('500g', '400g'))

    def test_return_changes_with_additions(self):
        """Test that return_changes tracks added items."""
        # Generate initial shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Add new ingredient to recipe
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.milk, quantity="1 cup"
        )

        # Regenerate and get changes
        regenerated_list, changes = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list,
            replace=True, return_changes=True
        )

        # Check changes tracked correctly (milk should be in added dict)
        self.assertIn('Milk', changes['added'])
        self.assertEqual(changes['added']['Milk'], '1 cup')
        self.assertGreater(len(changes['added']), 0)  # At least 1 added

    def test_return_changes_with_removals(self):
        """Test that return_changes tracks removed items."""
        # Generate initial shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Remove sugar from recipe
        self.ri_sugar.delete()

        # Regenerate and get changes
        regenerated_list, changes = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list,
            replace=True, return_changes=True
        )

        # Check changes tracked correctly (sugar should be in removed dict)
        self.assertIn('Sugar', changes['removed'])
        self.assertEqual(changes['removed']['Sugar'], '100g')
        self.assertGreater(len(changes['removed']), 0)  # At least 1 removed

    def test_return_changes_mixed(self):
        """Test that return_changes tracks updates, additions, and removals."""
        # Generate initial shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Update some ingredients, add one, remove one
        self.ri_eggs.quantity = "2"
        self.ri_eggs.save()
        self.ri_sugar.delete()
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.milk, quantity="1 cup"
        )

        # Regenerate and get changes
        regenerated_list, changes = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list,
            replace=True, return_changes=True
        )

        # Check changes tracked correctly (items should be in correct dicts)
        self.assertEqual(changes['updated']['Eggs'], ('3', '2'))
        self.assertEqual(changes['added']['Milk'], '1 cup')
        self.assertEqual(changes['removed']['Sugar'], '100g')

    def test_regeneration_replaces_quantities(self):
        """Test that regenerating a list replaces quantities instead of augmenting."""
        # Generate initial shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Verify initial quantities
        initial_eggs = shopping_list.items.get(ingredient=self.eggs)
        initial_flour = shopping_list.items.get(ingredient=self.flour)

        self.assertEqual(initial_eggs.quantities, "3")
        self.assertEqual(initial_flour.quantities, "500g")

        # Update recipe ingredient quantities
        self.ri_eggs.quantity = "2"
        self.ri_eggs.save()
        self.ri_flour.quantity = "400g"
        self.ri_flour.save()

        # Regenerate shopping list with replace=True
        regenerated_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list, replace=True
        )

        # Verify quantities are replaced, not augmented
        final_eggs = regenerated_list.items.get(ingredient=self.eggs)
        final_flour = regenerated_list.items.get(ingredient=self.flour)

        self.assertEqual(final_eggs.quantities, "2")  # Should be 2, not 5 (3+2)
        self.assertEqual(final_flour.quantities, "400g")  # Should be 400g, not 900g (500g+400g)

    def test_regeneration_preserves_manual_items(self):
        """Test that regenerating preserves manual items."""
        # Generate initial shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Add a manual item
        ShoppingListItem.objects.create(
            shopping_list=shopping_list,
            ingredient=self.milk,
            name="Milk",
            category=self.category,
            quantities="2L",
            is_manual=True,
        )

        initial_count = shopping_list.items.count()

        # Regenerate shopping list with replace=True
        regenerated_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list, replace=True
        )

        # Manual item should still be there
        self.assertEqual(regenerated_list.items.count(), initial_count)
        milk_item = regenerated_list.items.get(ingredient=self.milk)
        self.assertEqual(milk_item.quantities, "2L")
        self.assertTrue(milk_item.is_manual)

    def test_regeneration_updates_pantry_status(self):
        """Test that regenerating updates pantry item status."""
        # Generate initial shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        eggs_item = shopping_list.items.get(ingredient=self.eggs)
        self.assertFalse(eggs_item.is_pantry_item)

        # Change ingredient to pantry staple
        self.eggs.is_pantry_staple = True
        self.eggs.save()

        # Regenerate shopping list
        regenerated_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list, replace=True
        )

        # Pantry status should be updated
        eggs_item = regenerated_list.items.get(ingredient=self.eggs)
        self.assertTrue(eggs_item.is_pantry_item)

    def test_regeneration_removes_deleted_recipe_ingredients(self):
        """Test that regenerating removes items whose ingredients were removed from recipes."""
        # Generate initial shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Verify initial items
        initial_count = shopping_list.items.count()

        # Remove flour from recipe
        self.ri_flour.delete()

        # Regenerate shopping list with replace=True
        regenerated_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list, replace=True
        )

        # Should have one less item
        self.assertEqual(regenerated_list.items.count(), initial_count - 1)
        self.assertTrue(regenerated_list.items.filter(ingredient=self.eggs).exists())
        self.assertFalse(regenerated_list.items.filter(ingredient=self.flour).exists())

    def test_regeneration_multiple_times(self):
        """Test that regenerating multiple times works correctly."""
        # Generate initial shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # First regeneration
        self.ri_eggs.quantity = "1"
        self.ri_eggs.save()
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list, replace=True
        )
        self.assertEqual(shopping_list.items.get(ingredient=self.eggs).quantities, "1")

        # Second regeneration
        self.ri_eggs.quantity = "4"
        self.ri_eggs.save()
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list, replace=True
        )
        self.assertEqual(shopping_list.items.get(ingredient=self.eggs).quantities, "4")

        # Third regeneration
        self.ri_eggs.quantity = "6"
        self.ri_eggs.save()
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list, replace=True
        )
        self.assertEqual(shopping_list.items.get(ingredient=self.eggs).quantities, "6")

    def test_regeneration_adds_new_recipe_ingredients(self):
        """Test that regenerating adds new ingredients added to recipes."""
        # Generate initial shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Verify initial items (eggs, flour, sugar from setUp)
        initial_count = shopping_list.items.count()
        self.assertGreaterEqual(initial_count, 2)

        # Add milk to recipe
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.milk, quantity="1 cup"
        )

        # Regenerate shopping list
        regenerated_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list, replace=True
        )

        # Milk should be added (should have initial_count + 1 items)
        self.assertEqual(regenerated_list.items.count(), initial_count + 1)
        self.assertTrue(regenerated_list.items.filter(ingredient=self.milk).exists())
        milk_item = regenerated_list.items.get(ingredient=self.milk)
        self.assertEqual(milk_item.quantities, "1 cup")

    def test_replace_false_still_augments(self):
        """Test that replace=False still augments (backward compatibility)."""
        # Generate initial shopping list
        shopping_list = ShoppingList.objects.create(
            name="Test List", week_plan=self.week_plan, store=self.store, is_active=True
        )

        # Add manual item: 2 eggs
        ShoppingListItem.objects.create(
            shopping_list=shopping_list,
            ingredient=self.eggs,
            name="Eggs",
            category=self.category,
            quantities="2",
            is_manual=True,
        )

        # Generate with replace=False (default) - should augment
        result_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list, replace=False
        )

        # Eggs should be augmented: 2 (manual) + 3 (from recipe) = 5
        eggs_item = result_list.items.get(ingredient=self.eggs)
        self.assertEqual(eggs_item.quantities, "5")


class StaleDetectionTests(TestCase):
    """Test shopping list stale detection when recipes/ingredients change."""

    def setUp(self):
        """Set up test data for stale detection tests."""
        # Create a store
        self.store = Store.objects.create(name="Test Store", is_default=True)

        # Create categories
        self.category = ShoppingCategory.objects.create(name="Produce")
        self.store_cat_order = StoreCategoryOrder.objects.create(
            store=self.store, category=self.category, sort_order=1
        )

        # Create ingredients
        self.eggs = Ingredient.objects.create(
            name="Eggs",
            category=self.category,
            default_unit="large",
            is_pantry_staple=False,
        )
        self.flour = Ingredient.objects.create(
            name="Flour",
            category=self.category,
            default_unit="g",
            is_pantry_staple=False,
        )

        # Create meal type and recipe
        self.meal_type = MealType.objects.create(name="Dinner")
        self.recipe = Recipe.objects.create(
            name="Pancakes", meal_type=self.meal_type, instructions="Cook them"
        )

        # Add ingredients to recipe
        self.ri_eggs = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.eggs, quantity="3"
        )
        self.ri_flour = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.flour, quantity="500g"
        )

        # Create a week plan
        self.week_plan = WeekPlan.objects.create(
            start_date=timezone.now().date(), created_by=None
        )

        # Add meal to the plan
        PlannedMeal.objects.create(
            week_plan=self.week_plan, day_offset=0, recipe=self.recipe
        )

    def test_stale_detection_on_recipe_edit(self):
        """Test that editing a recipe marks the shopping list as stale."""
        # Generate shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Initially not stale
        self.assertFalse(shopping_list.is_stale)

        # Capture the modified_at timestamp
        initial_modified_at = self.week_plan.modified_at

        # Update the recipe (this should trigger signal to update week_plan)
        self.recipe.name = "Fluffy Pancakes"
        self.recipe.save()

        # Refresh week_plan from database
        self.week_plan.refresh_from_db()

        # Modified_at should have been updated
        self.assertGreater(self.week_plan.modified_at, initial_modified_at)

        # Shopping list should now be stale
        self.assertTrue(shopping_list.is_stale)

    def test_stale_detection_on_ingredient_edit(self):
        """Test that editing a recipe ingredient marks the shopping list as stale."""
        # Generate shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Initially not stale
        self.assertFalse(shopping_list.is_stale)

        # Capture the modified_at timestamp
        initial_modified_at = self.week_plan.modified_at

        # Update a recipe ingredient (this should trigger signal to update week_plan)
        self.ri_eggs.quantity = "4"
        self.ri_eggs.save()

        # Refresh week_plan from database
        self.week_plan.refresh_from_db()

        # Modified_at should have been updated
        self.assertGreater(self.week_plan.modified_at, initial_modified_at)

        # Shopping list should now be stale
        self.assertTrue(shopping_list.is_stale)

    def test_stale_detection_on_ingredient_delete(self):
        """Test that deleting a recipe ingredient marks the shopping list as stale."""
        # Generate shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Initially not stale
        self.assertFalse(shopping_list.is_stale)

        # Capture the modified_at timestamp
        initial_modified_at = self.week_plan.modified_at

        # Delete a recipe ingredient (this should trigger signal to update week_plan)
        self.ri_flour.delete()

        # Refresh week_plan from database
        self.week_plan.refresh_from_db()

        # Modified_at should have been updated
        self.assertGreater(self.week_plan.modified_at, initial_modified_at)

        # Shopping list should now be stale
        self.assertTrue(shopping_list.is_stale)

    def test_stale_detection_on_ingredient_add(self):
        """Test that adding a recipe ingredient marks the shopping list as stale."""
        # Generate shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Initially not stale
        self.assertFalse(shopping_list.is_stale)

        # Capture the modified_at timestamp
        initial_modified_at = self.week_plan.modified_at

        # Add a new ingredient to the recipe
        milk = Ingredient.objects.create(
            name="Milk",
            category=self.category,
            default_unit="L",
            is_pantry_staple=False,
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=milk, quantity="1 cup"
        )

        # Refresh week_plan from database
        self.week_plan.refresh_from_db()

        # Modified_at should have been updated
        self.assertGreater(self.week_plan.modified_at, initial_modified_at)

        # Shopping list should now be stale
        self.assertTrue(shopping_list.is_stale)

    def test_regeneration_clears_stale_status(self):
        """Test that regenerating a shopping list clears the stale status."""
        # Generate shopping list
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        # Initially not stale
        self.assertFalse(shopping_list.is_stale)

        # Update recipe ingredient (makes list stale)
        self.ri_eggs.quantity = "4"
        self.ri_eggs.save()

        # Refresh shopping list
        shopping_list.refresh_from_db()

        # Should now be stale
        self.assertTrue(shopping_list.is_stale)

        # Capture generated_at before regeneration
        old_generated_at = shopping_list.generated_at

        # Regenerate shopping list
        generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list, replace=True
        )

        # Refresh shopping list
        shopping_list.refresh_from_db()

        # Generated_at should have been updated
        self.assertGreater(shopping_list.generated_at, old_generated_at)

        # Should no longer be stale
        self.assertFalse(shopping_list.is_stale)


class ChangeMessageTests(TestCase):
    """Test formatting of regeneration change messages."""

    def test_format_message_no_changes(self):
        """Test message when nothing changed."""
        changes = {
            'updated': {},
            'added': {},
            'removed': {},
            'counts': (0, 0, 0)
        }
        message = format_regeneration_message(changes)
        self.assertEqual(message, "Shopping list regenerated: no changes needed")

    def test_format_message_single_update(self):
        """Test message with one item updated."""
        changes = {
            'updated': {'Eggs': ('3', '2')},
            'added': {},
            'removed': {},
            'counts': (1, 0, 0)
        }
        message = format_regeneration_message(changes)
        self.assertEqual(message, "Shopping list regenerated: Eggs: 3 → 2")

    def test_format_message_multiple_updates(self):
        """Test message with multiple items updated."""
        changes = {
            'updated': {'Eggs': ('3', '2'), 'Flour': ('500g', '400g')},
            'added': {},
            'removed': {},
            'counts': (2, 0, 0)
        }
        message = format_regeneration_message(changes)
        self.assertEqual(message, "Shopping list regenerated: Eggs: 3 → 2, Flour: 500g → 400g")

    def test_format_message_many_updates(self):
        """Test message with many updates (shows only first 3)."""
        changes = {
            'updated': {
                'Eggs': ('3', '2'),
                'Flour': ('500g', '400g'),
                'Milk': ('1L', '2L'),
                'Sugar': ('100g', '50g'),
            },
            'added': {},
            'removed': {},
            'counts': (4, 0, 0)
        }
        message = format_regeneration_message(changes)
        # Should show first 3 updates and count for remaining
        self.assertIn("Eggs: 3 → 2", message)
        self.assertIn("Flour: 500g → 400g", message)
        self.assertIn("Milk: 1L → 2L", message)
        self.assertIn("1 more", message)
        self.assertNotIn("Sugar", message)

    def test_format_message_with_additions(self):
        """Test message including added items."""
        changes = {
            'updated': {'Eggs': ('3', '2')},
            'added': {'Milk': '1 cup'},
            'removed': {},
            'counts': (1, 1, 0)
        }
        message = format_regeneration_message(changes)
        self.assertEqual(message, "Shopping list regenerated: Eggs: 3 → 2 (1 added)")

    def test_format_message_with_removals(self):
        """Test message including removed items."""
        changes = {
            'updated': {},
            'added': {},
            'removed': {'Sugar': '100g'},
            'counts': (0, 0, 1)
        }
        message = format_regeneration_message(changes)
        self.assertEqual(message, "Shopping list regenerated: (1 removed)")

    def test_format_message_all_changes(self):
        """Test message with updates, additions, and removals."""
        changes = {
            'updated': {'Eggs': ('3', '2')},
            'added': {'Milk': '1 cup'},
            'removed': {'Sugar': '100g'},
            'counts': (1, 1, 1)
        }
        message = format_regeneration_message(changes)
        self.assertEqual(message, "Shopping list regenerated: Eggs: 3 → 2 (1 added, 1 removed)")

    def test_format_message_only_additions(self):
        """Test message with only additions."""
        changes = {
            'updated': {},
            'added': {'Milk': '1 cup', 'Eggs': '3'},
            'removed': {},
            'counts': (0, 2, 0)
        }
        message = format_regeneration_message(changes)
        self.assertEqual(message, "Shopping list regenerated: (2 added)")

    def test_format_message_only_removals(self):
        """Test message with only removals."""
        changes = {
            'updated': {},
            'added': {},
            'removed': {'Milk': '1 cup', 'Sugar': '100g'},
            'counts': (0, 0, 2)
        }
        message = format_regeneration_message(changes)
        self.assertEqual(message, "Shopping list regenerated: (2 removed)")


class ShoppingListGenerationTests(TestCase):
    """Test shopping list generation and augmentation."""

    def setUp(self):
        """Set up test data."""
        # Create a store
        self.store = Store.objects.create(name="Test Store", is_default=True)

        # Create categories
        self.category = ShoppingCategory.objects.create(name="Produce")
        self.store_cat_order = StoreCategoryOrder.objects.create(
            store=self.store, category=self.category, sort_order=1
        )

        # Create ingredients
        self.eggs = Ingredient.objects.create(
            name="Eggs",
            category=self.category,
            default_unit="large",
            is_pantry_staple=False,
        )
        self.milk = Ingredient.objects.create(
            name="Milk",
            category=self.category,
            default_unit="L",
            is_pantry_staple=False,
        )
        self.salt = Ingredient.objects.create(
            name="Salt",
            category=self.category,
            default_unit="g",
            is_pantry_staple=True,
        )

        # Create meal type and recipes
        self.meal_type = MealType.objects.create(name="Dinner")
        self.recipe1 = Recipe.objects.create(
            name="Omelette", meal_type=self.meal_type, instructions="Make it"
        )
        self.recipe2 = Recipe.objects.create(
            name="Pancakes", meal_type=self.meal_type, instructions="Cook them"
        )

        # Add ingredients to recipes
        RecipeIngredient.objects.create(
            recipe=self.recipe1, ingredient=self.eggs, quantity="2"
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe1, ingredient=self.salt, quantity="1 pinch"
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe2, ingredient=self.eggs, quantity="3"
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe2, ingredient=self.milk, quantity="1 cup"
        )

        # Create a week plan
        self.week_plan = WeekPlan.objects.create(
            start_date=timezone.now().date(), created_by=None
        )

        # Add meals to the plan
        PlannedMeal.objects.create(
            week_plan=self.week_plan, day_offset=0, recipe=self.recipe1
        )
        PlannedMeal.objects.create(
            week_plan=self.week_plan, day_offset=1, recipe=self.recipe2
        )

    def test_generate_new_shopping_list(self):
        """Test generating a new shopping list."""
        shopping_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store
        )

        self.assertEqual(shopping_list.week_plan, self.week_plan)
        self.assertEqual(shopping_list.items.count(), 3)

        # Check eggs are aggregated (2 + 3 = 5)
        eggs_item = shopping_list.items.get(ingredient=self.eggs)
        self.assertEqual(eggs_item.quantities, "5")

        # Check other items
        salt_item = shopping_list.items.get(ingredient=self.salt)
        self.assertEqual(salt_item.quantities, "1 pinch")
        self.assertTrue(salt_item.is_pantry_item)

        milk_item = shopping_list.items.get(ingredient=self.milk)
        self.assertEqual(milk_item.quantities, "1 cup")

    def test_augment_existing_shopping_list(self):
        """Test augmenting an existing shopping list."""
        # Create initial shopping list with a manual item
        shopping_list = ShoppingList.objects.create(
            name="Test List", week_plan=self.week_plan, store=self.store, is_active=True
        )

        # Add manual item: 3 eggs
        ShoppingListItem.objects.create(
            shopping_list=shopping_list,
            ingredient=self.eggs,
            name="Eggs",
            category=self.category,
            quantities="3",
            is_manual=True,
        )

        # Generate shopping list (should augment, not replace)
        result_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list
        )

        # Should be the same list
        self.assertEqual(result_list.pk, shopping_list.pk)
        self.assertEqual(result_list.items.count(), 3)

        # Eggs should be augmented: 3 (manual) + 5 (from recipes) = 8
        eggs_item = result_list.items.get(ingredient=self.eggs)
        self.assertEqual(eggs_item.quantities, "8")
        self.assertTrue(eggs_item.is_manual)  # Should still be manual

        # Check other items were added
        self.assertTrue(result_list.items.filter(ingredient=self.milk).exists())
        self.assertTrue(result_list.items.filter(ingredient=self.salt).exists())

    def test_generation_does_not_remove_items(self):
        """Test that generating a shopping list never removes items."""
        # Create initial list with an item that won't be in recipes
        shopping_list = ShoppingList.objects.create(
            name="Test List", week_plan=self.week_plan, store=self.store, is_active=True
        )

        # Add items: eggs and an extra item not in recipes
        ShoppingListItem.objects.create(
            shopping_list=shopping_list,
            ingredient=self.eggs,
            name="Eggs",
            category=self.category,
            quantities="3",
            is_manual=True,
        )
        ShoppingListItem.objects.create(
            shopping_list=shopping_list,
            ingredient=None,
            name="Chocolate",
            category=self.category,
            quantities="1 bar",
            is_manual=True,
        )

        initial_count = shopping_list.items.count()

        # Generate shopping list
        result_list = generate_shopping_list(
            week_plan=self.week_plan, store=self.store, shopping_list=shopping_list
        )

        # Should have the same or more items, never fewer
        self.assertGreaterEqual(result_list.items.count(), initial_count)

        # Chocolate should still be there
        self.assertTrue(result_list.items.filter(name="Chocolate").exists())

    def test_reusing_existing_shopping_list(self):
        """Test that generating for the same week plan reuses the existing list."""
        # Generate first time
        list1 = generate_shopping_list(week_plan=self.week_plan, store=self.store)
        list1_pk = list1.pk

        # Generate again - should reuse the same list
        list2 = generate_shopping_list(week_plan=self.week_plan, store=self.store)

        self.assertEqual(list1_pk, list2.pk)
        self.assertEqual(list1.items.count(), list2.items.count())

    def test_different_week_plans_create_different_lists(self):
        """Test that different week plans create different shopping lists."""
        # Create another week plan with the same recipes
        week_plan2 = WeekPlan.objects.create(
            start_date=timezone.now().date() + timedelta(days=7), created_by=None
        )
        PlannedMeal.objects.create(
            week_plan=week_plan2, day_offset=0, recipe=self.recipe1
        )

        list1 = generate_shopping_list(week_plan=self.week_plan, store=self.store)
        list2 = generate_shopping_list(week_plan=week_plan2, store=self.store)

        self.assertNotEqual(list1.pk, list2.pk)
        self.assertEqual(list1.week_plan, self.week_plan)
        self.assertEqual(list2.week_plan, week_plan2)
