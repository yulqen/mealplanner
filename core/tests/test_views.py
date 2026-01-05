from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import (
    MealType,
    ShoppingCategory,
    Store,
    Ingredient,
    Recipe,
    RecipeIngredient,
    WeekPlan,
    PlannedMeal,
    ShoppingList,
    ShoppingListItem,
)

User = get_user_model()


class BaseViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")


class RecipeViewTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.meal_type = MealType.objects.create(name="Dinner")
        self.recipe = Recipe.objects.create(
            name="Test Recipe",
            meal_type=self.meal_type,
            instructions="Test instructions",
        )

    def test_recipe_list(self):
        response = self.client.get(reverse("recipe_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")

    def test_recipe_list_htmx(self):
        response = self.client.get(reverse("recipe_list"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "components/recipe_list_items.html")

    def test_recipe_detail(self):
        response = self.client.get(reverse("recipe_detail", args=[self.recipe.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")

    def test_recipe_create(self):
        response = self.client.post(
            reverse("recipe_create"),
            {
                "name": "New Recipe",
                "meal_type": self.meal_type.pk,
                "difficulty": 1,
                "instructions": "steps",
                "recipe_ingredients-TOTAL_FORMS": "1",
                "recipe_ingredients-INITIAL_FORMS": "0",
                "recipe_ingredients-MIN_NUM_FORMS": "0",
                "recipe_ingredients-MAX_NUM_FORMS": "1000",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Recipe.objects.filter(name="New Recipe").exists())

    def test_recipe_edit(self):
        response = self.client.post(
            reverse("recipe_edit", args=[self.recipe.pk]),
            {
                "name": "Updated Recipe",
                "meal_type": self.meal_type.pk,
                "instructions": "updated",
                "recipe_ingredients-TOTAL_FORMS": "0",
                "recipe_ingredients-INITIAL_FORMS": "0",
                "recipe_ingredients-MIN_NUM_FORMS": "0",
                "recipe_ingredients-MAX_NUM_FORMS": "1000",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.name, "Updated Recipe")

    def test_recipe_delete(self):
        response = self.client.post(reverse("recipe_delete", args=[self.recipe.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Recipe.objects.filter(pk=self.recipe.pk).exists())

    def test_recipe_toggle_ace(self):
        response = self.client.get(reverse("recipe_toggle_ace", args=[self.recipe.pk]))
        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertTrue(self.recipe.ace_tag)


class IngredientViewTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.category = ShoppingCategory.objects.create(name="Produce")
        self.ingredient = Ingredient.objects.create(
            name="Tomato", category=self.category
        )

    def test_ingredient_list(self):
        response = self.client.get(reverse("ingredient_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tomato")

    def test_ingredient_list_htmx(self):
        response = self.client.get(reverse("ingredient_list"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "components/ingredient_list_items.html")

    def test_ingredient_create(self):
        response = self.client.post(
            reverse("ingredient_create"),
            {"name": "Cucumber", "category": self.category.pk, "default_unit": "kg"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ingredient.objects.filter(name="Cucumber").exists())

    def test_ingredient_edit(self):
        response = self.client.post(
            reverse("ingredient_edit", args=[self.ingredient.pk]),
            {"name": "Big Tomato", "category": self.category.pk},
        )
        self.assertEqual(response.status_code, 302)
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.name, "Big Tomato")

    def test_ingredient_delete(self):
        response = self.client.post(
            reverse("ingredient_delete", args=[self.ingredient.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ingredient.objects.filter(pk=self.ingredient.pk).exists())

    def test_ingredient_autocomplete(self):
        response = self.client.get(
            reverse("ingredient_autocomplete"), {"q": "Tom"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tomato")

    def test_ingredient_create_inline(self):
        response = self.client.post(
            reverse("ingredient_create_inline"),
            {"name": "Onion", "category": self.category.pk},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Onion")
        self.assertTrue(Ingredient.objects.filter(name="Onion").exists())


class WeekPlanViewTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.plan = WeekPlan.objects.create(
            start_date=date(2023, 1, 1), created_by=self.user
        )
        self.meal_type = MealType.objects.create(name="Dinner")
        self.recipe = Recipe.objects.create(name="Pasta", meal_type=self.meal_type)

    def test_plan_list(self):
        response = self.client.get(reverse("plan_list"))
        self.assertEqual(response.status_code, 200)

    def test_plan_create(self):
        response = self.client.post(
            reverse("plan_create"), {"start_date": "2023-01-08"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(WeekPlan.objects.filter(start_date=date(2023, 1, 8)).exists())

    def test_plan_detail(self):
        response = self.client.get(reverse("plan_detail", args=[self.plan.pk]))
        self.assertEqual(response.status_code, 200)

    def test_plan_delete(self):
        response = self.client.post(reverse("plan_delete", args=[self.plan.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(WeekPlan.objects.filter(pk=self.plan.pk).exists())

    def test_plan_shuffle(self):
        # Setup a recipe to be shuffled in
        Recipe.objects.create(name="Pizza", meal_type=self.meal_type)
        response = self.client.post(reverse("plan_shuffle", args=[self.plan.pk]))
        self.assertEqual(response.status_code, 302)
        # Check that meals were created (shuffle logic is complex, just checking existence)
        self.assertTrue(self.plan.planned_meals.exists())

    def test_plan_shuffle_locked(self):
        self.plan.is_locked = True
        self.plan.save()
        # Ensure no meals before shuffling
        self.plan.planned_meals.all().delete()
        
        response = self.client.post(reverse("plan_shuffle", args=[self.plan.pk]))
        self.assertEqual(response.status_code, 302)
        # Check that NO meals were created because it's locked
        self.assertFalse(self.plan.planned_meals.exists())

    def test_plan_toggle_lock(self):
        # Toggle lock on
        response = self.client.post(reverse("plan_toggle_lock", args=[self.plan.pk]))
        self.assertEqual(response.status_code, 302)
        self.plan.refresh_from_db()
        self.assertTrue(self.plan.is_locked)

        # Toggle lock off
        response = self.client.post(reverse("plan_toggle_lock", args=[self.plan.pk]))
        self.assertEqual(response.status_code, 302)
        self.plan.refresh_from_db()
        self.assertFalse(self.plan.is_locked)

    def test_plan_assign(self):
        response = self.client.post(
            reverse("plan_assign", args=[self.plan.pk, 0]),
            {"recipe_id": self.recipe.pk},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            PlannedMeal.objects.filter(
                week_plan=self.plan, day_offset=0, recipe=self.recipe
            ).exists()
        )

    def test_plan_clear_day(self):
        PlannedMeal.objects.create(
            week_plan=self.plan, day_offset=0, recipe=self.recipe
        )
        response = self.client.post(
            reverse("plan_clear_day", args=[self.plan.pk, 0]), HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            PlannedMeal.objects.filter(week_plan=self.plan, day_offset=0).exists()
        )

    def test_plan_assign_supplementary(self):
        response = self.client.post(
            reverse("plan_assign_supplementary", args=[self.plan.pk, 0]),
            {"recipe_id": self.recipe.pk, "for_people": "Kids"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            PlannedMeal.objects.filter(
                week_plan=self.plan,
                day_offset=0,
                recipe=self.recipe,
                is_supplementary=True,
            ).exists()
        )

    def test_plan_clear_supplementary(self):
        PlannedMeal.objects.create(
            week_plan=self.plan,
            day_offset=0,
            recipe=self.recipe,
            is_supplementary=True,
        )
        response = self.client.post(
            reverse("plan_clear_supplementary", args=[self.plan.pk, 0]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            PlannedMeal.objects.filter(
                week_plan=self.plan, day_offset=0, is_supplementary=True
            ).exists()
        )


class ShoppingListViewTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.store = Store.objects.create(name="SuperMart")
        self.shopping_list = ShoppingList.objects.create(
            name="My List", created_by=self.user, store=self.store
        )
        self.item = ShoppingListItem.objects.create(
            shopping_list=self.shopping_list, name="Soap"
        )

    def test_shopping_list(self):
        response = self.client.get(reverse("shopping_list", args=[self.shopping_list.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My List")

    def test_shopping_list_create(self):
        response = self.client.post(
            reverse("shopping_list_create"),
            {"name": "Party List", "store": self.store.pk},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ShoppingList.objects.filter(name="Party List").exists())

    def test_shopping_list_delete(self):
        response = self.client.post(
            reverse("shopping_list_delete", args=[self.shopping_list.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ShoppingList.objects.filter(pk=self.shopping_list.pk).exists())

    def test_shopping_generate(self):
        plan = WeekPlan.objects.create(start_date=date(2023, 2, 1))
        response = self.client.post(
            reverse("shopping_generate", args=[plan.pk]), {"store": self.store.pk}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ShoppingList.objects.filter(week_plan=plan).exists())

    def test_shopping_check(self):
        response = self.client.post(
            reverse("shopping_check", args=[self.shopping_list.pk, self.item.pk]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_checked)

    def test_shopping_star(self):
        response = self.client.post(
            reverse("shopping_star", args=[self.shopping_list.pk, self.item.pk]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_starred)

    def test_shopping_add(self):
        response = self.client.post(
            reverse("shopping_add", args=[self.shopping_list.pk]),
            {"name": "Bread"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ShoppingListItem.objects.filter(
                shopping_list=self.shopping_list, name="Bread"
            ).exists()
        )

    def test_shopping_item_autocomplete(self):
        response = self.client.get(
            reverse("shopping_item_autocomplete", args=[self.shopping_list.pk]),
            {"name": "Soa"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)

    def test_shopping_clear(self):
        self.item.is_checked = True
        self.item.save()
        response = self.client.post(
            reverse("shopping_clear", args=[self.shopping_list.pk]), {"type": "checked"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ShoppingListItem.objects.filter(pk=self.item.pk).exists())

    def test_shopping_change_store(self):
        other_store = Store.objects.create(name="Other Mart")
        response = self.client.post(
            reverse("shopping_change_store", args=[self.shopping_list.pk]),
            {"store": other_store.pk},
        )
        self.assertEqual(response.status_code, 302)
        self.shopping_list.refresh_from_db()
        self.assertEqual(self.shopping_list.store, other_store)

    def test_shopping_edit_category(self):
        category = ShoppingCategory.objects.create(name="Household")
        response = self.client.post(
            reverse(
                "shopping_edit_category",
                args=[self.shopping_list.pk, self.item.pk],
            ),
            {"category": category.pk},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.category, category)
