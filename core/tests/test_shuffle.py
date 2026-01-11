"""
Test shuffle functionality including pinned meals.
"""

from datetime import date
from django.test import TestCase
from core.models import (
    MealType,
    PlannedMeal,
    Recipe,
    WeekPlan,
)
from core.services.shuffle import shuffle_meals


class ShuffleServiceTests(TestCase):
    """Test the shuffle service functionality."""

    def setUp(self):
        """Set up test data for shuffle tests."""
        # Create meal types
        self.pasta_type = MealType.objects.create(name="Pasta", colour="#FF6B6B")
        self.rice_type = MealType.objects.create(name="Rice", colour="#4ECDC4")
        self.potato_type = MealType.objects.create(name="Potato", colour="#45B7D1")

        # Create recipes for each meal type
        self.pasta1 = Recipe.objects.create(
            name="Spaghetti Bolognese", meal_type=self.pasta_type, instructions="Cook"
        )
        self.pasta2 = Recipe.objects.create(
            name="Penne Carbonara", meal_type=self.pasta_type, instructions="Cook"
        )
        self.rice1 = Recipe.objects.create(
            name="Fried Rice", meal_type=self.rice_type, instructions="Cook"
        )
        self.rice2 = Recipe.objects.create(
            name="Curry Rice", meal_type=self.rice_type, instructions="Cook"
        )
        self.potato1 = Recipe.objects.create(
            name="Baked Potato", meal_type=self.potato_type, instructions="Cook"
        )
        self.potato2 = Recipe.objects.create(
            name="Mashed Potato", meal_type=self.potato_type, instructions="Cook"
        )

        # Create a week plan
        self.week_plan = WeekPlan.objects.create(
            start_date=date(2023, 1, 1), created_by=None
        )

    def test_shuffle_creates_meals(self):
        """Test that shuffling creates meals for each day."""
        result = shuffle_meals(self.week_plan, num_days=7)

        self.assertEqual(len(result), 7)
        self.assertEqual(
            self.week_plan.planned_meals.filter(is_supplementary=False).count(), 7
        )

    def test_shuffle_avoids_consecutive_same_types(self):
        """Test that shuffling avoids consecutive days with same meal type."""
        shuffle_meals(self.week_plan, num_days=7)

        meals = list(
            self.week_plan.planned_meals.filter(is_supplementary=False).order_by(
                "day_offset"
            )
        )

        for i in range(len(meals) - 1):
            current_type = meals[i].recipe.meal_type.id
            next_type = meals[i + 1].recipe.meal_type.id
            self.assertNotEqual(
                current_type,
                next_type,
                f"Consecutive meals have same type at offsets {i} and {i+1}",
            )

    def test_shuffle_preserves_pinned_meals(self):
        """Test that shuffling preserves pinned meals."""
        # Create some initial meals
        pinned_meal1 = PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=0,
            recipe=self.pasta1,
            is_supplementary=False,
            is_pinned=True,
        )
        pinned_meal2 = PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=3,
            recipe=self.rice1,
            is_supplementary=False,
            is_pinned=True,
        )

        # Shuffle
        result = shuffle_meals(self.week_plan, num_days=7)

        # Check pinned meals are still there
        self.assertIn(pinned_meal1, result)
        self.assertIn(pinned_meal2, result)

        # Refresh from db and verify
        pinned_meal1.refresh_from_db()
        pinned_meal2.refresh_from_db()
        self.assertTrue(pinned_meal1.is_pinned)
        self.assertTrue(pinned_meal2.is_pinned)
        self.assertEqual(pinned_meal1.day_offset, 0)
        self.assertEqual(pinned_meal2.day_offset, 3)

    def test_shuffle_replaces_unpinned_meals(self):
        """Test that shuffling replaces unpinned meals."""
        # Create some meals, some pinned some not
        PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=0,
            recipe=self.pasta1,
            is_supplementary=False,
            is_pinned=True,
        )
        unpinned = PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=1,
            recipe=self.pasta2,
            is_supplementary=False,
            is_pinned=False,
        )

        # Shuffle
        shuffle_meals(self.week_plan, num_days=7)

        # Pinned meal should still exist
        self.assertTrue(
            PlannedMeal.objects.filter(
                week_plan=self.week_plan, day_offset=0, is_pinned=True
            ).exists()
        )

        # Unpinned meal should have been deleted
        self.assertFalse(
            PlannedMeal.objects.filter(pk=unpinned.pk).exists()
        )

        # But there should be a new meal at that offset
        self.assertTrue(
            PlannedMeal.objects.filter(
                week_plan=self.week_plan, day_offset=1, is_supplementary=False
            ).exists()
        )

    def test_shuffle_respects_pinned_meal_type_for_next_day(self):
        """Test that shuffle respects the meal type of a pinned meal for the next day."""
        # Pin a pasta meal on day 0
        PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=0,
            recipe=self.pasta1,
            is_supplementary=False,
            is_pinned=True,
        )

        # Shuffle
        shuffle_meals(self.week_plan, num_days=7)

        # Day 1 should NOT have a pasta meal (to avoid consecutive same types)
        day1_meal = PlannedMeal.objects.get(
            week_plan=self.week_plan, day_offset=1, is_supplementary=False
        )
        self.assertNotEqual(
            day1_meal.recipe.meal_type.id, self.pasta_type.id
        )

    def test_shuffle_clears_unpinned_only(self):
        """Test that shuffling only clears unpinned meals."""
        # Create pinned and unpinned meals
        pinned = PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=0,
            recipe=self.pasta1,
            is_supplementary=False,
            is_pinned=True,
        )
        unpinned = PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=1,
            recipe=self.pasta2,
            is_supplementary=False,
            is_pinned=False,
        )

        # Create supplementary meal (should not be deleted)
        supp = PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=0,
            recipe=self.rice1,
            is_supplementary=True,
            is_pinned=False,
        )

        # Shuffle
        shuffle_meals(self.week_plan, num_days=7)

        # Pinned meal should still exist
        self.assertTrue(PlannedMeal.objects.filter(pk=pinned.pk).exists())

        # Supplementary meal should still exist
        self.assertTrue(PlannedMeal.objects.filter(pk=supp.pk).exists())

        # Unpinned meal should be deleted
        self.assertFalse(PlannedMeal.objects.filter(pk=unpinned.pk).exists())

    def test_shuffle_with_multiple_pinned_meals(self):
        """Test shuffling with multiple pinned meals."""
        # Pin meals on days 0, 2, 4
        PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=0,
            recipe=self.pasta1,
            is_supplementary=False,
            is_pinned=True,
        )
        PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=2,
            recipe=self.rice1,
            is_supplementary=False,
            is_pinned=True,
        )
        PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=4,
            recipe=self.potato1,
            is_supplementary=False,
            is_pinned=True,
        )

        # Shuffle
        result = shuffle_meals(self.week_plan, num_days=7)

        # All 3 pinned meals should be in the result
        pinned_count = sum(1 for m in result if m.is_pinned)
        self.assertEqual(pinned_count, 3)

        # Should have 7 total meals
        self.assertEqual(len(result), 7)

        # Verify pinned meals are still on their original days
        day0 = PlannedMeal.objects.get(week_plan=self.week_plan, day_offset=0, is_supplementary=False)
        day2 = PlannedMeal.objects.get(week_plan=self.week_plan, day_offset=2, is_supplementary=False)
        day4 = PlannedMeal.objects.get(week_plan=self.week_plan, day_offset=4, is_supplementary=False)

        self.assertEqual(day0.recipe.pk, self.pasta1.pk)
        self.assertEqual(day2.recipe.pk, self.rice1.pk)
        self.assertEqual(day4.recipe.pk, self.potato1.pk)

    def test_shuffle_with_all_days_pinned(self):
        """Test shuffling when all days are pinned."""
        # Pin meals for all 7 days
        for i, recipe in enumerate([self.pasta1, self.rice1, self.potato1, self.pasta2, self.rice2, self.potato2, self.pasta1]):
            PlannedMeal.objects.create(
                week_plan=self.week_plan,
                day_offset=i,
                recipe=recipe,
                is_supplementary=False,
                is_pinned=True,
            )

        # Shuffle
        result = shuffle_meals(self.week_plan, num_days=7)

        # All meals should be pinned (unchanged)
        self.assertEqual(len(result), 7)
        self.assertTrue(all(m.is_pinned for m in result))

        # Count should still be 7
        self.assertEqual(
            self.week_plan.planned_meals.filter(is_supplementary=False).count(), 7
        )

    def test_shuffle_with_no_recipes(self):
        """Test shuffling when there are no recipes."""
        # Delete all recipes first, then meal types
        Recipe.objects.all().delete()
        MealType.objects.all().delete()

        # Shuffle
        result = shuffle_meals(self.week_plan, num_days=7)

        # Should return empty list
        self.assertEqual(result, [])
        self.assertEqual(
            self.week_plan.planned_meals.filter(is_supplementary=False).count(), 0
        )

    def test_shuffle_with_single_meal_type(self):
        """Test shuffling when only one meal type exists (allows repeats)."""
        # Keep only pasta meal type, delete others
        # First delete recipes of other types
        Recipe.objects.exclude(meal_type=self.pasta_type).delete()
        # Then delete other meal types
        MealType.objects.exclude(pk=self.pasta_type.pk).delete()

        # Shuffle
        shuffle_meals(self.week_plan, num_days=7)

        # Should create 7 meals, all of the same type
        meals = list(
            self.week_plan.planned_meals.filter(is_supplementary=False).order_by(
                "day_offset"
            )
        )
        self.assertEqual(len(meals), 7)
        self.assertTrue(
            all(m.recipe.meal_type.id == self.pasta_type.id for m in meals)
        )
