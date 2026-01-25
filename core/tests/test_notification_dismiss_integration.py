"""
Integration tests for dismiss notification functionality.
"""

from django.test import TestCase, Client
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


class DismissNotificationIntegrationTests(TestCase):
    """Integration tests for dismiss notification functionality."""

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

    def test_dismiss_button_in_html_response(self):
        """Test that dismiss button is present in HTML response."""
        # Make list stale
        self.week_plan.modified_at = timezone.now()
        self.week_plan.save()

        # Get shopping list page
        response = self.client.get(reverse("shopping_list", kwargs={"pk": self.shopping_list.pk}))

        # Should contain dismiss button with proper attributes
        self.assertContains(response, 'hx-post="%s"' % reverse("shopping_dismiss_notification", kwargs={"pk": self.shopping_list.pk}))
        self.assertContains(response, 'hx-target="#notification-banner"')
        self.assertContains(response, 'aria-label="Dismiss notification"')
        self.assertContains(response, '<svg')  # X icon

    def test_dismiss_removes_notification_from_dom(self):
        """Test that dismiss action removes notification from DOM."""
        # Make list stale
        self.week_plan.modified_at = timezone.now()
        self.week_plan.save()

        # Verify dismiss button exists
        response = self.client.get(reverse("shopping_list", kwargs={"pk": self.shopping_list.pk}))
        self.assertContains(response, "Meal plan has been updated")

        # Dismiss notification - this is a client-side HTMX action
        # The button uses hx-target="#notification-banner" and hx-swap="outerHTML"
        # so clicking it will replace the entire banner with empty content
        response = self.client.post(
            reverse("shopping_dismiss_notification", kwargs={"pk": self.shopping_list.pk}),
            HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")

        # Reload page - notification should still be there (client-side dismissal)
        # because we're not doing server-side persistence
        # The notification was removed from DOM via HTMX swap-delete
        # but Django re-renders it on subsequent GET request
        response = self.client.get(reverse("shopping_list", kwargs={"pk": self.shopping_list.pk}))
        self.assertEqual(response.status_code, 200)
        # Since there's no server-side dismissal tracking, the notification is still rendered
        self.assertContains(response, "Meal plan has been updated")
