"""
Test moving shopping list items between lists.
"""

from django.test import TestCase
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
from django.utils import timezone
from datetime import timedelta


class ShoppingListItemMoveTests(TestCase):
    """Test moving shopping list items between different shopping lists."""

    def setUp(self):
        """Set up test data for move tests."""
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

        # Create meal type and recipe
        self.meal_type = MealType.objects.create(name="Dinner")
        self.recipe = Recipe.objects.create(
            name="Pancakes", meal_type=self.meal_type, instructions="Cook them"
        )

        # Add ingredients to recipe
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.eggs, quantity="3"
        )
        RecipeIngredient.objects.create(
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

        # Create two shopping lists
        self.list_a = ShoppingList.objects.create(
            name="List A",
            week_plan=self.week_plan,
            store=self.store,
            is_active=True,
        )
        self.list_b = ShoppingList.objects.create(
            name="List B",
            week_plan=None,
            store=self.store,
            is_active=False,
        )

        # Add items to List A
        self.item_eggs = ShoppingListItem.objects.create(
            shopping_list=self.list_a,
            ingredient=self.eggs,
            name="Eggs",
            category=self.category,
            quantities="3",
            is_checked=False,
            is_manual=False,
        )
        self.item_flour = ShoppingListItem.objects.create(
            shopping_list=self.list_a,
            ingredient=self.flour,
            name="Flour",
            category=self.category,
            quantities="500g",
            is_checked=True,
            is_manual=False,
        )

    def test_move_item_from_list_a_to_list_b(self):
        """Test moving an item from List A to List B."""
        # Verify initial state
        self.assertEqual(self.list_a.items.count(), 2)
        self.assertEqual(self.list_b.items.count(), 0)

        # Move the eggs item
        self.item_eggs.shopping_list = self.list_b
        self.item_eggs.save()

        # Refresh from database
        self.item_eggs.refresh_from_db()
        self.list_a.refresh_from_db()
        self.list_b.refresh_from_db()

        # Verify the item is now in List B
        self.assertEqual(self.item_eggs.shopping_list, self.list_b)
        self.assertEqual(self.list_a.items.count(), 1)
        self.assertEqual(self.list_b.items.count(), 1)

        # Verify List A only has flour
        self.assertTrue(self.list_a.items.filter(ingredient=self.flour).exists())
        self.assertFalse(self.list_a.items.filter(ingredient=self.eggs).exists())

        # Verify List B has eggs
        self.assertTrue(self.list_b.items.filter(ingredient=self.eggs).exists())

    def test_move_preserves_quantity(self):
        """Test that moving an item preserves its quantity."""
        original_quantity = self.item_eggs.quantities

        # Move the eggs item
        self.item_eggs.shopping_list = self.list_b
        self.item_eggs.save()

        # Refresh from database
        self.item_eggs.refresh_from_db()

        # Verify quantity is preserved
        self.assertEqual(self.item_eggs.quantities, original_quantity)
        self.assertEqual(self.item_eggs.quantities, "3")

    def test_move_preserves_checked_status(self):
        """Test that moving an item preserves its checked status."""
        # Move the flour item (which is checked)
        original_checked = self.item_flour.is_checked

        self.item_flour.shopping_list = self.list_b
        self.item_flour.save()

        # Refresh from database
        self.item_flour.refresh_from_db()

        # Verify checked status is preserved
        self.assertEqual(self.item_flour.is_checked, original_checked)
        self.assertTrue(self.item_flour.is_checked)

    def test_move_preserves_all_attributes(self):
        """Test that moving an item preserves all its attributes."""
        # Store all original attributes
        original_attrs = {
            'ingredient': self.item_eggs.ingredient,
            'name': self.item_eggs.name,
            'category': self.item_eggs.category,
            'quantities': self.item_eggs.quantities,
            'is_checked': self.item_eggs.is_checked,
            'is_manual': self.item_eggs.is_manual,
            'is_pantry_override': self.item_eggs.is_pantry_override,
            'is_pantry_item': self.item_eggs.is_pantry_item,
            'is_starred': self.item_eggs.is_starred,
        }

        # Move the eggs item
        self.item_eggs.shopping_list = self.list_b
        self.item_eggs.save()

        # Refresh from database
        self.item_eggs.refresh_from_db()

        # Verify all attributes are preserved
        self.assertEqual(self.item_eggs.ingredient, original_attrs['ingredient'])
        self.assertEqual(self.item_eggs.name, original_attrs['name'])
        self.assertEqual(self.item_eggs.category, original_attrs['category'])
        self.assertEqual(self.item_eggs.quantities, original_attrs['quantities'])
        self.assertEqual(self.item_eggs.is_checked, original_attrs['is_checked'])
        self.assertEqual(self.item_eggs.is_manual, original_attrs['is_manual'])
        self.assertEqual(self.item_eggs.is_pantry_override, original_attrs['is_pantry_override'])
        self.assertEqual(self.item_eggs.is_pantry_item, original_attrs['is_pantry_item'])
        self.assertEqual(self.item_eggs.is_starred, original_attrs['is_starred'])

    def test_move_removes_source_list_association(self):
        """Test that moving an item removes it from the source list's items queryset."""
        # Verify item is in List A's items
        self.assertIn(self.item_eggs, self.list_a.items.all())

        # Move the eggs item
        self.item_eggs.shopping_list = self.list_b
        self.item_eggs.save()

        # Refresh from database
        self.item_eggs.refresh_from_db()
        self.list_a.refresh_from_db()

        # Verify item is no longer in List A's items
        self.assertNotIn(self.item_eggs, self.list_a.items.all())

        # Verify item is in List B's items
        self.assertIn(self.item_eggs, self.list_b.items.all())

    def test_move_multiple_items_sequentially(self):
        """Test moving multiple items one after another."""
        # Add an item to List B first
        item_milk = ShoppingListItem.objects.create(
            shopping_list=self.list_b,
            ingredient=self.milk,
            name="Milk",
            category=self.category,
            quantities="1L",
            is_checked=False,
            is_manual=True,
        )

        self.assertEqual(self.list_a.items.count(), 2)
        self.assertEqual(self.list_b.items.count(), 1)

        # Move eggs from A to B
        self.item_eggs.shopping_list = self.list_b
        self.item_eggs.save()

        self.assertEqual(self.list_a.items.count(), 1)
        self.assertEqual(self.list_b.items.count(), 2)

        # Move flour from A to B
        self.item_flour.shopping_list = self.list_b
        self.item_flour.save()

        self.assertEqual(self.list_a.items.count(), 0)
        self.assertEqual(self.list_b.items.count(), 3)

        # Verify all items are in List B
        self.assertEqual(self.list_b.items.count(), 3)
        self.assertTrue(self.list_b.items.filter(ingredient=self.eggs).exists())
        self.assertTrue(self.list_b.items.filter(ingredient=self.flour).exists())
        self.assertTrue(self.list_b.items.filter(ingredient=self.milk).exists())
