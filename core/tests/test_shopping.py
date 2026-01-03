"""
Test shopping list generation functionality.
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
from core.services.shopping import generate_shopping_list
from django.utils import timezone
from datetime import timedelta


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
