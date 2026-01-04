from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import (
    MealType,
    ShoppingCategory,
    Store,
    StoreCategoryOrder,
    Ingredient,
    Recipe,
    RecipeIngredient,
    WeekPlan,
    PlannedMeal,
    ShoppingList,
    ShoppingListItem,
)

User = get_user_model()


class MealTypeTests(TestCase):
    def test_create_meal_type(self):
        """Test creating a MealType with valid data."""
        meal_type = MealType.objects.create(name="Dinner", colour="#FF0000")
        self.assertEqual(meal_type.name, "Dinner")
        self.assertEqual(meal_type.colour, "#FF0000")
        self.assertEqual(str(meal_type), "Dinner")


class ShoppingCategoryTests(TestCase):
    def test_create_shopping_category(self):
        """Test creating a ShoppingCategory."""
        category = ShoppingCategory.objects.create(name="Produce")
        self.assertEqual(category.name, "Produce")
        self.assertEqual(str(category), "Produce")


class StoreTests(TestCase):
    def test_create_store(self):
        """Test creating a Store."""
        store = Store.objects.create(name="SuperMart", is_default=True)
        self.assertEqual(store.name, "SuperMart")
        self.assertTrue(store.is_default)
        self.assertEqual(str(store), "SuperMart")

    def test_default_store_logic(self):
        """Test that only one store can be default."""
        store1 = Store.objects.create(name="Store 1", is_default=True)
        store2 = Store.objects.create(name="Store 2", is_default=True)
        
        store1.refresh_from_db()
        self.assertFalse(store1.is_default)
        self.assertTrue(store2.is_default)


class StoreCategoryOrderTests(TestCase):
    def test_create_store_category_order(self):
        """Test mapping a category order to a store."""
        store = Store.objects.create(name="SuperMart")
        category = ShoppingCategory.objects.create(name="Produce")
        order = StoreCategoryOrder.objects.create(
            store=store, category=category, sort_order=1
        )
        self.assertEqual(order.store, store)
        self.assertEqual(order.category, category)
        self.assertEqual(order.sort_order, 1)
        self.assertEqual(str(order), "SuperMart: Produce (1)")


class IngredientTests(TestCase):
    def test_create_ingredient(self):
        """Test creating an ingredient."""
        category = ShoppingCategory.objects.create(name="Produce")
        ingredient = Ingredient.objects.create(
            name="Tomato", category=category, default_unit="kg", is_pantry_staple=True
        )
        self.assertEqual(ingredient.name, "Tomato")
        self.assertEqual(ingredient.category, category)
        self.assertEqual(ingredient.default_unit, "kg")
        self.assertTrue(ingredient.is_pantry_staple)
        self.assertEqual(str(ingredient), "Tomato")


class RecipeTests(TestCase):
    def setUp(self):
        self.meal_type = MealType.objects.create(name="Dinner")
        self.recipe = Recipe.objects.create(
            name="Pasta",
            meal_type=self.meal_type,
            difficulty=1,
            instructions="Boil water...",
        )

    def test_create_recipe(self):
        """Test creating a recipe."""
        self.assertEqual(self.recipe.name, "Pasta")
        self.assertEqual(self.recipe.meal_type, self.meal_type)
        self.assertEqual(self.recipe.difficulty, 1)
        self.assertEqual(str(self.recipe), "Pasta")

    def test_times_made(self):
        """Test times_made calculation."""
        # Create a WeekPlan and PlannedMeal
        week_plan = WeekPlan.objects.create(start_date=date(2023, 1, 1))
        PlannedMeal.objects.create(
            week_plan=week_plan, day_offset=0, recipe=self.recipe
        )
        self.assertEqual(self.recipe.times_made(), 1)

    def test_last_made(self):
        """Test last_made calculation."""
        week_plan = WeekPlan.objects.create(start_date=date(2023, 1, 1))
        PlannedMeal.objects.create(
            week_plan=week_plan, day_offset=1, recipe=self.recipe
        )
        self.assertEqual(self.recipe.last_made(), date(2023, 1, 2))


class RecipeIngredientTests(TestCase):
    def test_create_recipe_ingredient(self):
        """Test linking ingredient to recipe."""
        meal_type = MealType.objects.create(name="Dinner")
        recipe = Recipe.objects.create(name="Pasta", meal_type=meal_type)
        category = ShoppingCategory.objects.create(name="Pantry")
        ingredient = Ingredient.objects.create(name="Pasta", category=category)
        
        ri = RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient, quantity="500g"
        )
        self.assertEqual(ri.recipe, recipe)
        self.assertEqual(ri.ingredient, ingredient)
        self.assertEqual(ri.quantity, "500g")
        self.assertEqual(str(ri), "500g Pasta")


class WeekPlanTests(TestCase):
    def test_create_week_plan(self):
        """Test creating a week plan."""
        user = User.objects.create_user(username="testuser")
        plan = WeekPlan.objects.create(start_date=date(2023, 1, 1), created_by=user)
        self.assertEqual(plan.start_date, date(2023, 1, 1))
        self.assertEqual(plan.created_by, user)
        self.assertTrue(str(plan).startswith("Week of 01 Jan 2023"))


class PlannedMealTests(TestCase):
    def setUp(self):
        self.week_plan = WeekPlan.objects.create(start_date=date(2023, 1, 1))
        self.meal_type = MealType.objects.create(name="Dinner")
        self.recipe = Recipe.objects.create(name="Pasta", meal_type=self.meal_type)

    def test_create_planned_meal_with_recipe(self):
        """Test creating a planned meal with a recipe."""
        meal = PlannedMeal.objects.create(
            week_plan=self.week_plan, day_offset=0, recipe=self.recipe
        )
        self.assertEqual(meal.actual_date(), date(2023, 1, 1))
        self.assertIn("Pasta", str(meal))

    def test_create_planned_meal_with_note(self):
        """Test creating a planned meal with just a note."""
        meal = PlannedMeal.objects.create(
            week_plan=self.week_plan, day_offset=1, note="Eating out"
        )
        self.assertEqual(meal.actual_date(), date(2023, 1, 2))
        self.assertIn("Eating out", str(meal))


class ShoppingListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.store = Store.objects.create(name="SuperMart")
        self.week_plan = WeekPlan.objects.create(start_date=date(2023, 1, 1))
        
    def test_create_shopping_list(self):
        """Test creating a shopping list."""
        sl = ShoppingList.objects.create(
            week_plan=self.week_plan,
            store=self.store,
            created_by=self.user,
            is_active=True
        )
        self.assertTrue(sl.is_active)
        self.assertIn("Shopping List", str(sl))

    def test_active_list_logic(self):
        """Test that only one shopping list can be active."""
        sl1 = ShoppingList.objects.create(is_active=True)
        sl2 = ShoppingList.objects.create(is_active=True)
        
        sl1.refresh_from_db()
        self.assertFalse(sl1.is_active)
        self.assertTrue(sl2.is_active)

    def test_checked_count(self):
        """Test checked items count."""
        sl = ShoppingList.objects.create()
        ShoppingListItem.objects.create(shopping_list=sl, name="Item 1", is_checked=True)
        ShoppingListItem.objects.create(shopping_list=sl, name="Item 2", is_checked=False)
        self.assertEqual(sl.checked_count, 1)

    def test_is_stale(self):
        """Test is_stale property."""
        sl = ShoppingList.objects.create(
            week_plan=self.week_plan,
            generated_at=timezone.now()
        )
        # Initially not stale
        self.assertFalse(sl.is_stale)
        
        # Modify week plan to be newer than generated_at
        # We need to manually update modified_at or wait, but since auto_now=True,
        # saving the week plan should update it.
        # Ideally we mock or manipulate times, but for a simple test:
        self.week_plan.save()
        # Even with save, if it's too fast, timestamps might match
        # Let's manually set generated_at to past
        sl.generated_at = timezone.now() - timedelta(hours=1)
        sl.save()
        
        self.assertTrue(sl.is_stale)


class ShoppingListItemTests(TestCase):
    def test_create_shopping_list_item(self):
        """Test creating a shopping list item."""
        sl = ShoppingList.objects.create()
        item = ShoppingListItem.objects.create(
            shopping_list=sl,
            name="Milk",
            quantities="2L",
            is_checked=True
        )
        self.assertEqual(item.name, "Milk")
        self.assertEqual(item.quantities, "2L")
        self.assertTrue(item.is_checked)
        self.assertEqual(str(item), "Milk: 2L")
