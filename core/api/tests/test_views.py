"""
Tests for API views.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status
from core.models import (
    MealType,
    ShoppingCategory,
    Store,
    Ingredient,
    Recipe,
    WeekPlan,
    PlannedMeal,
    ShoppingList,
    ShoppingListItem,
)

User = get_user_model()


class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client.login(username="testuser", password="testpass123")


class MealTypeViewSetTests(APITestCase):
    def test_list(self):
        MealType.objects.create(name="Dinner", colour="#FF0000")
        response = self.client.get("/api/v1/meal-types/", HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreater(len(data["results"]), 0)

    def test_create(self):
        data = {"name": "Lunch", "colour": "#00FF00"}
        response = self.client.post("/api/v1/meal-types/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MealType.objects.count(), 1)

    def test_retrieve(self):
        meal_type = MealType.objects.create(name="Dinner", colour="#FF0000")
        response = self.client.get(f"/api/v1/meal-types/{meal_type.id}/", HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Dinner")

    def test_update(self):
        meal_type = MealType.objects.create(name="Dinner", colour="#FF0000")
        data = {"name": "Supper", "colour": "#0000FF"}
        response = self.client.put(f"/api/v1/meal-types/{meal_type.id}/", data, content_type="application/json", HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        meal_type.refresh_from_db()
        self.assertEqual(meal_type.name, "Supper")

    def test_delete(self):
        meal_type = MealType.objects.create(name="Dinner", colour="#FF0000")
        response = self.client.delete(f"/api/v1/meal-types/{meal_type.id}/", HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MealType.objects.count(), 0)


class ShoppingCategoryViewSetTests(APITestCase):
    def test_list(self):
        ShoppingCategory.objects.create(name="Produce")
        response = self.client.get("/api/v1/shopping-categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        data = {"name": "Dairy"}
        response = self.client.post("/api/v1/shopping-categories/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class StoreViewSetTests(APITestCase):
    def test_list(self):
        Store.objects.create(name="SuperMart", is_default=True)
        response = self.client.get("/api/v1/stores/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        data = {"name": "MegaStore", "is_default": False}
        response = self.client.post("/api/v1/stores/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class IngredientViewSetTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.category = ShoppingCategory.objects.create(name="Produce")

    def test_list(self):
        Ingredient.objects.create(
            name="Carrot",
            category=self.category,
            is_pantry_staple=False,
        )
        response = self.client.get("/api/v1/ingredients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        data = {
            "name": "Potato",
            "category": self.category.id,
            "is_pantry_staple": True,
        }
        response = self.client.post("/api/v1/ingredients/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RecipeViewSetTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.meal_type = MealType.objects.create(name="Dinner", colour="#FF0000")
        self.category = ShoppingCategory.objects.create(name="Produce")
        self.ingredient = Ingredient.objects.create(
            name="Carrot",
            category=self.category,
            is_pantry_staple=False,
        )

    def test_list(self):
        Recipe.objects.create(
            name="Roasted Carrots",
            meal_type=self.meal_type,
            instructions="Cook carrots",
        )
        response = self.client.get("/api/v1/recipes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        data = {
            "name": "New Recipe",
            "meal_type": self.meal_type.id,
            "instructions": "Test instructions",
        }
        response = self.client.post("/api/v1/recipes/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_filter_by_meal_type(self):
        Recipe.objects.create(
            name="Recipe 1",
            meal_type=self.meal_type,
            instructions="Test",
        )
        response = self.client.get(
            "/api/v1/recipes/",
            {"meal_type": self.meal_type.id},
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertGreater(len(results), 0)

    def test_search(self):
        Recipe.objects.create(
            name="Pasta Carbonara",
            meal_type=self.meal_type,
            instructions="Test",
        )
        response = self.client.get(
            "/api/v1/recipes/",
            {"search": "pasta"},
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertGreater(len(results), 0)


class WeekPlanViewSetTests(APITestCase):
    def setUp(self):
        super().setUp()
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
            instructions="Cook carrots",
        )
        from core.models import RecipeIngredient
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity="500g",
        )

    def test_list(self):
        from datetime import date
        WeekPlan.objects.create(
            start_date=date(2024, 1, 1),
            is_locked=False,
        )
        response = self.client.get("/api/v1/week-plans/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        from datetime import date
        data = {"start_date": date(2024, 1, 1), "is_locked": False}
        response = self.client.post("/api/v1/week-plans/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_shuffle_action(self):
        from datetime import date
        week_plan = WeekPlan.objects.create(
            start_date=date(2024, 1, 1),
            is_locked=False,
        )
        response = self.client.post(
            f"/api/v1/week-plans/{week_plan.id}/shuffle/",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        week_plan.refresh_from_db()
        # After shuffle, there should be planned meals
        self.assertGreater(week_plan.planned_meals.count(), 0)


class PlannedMealViewSetTests(APITestCase):
    def setUp(self):
        super().setUp()
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

    def test_create(self):
        data = {
            "week_plan": self.week_plan.id,
            "day_offset": 0,
            "recipe": self.recipe.id,
        }
        response = self.client.post("/api/v1/planned-meals/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_toggle_pin_action(self):
        planned_meal = PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=0,
            recipe=self.recipe,
        )
        self.assertFalse(planned_meal.is_pinned)
        
        response = self.client.post(
            f"/api/v1/planned-meals/{planned_meal.id}/toggle_pin/",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        planned_meal.refresh_from_db()
        self.assertTrue(planned_meal.is_pinned)


class ShoppingListViewSetTests(APITestCase):
    def setUp(self):
        super().setUp()
        from datetime import date
        from core.models import RecipeIngredient
        
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
            instructions="Cook carrots",
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity="500g",
        )
        
        self.week_plan = WeekPlan.objects.create(
            start_date=date(2024, 1, 1),
            is_locked=False,
        )
        # Add a planned meal with the recipe
        PlannedMeal.objects.create(
            week_plan=self.week_plan,
            day_offset=0,
            recipe=self.recipe,
        )
        self.store = Store.objects.create(name="SuperMart", is_default=True)

    def test_create(self):
        data = {
            "name": "Shopping List",
            "week_plan": self.week_plan.id,
            "store": self.store.id,
        }
        response = self.client.post("/api/v1/shopping-lists/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_generate_action(self):
        shopping_list = ShoppingList.objects.create(
            name="Test List",
            week_plan=self.week_plan,
            store=self.store,
        )
        response = self.client.post(
            f"/api/v1/shopping-lists/{shopping_list.id}/generate/",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        shopping_list.refresh_from_db()
        # After generation, there should be items
        self.assertGreater(shopping_list.items.count(), 0)


class ShoppingListItemViewSetTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.shopping_list = ShoppingList.objects.create(
            name="Test List",
        )

    def test_toggle_check_action(self):
        item = ShoppingListItem.objects.create(
            shopping_list=self.shopping_list,
            name="Carrot",
            quantities="2",
            is_checked=False,
        )
        self.assertFalse(item.is_checked)
        
        response = self.client.post(
            f"/api/v1/shopping-list-items/{item.id}/toggle_check/",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertTrue(item.is_checked)
