from django.contrib import admin

from .models import (
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


@admin.register(MealType)
class MealTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "colour"]
    search_fields = ["name"]


@admin.register(ShoppingCategory)
class ShoppingCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name", "is_default"]
    list_filter = ["is_default"]


@admin.register(StoreCategoryOrder)
class StoreCategoryOrderAdmin(admin.ModelAdmin):
    list_display = ["store", "category", "sort_order"]
    list_filter = ["store"]
    ordering = ["store", "sort_order"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_pantry_staple", "default_unit"]
    list_filter = ["category", "is_pantry_staple"]
    search_fields = ["name"]


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ["ingredient"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "meal_type", "difficulty", "is_archived", "created_at"]
    list_filter = ["meal_type", "difficulty", "is_archived"]
    search_fields = ["name"]
    inlines = [RecipeIngredientInline]


@admin.register(WeekPlan)
class WeekPlanAdmin(admin.ModelAdmin):
    list_display = ["start_date", "created_by", "created_at"]
    list_filter = ["created_by"]
    date_hierarchy = "start_date"


class PlannedMealInline(admin.TabularInline):
    model = PlannedMeal
    extra = 0
    autocomplete_fields = ["recipe"]


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ["name", "store", "is_active", "created_by", "created_at"]
    list_filter = ["is_active", "store"]


@admin.register(ShoppingListItem)
class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ["name", "shopping_list", "category", "is_checked"]
    list_filter = ["shopping_list", "is_checked", "category"]
