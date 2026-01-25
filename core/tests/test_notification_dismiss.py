"""
Test dismiss notification functionality.
"""

from django.test import TestCase
from django.urls import reverse
from core.models import (
    Ingredient,
    MealType,
    PlannedMeal,
    Recipe,
    RecipeIngredient,
    ShoppingCategory,
    ShoppingList,
    Store,
    WeekPlan,
)
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class DismissNotificationTests(TestCase):
    """Test dismiss notification endpoint."""

    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Create a store
        self.store = Store.objects.create(name="Test Store", is_default=True)

        # Create a category
        self.category = ShoppingCategory.objects.create(name="Produce")

        # Create ingredient
        self.ingredient = Ingredient.objects.create(
            name="Eggs",
            category=self.category,
            default_unit="large",
            is_pantry_staple=False,
        )

        # Create meal type and recipe
        self.meal_type = MealType.objects.create(name="Dinner")
        self.recipe = Recipe.objects.create(
            name="Pancakes", meal_type=self.meal_type, instructions="Cook them"
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient, quantity="3"
        )

        # Create week plan with a meal
        self.week_plan = WeekPlan.objects.create(
            start_date=timezone.now().date(), created_by=self.user
        )
        self.planned_meal = PlannedMeal.objects.create(
            week_plan=self.week_plan, day_offset=0, recipe=self.recipe
        )

        # Generate shopping list
        self.shopping_list = ShoppingList.objects.create(
            name="Weekly Shopping",
            week_plan=self.week_plan,
            store=self.store,
            generated_at=timezone.now(),
        )

        # Log in
        self.client.login(username="testuser", password="testpass")

    def test_dismiss_endpoint_returns_empty_response(self):
        """Test that dismiss endpoint returns empty response for HTMX swap."""
        response = self.client.post(
            reverse("shopping_dismiss_notification", kwargs={"pk": self.shopping_list.pk}),
            HTTP_HX_REQUEST="true"
        )

        # Should return empty content for HTMX swap
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "")

    def test_dismiss_endpoint_does_not_modify_shopping_list(self):
        """Test that dismiss endpoint does not modify shopping list data."""
        # Get initial state
        initial_item_count = self.shopping_list.items.count()
        initial_name = self.shopping_list.name
        initial_generated_at = self.shopping_list.generated_at

        # Dismiss notification
        response = self.client.post(
            reverse("shopping_dismiss_notification", kwargs={"pk": self.shopping_list.pk}),
            HTTP_HX_REQUEST="true"
        )

        # Refresh from DB
        self.shopping_list.refresh_from_db()

        # Should not have changed
        self.assertEqual(self.shopping_list.items.count(), initial_item_count)
        self.assertEqual(self.shopping_list.name, initial_name)
        self.assertEqual(self.shopping_list.generated_at, initial_generated_at)

    def test_dismiss_endpoint_does_not_modify_meal_plan(self):
        """Test that dismiss endpoint does not modify meal plan data."""
        # Get initial state
        initial_modified_at = self.week_plan.modified_at
        initial_meal_count = self.week_plan.planned_meals.count()

        # Dismiss notification
        response = self.client.post(
            reverse("shopping_dismiss_notification", kwargs={"pk": self.shopping_list.pk}),
            HTTP_HX_REQUEST="true"
        )

        # Refresh from DB
        self.week_plan.refresh_from_db()

        # Should not have changed
        self.assertEqual(self.week_plan.modified_at, initial_modified_at)
        self.assertEqual(self.week_plan.planned_meals.count(), initial_meal_count)
