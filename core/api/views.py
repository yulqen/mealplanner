"""
DRF Views for the Meal Planner API.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

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
from core.api.serializers import (
    MealTypeSerializer,
    ShoppingCategorySerializer,
    StoreSerializer,
    StoreCategoryOrderSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeIngredientSerializer,
    WeekPlanSerializer,
    PlannedMealSerializer,
    ShoppingListSerializer,
    ShoppingListItemSerializer,
)
from core.api.pagination import StandardResultsSetPagination
from core.services.shuffle import shuffle_meals
from core.services.shopping import generate_shopping_list


class MealTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for MealType model."""

    queryset = MealType.objects.all()
    serializer_class = MealTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class ShoppingCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for ShoppingCategory model."""

    queryset = ShoppingCategory.objects.all()
    serializer_class = ShoppingCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class StoreViewSet(viewsets.ModelViewSet):
    """ViewSet for Store model."""

    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class StoreCategoryOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for StoreCategoryOrder model."""

    queryset = StoreCategoryOrder.objects.all()
    serializer_class = StoreCategoryOrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet for Ingredient model."""

    queryset = Ingredient.objects.all().select_related("category")
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    """ViewSet for RecipeIngredient model."""

    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for Recipe model with filtering."""

    queryset = Recipe.objects.filter(is_archived=False).select_related(
        "meal_type"
    ).prefetch_related("recipe_ingredients__ingredient__category")
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Apply filtering based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by meal_type
        meal_type_id = self.request.query_params.get("meal_type")
        if meal_type_id:
            queryset = queryset.filter(meal_type_id=meal_type_id)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get("difficulty")
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by ace_tag
        ace_tag = self.request.query_params.get("ace_tag")
        if ace_tag:
            queryset = queryset.filter(ace_tag=True)
        
        # Search by name
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset


class WeekPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for WeekPlan model."""

    queryset = WeekPlan.objects.all()
    serializer_class = WeekPlanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=["post"])
    def shuffle(self, request, pk=None):
        """Custom action to shuffle meals for a week plan."""
        week_plan = self.get_object()
        
        # Call the shuffle service
        planned_meals = shuffle_meals(week_plan)
        
        # Return the updated week plan
        serializer = self.get_serializer(week_plan)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def planned_meals(self, request, pk=None):
        """List planned meals for a specific week plan."""
        week_plan = self.get_object()
        planned_meals = week_plan.planned_meals.filter(is_supplementary=False)
        
        serializer = PlannedMealSerializer(planned_meals, many=True)
        return Response(serializer.data)


class PlannedMealViewSet(viewsets.ModelViewSet):
    """ViewSet for PlannedMeal model."""

    queryset = PlannedMeal.objects.all()
    serializer_class = PlannedMealSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=["post"])
    def toggle_pin(self, request, pk=None):
        """Toggle the pinned status of a planned meal."""
        planned_meal = self.get_object()
        planned_meal.is_pinned = not planned_meal.is_pinned
        planned_meal.save()
        
        serializer = self.get_serializer(planned_meal)
        return Response(serializer.data)


class ShoppingListViewSet(viewsets.ModelViewSet):
    """ViewSet for ShoppingList model."""

    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=["post"])
    def generate(self, request, pk=None):
        """Generate shopping list from a week plan."""
        shopping_list = self.get_object()
        
        if shopping_list.week_plan:
            # Generate shopping list from week plan
            updated_list = generate_shopping_list(
                week_plan=shopping_list.week_plan,
                store=shopping_list.store,
                created_by=request.user,
                shopping_list=shopping_list,
                replace=True,
            )
            
            serializer = self.get_serializer(updated_list)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Shopping list has no associated week plan"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["get"])
    def items(self, request, pk=None):
        """List items for a specific shopping list."""
        shopping_list = self.get_object()
        items = shopping_list.items.all()
        
        serializer = ShoppingListItemSerializer(items, many=True)
        return Response(serializer.data)


class ShoppingListItemViewSet(viewsets.ModelViewSet):
    """ViewSet for ShoppingListItem model."""

    queryset = ShoppingListItem.objects.all()
    serializer_class = ShoppingListItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=["post"])
    def toggle_check(self, request, pk=None):
        """Toggle the checked status of a shopping list item."""
        item = self.get_object()
        item.is_checked = not item.is_checked
        item.save()
        
        serializer = self.get_serializer(item)
        return Response(serializer.data)
