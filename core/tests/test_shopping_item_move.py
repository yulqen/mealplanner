"""
Test moving shopping list items between lists.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
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


class ShoppingItemMoveViewTests(TestCase):
    """Test the view for moving shopping list items."""

    def setUp(self):
        """Set up test data for view tests."""
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="testpass")

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
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.eggs, quantity="3"
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.flour, quantity="500g"
        )

        # Create a week plan
        self.week_plan = WeekPlan.objects.create(
            start_date=timezone.now().date(), created_by=self.user
        )

        # Add meal to the plan
        PlannedMeal.objects.create(
            week_plan=self.week_plan, day_offset=0, recipe=self.recipe
        )

        # Create three shopping lists
        self.list_a = ShoppingList.objects.create(
            name="List A",
            week_plan=self.week_plan,
            store=self.store,
            is_active=True,
            created_by=self.user,
        )
        self.list_b = ShoppingList.objects.create(
            name="List B",
            week_plan=None,
            store=self.store,
            is_active=False,
            created_by=self.user,
        )
        self.list_c = ShoppingList.objects.create(
            name="List C",
            week_plan=None,
            store=self.store,
            is_active=False,
            created_by=self.user,
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

        # Create a test client
        self.client = Client()
        self.client.login(username="testuser", password="testpass")

    def test_get_request_returns_move_modal_html(self):
        """Test that GET request returns move modal HTML."""
        url = reverse("shopping_item_move", kwargs={"pk": self.list_a.pk, "item_pk": self.item_eggs.pk})
        response = self.client.get(url)

        # Should return HTML
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")

        # Should contain modal structure
        self.assertContains(response, "Move Item")

    def test_get_dropdown_excludes_current_list(self):
        """Test that the dropdown excludes the current list."""
        url = reverse("shopping_item_move", kwargs={"pk": self.list_a.pk, "item_pk": self.item_eggs.pk})
        response = self.client.get(url)

        # List A (the current list) should NOT be in the dropdown
        self.assertNotContains(response, f'value="{self.list_a.pk}"')

        # List B and List C should be in the dropdown
        self.assertContains(response, f'value="{self.list_b.pk}"')
        self.assertContains(response, f'value="{self.list_c.pk}"')

    def test_post_request_successfully_moves_item(self):
        """Test that POST request successfully moves item."""
        url = reverse("shopping_item_move", kwargs={"pk": self.list_a.pk, "item_pk": self.item_eggs.pk})

        # Verify initial state
        self.assertEqual(self.list_a.items.count(), 2)
        self.assertEqual(self.list_b.items.count(), 0)

        # POST request to move item
        response = self.client.post(url, {"destination_list": self.list_b.pk})

        # Should redirect or return success
        self.assertEqual(response.status_code, 200)

        # Refresh from database
        self.item_eggs.refresh_from_db()
        self.list_a.refresh_from_db()
        self.list_b.refresh_from_db()

        # Verify item was moved
        self.assertEqual(self.item_eggs.shopping_list, self.list_b)
        self.assertEqual(self.list_a.items.count(), 1)
        self.assertEqual(self.list_b.items.count(), 1)

        # Verify attributes are preserved
        self.assertEqual(self.item_eggs.quantities, "3")
        self.assertFalse(self.item_eggs.is_checked)

    def test_response_includes_htmx_triggers(self):
        """Test that response includes HTMX triggers for UI update."""
        url = reverse("shopping_item_move", kwargs={"pk": self.list_a.pk, "item_pk": self.item_eggs.pk})

        # Simulate HTMX request
        response = self.client.post(
            url,
            {"destination_list": self.list_b.pk},
            HTTP_HX_REQUEST="true"
        )

        # Should return HTML (the updated items list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")

    def test_post_requires_authentication(self):
        """Test that POST requires authentication."""
        # Logout
        self.client.logout()

        url = reverse("shopping_item_move", kwargs={"pk": self.list_a.pk, "item_pk": self.item_eggs.pk})
        response = self.client.post(url, {"destination_list": self.list_b.pk})

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_get_requires_authentication(self):
        """Test that GET requires authentication."""
        # Logout
        self.client.logout()

        url = reverse("shopping_item_move", kwargs={"pk": self.list_a.pk, "item_pk": self.item_eggs.pk})
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_post_with_invalid_destination(self):
        """Test POST with invalid destination list."""
        url = reverse("shopping_item_move", kwargs={"pk": self.list_a.pk, "item_pk": self.item_eggs.pk})
        response = self.client.post(url, {"destination_list": 99999})

        # Should return error (404 since get_object_or_404 is used)
        self.assertEqual(response.status_code, 404)

        # Item should not be moved
        self.item_eggs.refresh_from_db()
        self.assertEqual(self.item_eggs.shopping_list, self.list_a)

    def test_get_when_no_other_lists_exist(self):
        """Test GET when user has only one shopping list."""
        # Delete other lists
        self.list_b.delete()
        self.list_c.delete()

        url = reverse("shopping_item_move", kwargs={"pk": self.list_a.pk, "item_pk": self.item_eggs.pk})
        response = self.client.get(url)

        # Should still return the modal with a message about no other lists
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No other shopping lists")

    def test_post_when_no_other_lists_exist(self):
        """Test POST when user has only one shopping list."""
        # Delete other lists
        self.list_b.delete()
        self.list_c.delete()

        url = reverse("shopping_item_move", kwargs={"pk": self.list_a.pk, "item_pk": self.item_eggs.pk})
        response = self.client.post(url, {"destination_list": self.list_a.pk})

        # Should return error
        self.assertEqual(response.status_code, 400)

        # Item should not be moved
        self.item_eggs.refresh_from_db()
        self.assertEqual(self.item_eggs.shopping_list, self.list_a)
