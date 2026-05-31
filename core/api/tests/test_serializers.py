"""
Tests for API serializers.
"""

from django.test import TestCase
from core.models import MealType, ShoppingCategory, Store, Ingredient, Recipe, WeekPlan, PlannedMeal
from core.api.serializers import (
    MealTypeSerializer,
    ShoppingCategorySerializer,
    StoreSerializer,
    IngredientSerializer,
    RecipeSerializer,
    WeekPlanSerializer,
    PlannedMealSerializer,
)


class MealTypeSerializerTests(TestCase):
    def setUp(self):
        self.meal_type = MealType.objects.create(name="Dinner", colour="#FF0000")

    def test_serialize(self):
        serializer = MealTypeSerializer(self.meal_type)
        data = serializer.data
        self.assertEqual(data["id"], self.meal_type.id)
        self.assertEqual(data["name"], "Dinner")
        self.assertEqual(data["colour"], "#FF0000")

    def test_deserialize(self):
        data = {"name": "Lunch", "colour": "#00FF00"}
        serializer = MealTypeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        meal_type = serializer.save()
        self.assertEqual(meal_type.name, "Lunch")
        self.assertEqual(meal_type.colour, "#00FF00")


class ShoppingCategorySerializerTests(TestCase):
    def setUp(self):
        self.category = ShoppingCategory.objects.create(name="Produce")

    def test_serialize(self):
        serializer = ShoppingCategorySerializer(self.category)
        data = serializer.data
        self.assertEqual(data["id"], self.category.id)
        self.assertEqual(data["name"], "Produce")

    def test_deserialize(self):
        data = {"name": "Dairy"}
        serializer = ShoppingCategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        category = serializer.save()
        self.assertEqual(category.name, "Dairy")


class StoreSerializerTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name="SuperMart", is_default=True)

    def test_serialize(self):
        serializer = StoreSerializer(self.store)
        data = serializer.data
        self.assertEqual(data["id"], self.store.id)
        self.assertEqual(data["name"], "SuperMart")
        self.assertEqual(data["is_default"], True)

    def test_deserialize(self):
        data = {"name": "MegaStore", "is_default": False}
        serializer = StoreSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        store = serializer.save()
        self.assertEqual(store.name, "MegaStore")
        self.assertEqual(store.is_default, False)


class IngredientSerializerTests(TestCase):
    def setUp(self):
        self.category = ShoppingCategory.objects.create(name="Produce")
        self.ingredient = Ingredient.objects.create(
            name="Carrot",
            category=self.category,
            is_pantry_staple=False,
            default_unit="kg",
        )

    def test_serialize(self):
        serializer = IngredientSerializer(self.ingredient)
        data = serializer.data
        self.assertEqual(data["id"], self.ingredient.id)
        self.assertEqual(data["name"], "Carrot")
        self.assertEqual(data["category"], self.category.id)
        self.assertEqual(data["is_pantry_staple"], False)
        self.assertEqual(data["default_unit"], "kg")

    def test_deserialize(self):
        data = {
            "name": "Potato",
            "category": self.category.id,
            "is_pantry_staple": True,
            "default_unit": "kg",
        }
        serializer = IngredientSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        ingredient = serializer.save()
        self.assertEqual(ingredient.name, "Potato")
        self.assertEqual(ingredient.category, self.category)


class RecipeSerializerTests(TestCase):
    def setUp(self):
        self.meal_type = MealType.objects.create(name="Dinner", colour="#FF0000")
        self.category = ShoppingCategory.objects.create(name="Produce")
        self.ingredient = Ingredient.objects.create(
            name="Carrot",
            category=self.category,
            is_pantry_staple=False,
        )
        self.recipe = Recipe.objects.create(
            name="Roasted Carrots",
            meal_type=self.meal_type,
            instructions="Cook carrots in oven",
        )
        # Add ingredient to recipe
        from core.models import RecipeIngredient
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity="500g",
        )

    def test_serialize(self):
        serializer = RecipeSerializer(self.recipe)
        data = serializer.data
        self.assertEqual(data["id"], self.recipe.id)
        self.assertEqual(data["name"], "Roasted Carrots")
        self.assertEqual(data["meal_type"], self.meal_type.id)
        self.assertEqual(len(data["recipe_ingredients"]), 1)

    def test_deserialize_with_ingredients(self):
        data = {
            "name": "New Recipe",
            "meal_type": self.meal_type.id,
            "instructions": "Test instructions",
            "recipe_ingredients": [
                {"ingredient": self.ingredient.id, "quantity": "2"}
            ],
        }
        serializer = RecipeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        recipe = serializer.save()
        self.assertEqual(recipe.name, "New Recipe")
        self.assertEqual(recipe.recipe_ingredients.count(), 1)


class WeekPlanSerializerTests(TestCase):
    def setUp(self):
        from datetime import date
        self.week_plan = WeekPlan.objects.create(
            start_date=date(2024, 1, 1),
            is_locked=False,
        )

    def test_serialize(self):
        serializer = WeekPlanSerializer(self.week_plan)
        data = serializer.data
        self.assertEqual(data["id"], self.week_plan.id)
        self.assertEqual(data["start_date"], "2024-01-01")


class PlannedMealSerializerTests(TestCase):
    def setUp(self):
        from datetime import date
        self.meal_type = MealType.objects.create(name="Dinner", colour="#FF0000")
        self.week_plan = WeekPlan.objects.create(
            start_date=date(2024, 1, 1),
            is_locked=False,
        )
        self.recipe = Recipe.objects.create(
            name="Test Recipe",
            meal_type=self.meal_type,
            instructions="Test",
        )
        self.planned_meal = PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=0,
            recipe=self.recipe,
            note="",
            is_supplementary=False,
        )

    def test_serialize(self):
        serializer = PlannedMealSerializer(self.planned_meal)
        data = serializer.data
        self.assertEqual(data["id"], self.planned_meal.id)
        self.assertEqual(data["week_plan"], self.week_plan.id)
        self.assertEqual(data["day_offset"], 0)
        self.assertEqual(data["recipe"], self.recipe.id)

    def test_deserialize(self):
        data = {
            "week_plan": self.week_plan.id,
            "day_offset": 1,
            "recipe": self.recipe.id,
        }
        serializer = PlannedMealSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        planned_meal = serializer.save()
        self.assertEqual(planned_meal.day_offset, 1)
