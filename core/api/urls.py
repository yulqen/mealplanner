"""
API URL routing for Meal Planner.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r"meal-types", views.MealTypeViewSet)
router.register(r"shopping-categories", views.ShoppingCategoryViewSet)
router.register(r"stores", views.StoreViewSet)
router.register(r"store-category-orders", views.StoreCategoryOrderViewSet)
router.register(r"ingredients", views.IngredientViewSet)
router.register(r"recipe-ingredients", views.RecipeIngredientViewSet)
router.register(r"recipes", views.RecipeViewSet)
router.register(r"week-plans", views.WeekPlanViewSet)
router.register(r"planned-meals", views.PlannedMealViewSet)
router.register(r"shopping-lists", views.ShoppingListViewSet)
router.register(r"shopping-list-items", views.ShoppingListItemViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
