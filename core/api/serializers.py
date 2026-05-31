"""
DRF Serializers for all Meal Planner models.
"""

from rest_framework import serializers
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


class MealTypeSerializer(serializers.ModelSerializer):
    """Serializer for MealType model."""

    class Meta:
        model = MealType
        fields = ["id", "name", "colour"]
        read_only_fields = ["id"]


class ShoppingCategorySerializer(serializers.ModelSerializer):
    """Serializer for ShoppingCategory model."""

    class Meta:
        model = ShoppingCategory
        fields = ["id", "name"]
        read_only_fields = ["id"]


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for Store model."""

    class Meta:
        model = Store
        fields = ["id", "name", "is_default"]
        read_only_fields = ["id"]


class StoreCategoryOrderSerializer(serializers.ModelSerializer):
    """Serializer for StoreCategoryOrder model."""

    class Meta:
        model = StoreCategoryOrder
        fields = ["id", "store", "category", "sort_order"]
        read_only_fields = ["id"]


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient model."""

    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "category",
            "is_pantry_staple",
            "default_unit",
        ]
        read_only_fields = ["id"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer for RecipeIngredient model."""

    class Meta:
        model = RecipeIngredient
        fields = ["id", "ingredient", "quantity"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model with nested ingredients."""

    recipe_ingredients = RecipeIngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "meal_type",
            "difficulty",
            "instructions",
            "reference",
            "is_archived",
            "ace_tag",
            "created_at",
            "updated_at",
            "recipe_ingredients",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "recipe_ingredients",
        ]

    def create(self, validated_data):
        """Create a recipe with ingredients."""
        ingredients_data = validated_data.pop("recipe_ingredients", [])
        recipe = Recipe.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        
        return recipe

    def update(self, instance, validated_data):
        """Update a recipe with ingredients."""
        ingredients_data = validated_data.pop("recipe_ingredients", None)
        
        # Update recipe fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update ingredients if provided
        if ingredients_data is not None:
            # Clear existing ingredients
            instance.recipe_ingredients.all().delete()
            
            # Create new ingredients
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(recipe=instance, **ingredient_data)
        
        return instance


class WeekPlanSerializer(serializers.ModelSerializer):
    """Serializer for WeekPlan model."""

    class Meta:
        model = WeekPlan
        fields = [
            "id",
            "start_date",
            "created_by",
            "created_at",
            "modified_at",
            "is_locked",
        ]
        read_only_fields = ["id", "created_at", "modified_at"]


class PlannedMealSerializer(serializers.ModelSerializer):
    """Serializer for PlannedMeal model with nested recipe."""

    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = PlannedMeal
        fields = [
            "id",
            "week_plan",
            "day_offset",
            "recipe",
            "note",
            "is_supplementary",
            "for_people",
            "is_pinned",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """Create a planned meal."""
        return PlannedMeal.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update a planned meal."""
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class ShoppingListSerializer(serializers.ModelSerializer):
    """Serializer for ShoppingList model."""

    class Meta:
        model = ShoppingList
        fields = [
            "id",
            "name",
            "week_plan",
            "store",
            "created_by",
            "created_at",
            "generated_at",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "generated_at",
        ]


class ShoppingListItemSerializer(serializers.ModelSerializer):
    """Serializer for ShoppingListItem model."""

    class Meta:
        model = ShoppingListItem
        fields = [
            "id",
            "shopping_list",
            "ingredient",
            "name",
            "category",
            "quantities",
            "is_checked",
            "is_manual",
            "is_pantry_override",
            "is_pantry_item",
            "is_starred",
        ]
        read_only_fields = ["id"]
