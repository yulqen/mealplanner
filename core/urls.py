from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("logout/", views.logout, name="logout"),
    # Recipes
    path("recipes/", views.recipe_list, name="recipe_list"),
    path("recipes/new/", views.recipe_create, name="recipe_create"),
    path("recipes/<int:pk>/", views.recipe_detail, name="recipe_detail"),
    path("recipes/<int:pk>/edit/", views.recipe_edit, name="recipe_edit"),
    path("recipes/<int:pk>/delete/", views.recipe_delete, name="recipe_delete"),
    path("recipes/<int:pk>/toggle-ace/", views.recipe_toggle_ace, name="recipe_toggle_ace"),
    # Ingredients
    path("ingredients/", views.ingredient_list, name="ingredient_list"),
    path("ingredients/new/", views.ingredient_create, name="ingredient_create"),
    path("ingredients/<int:pk>/edit/", views.ingredient_edit, name="ingredient_edit"),
    path(
        "ingredients/<int:pk>/delete/", views.ingredient_delete, name="ingredient_delete"
    ),
    # Ingredient HTMX endpoints
    path(
        "ingredients/autocomplete/",
        views.ingredient_autocomplete,
        name="ingredient_autocomplete",
    ),
    path(
        "ingredients/create-inline/",
        views.ingredient_create_inline,
        name="ingredient_create_inline",
    ),
    # Week Plans
    path("plans/", views.plan_list, name="plan_list"),
    path("plans/new/", views.plan_create, name="plan_create"),
    path("plans/<int:pk>/", views.plan_detail, name="plan_detail"),
    path("plans/<int:pk>/delete/", views.plan_delete, name="plan_delete"),
    path("plans/<int:pk>/shuffle/", views.plan_shuffle, name="plan_shuffle"),
    path("plans/<int:pk>/toggle-lock/", views.plan_toggle_lock, name="plan_toggle_lock"),
    path("plans/<int:pk>/assign/<int:day>/", views.plan_assign, name="plan_assign"),
    path(
        "plans/<int:pk>/clear/<int:day>/", views.plan_clear_day, name="plan_clear_day"
    ),
    path(
        "plans/<int:pk>/assign-supplementary/<int:day>/",
        views.plan_assign_supplementary,
        name="plan_assign_supplementary",
    ),
    path(
        "plans/<int:pk>/clear-supplementary/<int:day>/",
        views.plan_clear_supplementary,
        name="plan_clear_supplementary",
    ),
    # Shopping Lists
    path("shopping/", views.shopping_list, name="shopping_list_current"),
    path("shopping/new/", views.shopping_list_create, name="shopping_list_create"),
    path("shopping/<int:pk>/", views.shopping_list, name="shopping_list"),
    path(
        "shopping/<int:pk>/delete/", views.shopping_list_delete, name="shopping_list_delete"
    ),
    path(
        "shopping/generate/<int:plan_pk>/",
        views.shopping_generate,
        name="shopping_generate",
    ),
    path(
        "shopping/<int:pk>/check/<int:item_pk>/",
        views.shopping_check,
        name="shopping_check",
    ),
    path(
        "shopping/<int:pk>/star/<int:item_pk>/",
        views.shopping_star,
        name="shopping_star",
    ),
    path("shopping/<int:pk>/add/", views.shopping_add, name="shopping_add"),
    path(
        "shopping/<int:pk>/autocomplete/",
        views.shopping_item_autocomplete,
        name="shopping_item_autocomplete",
    ),
    path("shopping/<int:pk>/clear/", views.shopping_clear, name="shopping_clear"),
    path(
        "shopping/<int:pk>/change-store/",
        views.shopping_change_store,
        name="shopping_change_store",
    ),
    path(
        "shopping/<int:pk>/edit-category/<int:item_pk>/",
        views.shopping_edit_category,
        name="shopping_edit_category",
    ),
]
