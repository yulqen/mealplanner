import markdown
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Prefetch
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import IngredientForm, RecipeForm, RecipeIngredientFormSet, WeekPlanForm, ShoppingListForm
from .models import Ingredient, MealType, PlannedMeal, Recipe, RecipeIngredient, ShoppingCategory, ShoppingList, WeekPlan
from .services.shuffle import shuffle_meals


def logout(request):
    """Logout view that accepts both GET and POST."""
    auth_logout(request)
    return redirect("login")


@login_required
def home(request):
    """Home page - redirect to recipe list."""
    return redirect("recipe_list")


@login_required
def recipe_list(request):
    """List recipes with filtering by meal type, difficulty, and search."""
    recipes = Recipe.objects.filter(is_archived=False).select_related("meal_type")

    # Annotate with stats
    recipes = recipes.annotate(
        times_made_count=Count("planned_meals"),
        last_made_date=Max("planned_meals__week_plan__start_date"),
    )

    # Filter by meal type
    meal_type_id = request.GET.get("meal_type")
    if meal_type_id:
        recipes = recipes.filter(meal_type_id=meal_type_id)

    # Filter by difficulty
    difficulty = request.GET.get("difficulty")
    if difficulty:
        recipes = recipes.filter(difficulty=difficulty)

    # Filter by ace tag
    ace_tag = request.GET.get("ace_tag")
    if ace_tag:
        recipes = recipes.filter(ace_tag=True)

    # Search by name
    search = request.GET.get("search", "").strip()
    if search:
        recipes = recipes.filter(name__icontains=search)

    # Sort
    sort = request.GET.get("sort", "name")
    if sort == "times_made":
        recipes = recipes.order_by("-times_made_count", "name")
    elif sort == "last_made":
        recipes = recipes.order_by("-last_made_date", "name")
    else:
        recipes = recipes.order_by("name")

    meal_types = MealType.objects.all()

    context = {
        "recipes": recipes,
        "meal_types": meal_types,
        "current_meal_type": meal_type_id,
        "current_difficulty": difficulty,
        "current_ace_tag": ace_tag,
        "current_search": search,
        "current_sort": sort,
    }

    # Return partial for HTMX requests
    if request.headers.get("HX-Request"):
        return render(request, "components/recipe_list_items.html", context)

    return render(request, "core/recipe_list.html", context)


@login_required
def recipe_detail(request, pk):
    """View recipe details - clean cooking view."""
    # Prefetch ingredients sorted by category name, then ingredient name
    # This ordering is required for the template's regroup tag to work correctly
    ingredients_prefetch = Prefetch(
        "recipe_ingredients",
        queryset=RecipeIngredient.objects.select_related(
            "ingredient__category"
        ).order_by("ingredient__category__name", "ingredient__name"),
    )
    recipe = get_object_or_404(
        Recipe.objects.select_related("meal_type").prefetch_related(
            ingredients_prefetch
        ),
        pk=pk,
    )

    # Render markdown instructions to HTML
    instructions_html = markdown.markdown(
        recipe.instructions, extensions=["nl2br", "fenced_code"]
    )

    # Get the referring page for back button
    referer = request.META.get("HTTP_REFERER", "")
    back_url = None
    if referer:
        from urllib.parse import urlparse

        parsed = urlparse(referer)
        if parsed.netloc == request.META.get("HTTP_HOST", "") or not parsed.netloc:
            path = parsed.path
            if path and path != request.path:
                back_url = path

    context = {
        "recipe": recipe,
        "instructions_html": instructions_html,
        "back_url": back_url,
        "recipe_list_url": "/recipes/",
    }
    return render(request, "core/recipe_detail.html", context)


@login_required
def recipe_markdown_preview(request):
    """HTMX endpoint to render markdown preview."""
    content = request.POST.get("instructions", "")
    html = markdown.markdown(content, extensions=["nl2br", "fenced_code"])
    return render(request, "components/markdown_preview.html", {"html": html})


@login_required
def recipe_create(request):
    """Create a new recipe."""
    if request.method == "POST":
        form = RecipeForm(request.POST)
        formset = RecipeIngredientFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            recipe = form.save()
            formset.instance = recipe
            formset.save()
            messages.success(request, f'Recipe "{recipe.name}" created successfully.')
            return redirect("recipe_detail", pk=recipe.pk)
    else:
        form = RecipeForm()
        formset = RecipeIngredientFormSet()

    context = {
        "form": form,
        "formset": formset,
        "title": "Add Recipe",
        "submit_text": "Create Recipe",
        "all_ingredients": Ingredient.objects.order_by("name"),
    }
    return render(request, "core/recipe_form.html", context)


@login_required
def recipe_edit(request, pk):
    """Edit an existing recipe."""
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == "POST":
        form = RecipeForm(request.POST, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)

        if form.is_valid() and formset.is_valid():
            recipe = form.save()
            formset.save()
            messages.success(request, f'Recipe "{recipe.name}" updated successfully.')
            return redirect("recipe_detail", pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)

    context = {
        "form": form,
        "formset": formset,
        "recipe": recipe,
        "title": f"Edit {recipe.name}",
        "submit_text": "Save Changes",
        "all_ingredients": Ingredient.objects.order_by("name"),
    }
    return render(request, "core/recipe_form.html", context)


@login_required
def recipe_delete(request, pk):
    """Delete a recipe with confirmation."""
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == "POST":
        name = recipe.name
        recipe.delete()
        messages.success(request, f'Recipe "{name}" deleted.')
        return redirect("recipe_list")

    context = {"recipe": recipe}
    return render(request, "core/recipe_delete.html", context)


# Ingredient Views


@login_required
def ingredient_list(request):
    """List ingredients with category filtering and search."""
    ingredients = Ingredient.objects.select_related("category").annotate(
        recipe_count=Count("recipe_ingredients")
    )

    # Filter by category
    category_id = request.GET.get("category")
    if category_id:
        ingredients = ingredients.filter(category_id=category_id)

    # Filter by pantry staple
    pantry = request.GET.get("pantry")
    if pantry == "yes":
        ingredients = ingredients.filter(is_pantry_staple=True)
    elif pantry == "no":
        ingredients = ingredients.filter(is_pantry_staple=False)

    # Search by name
    search = request.GET.get("search", "").strip()
    if search:
        ingredients = ingredients.filter(name__icontains=search)

    ingredients = ingredients.order_by("name")
    categories = ShoppingCategory.objects.all()

    context = {
        "ingredients": ingredients,
        "categories": categories,
        "current_category": category_id,
        "current_pantry": pantry,
        "current_search": search,
    }

    if request.headers.get("HX-Request"):
        return render(request, "components/ingredient_list_items.html", context)

    return render(request, "core/ingredient_list.html", context)


@login_required
def ingredient_create(request):
    """Create a new ingredient."""
    if request.method == "POST":
        form = IngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save()
            messages.success(
                request, f'Ingredient "{ingredient.name}" created successfully.'
            )
            return redirect("ingredient_list")
    else:
        form = IngredientForm()

    context = {
        "form": form,
        "title": "Add Ingredient",
        "submit_text": "Create Ingredient",
    }
    return render(request, "core/ingredient_form.html", context)


@login_required
def ingredient_edit(request, pk):
    """Edit an existing ingredient."""
    ingredient = get_object_or_404(Ingredient, pk=pk)

    if request.method == "POST":
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            ingredient = form.save()
            messages.success(
                request, f'Ingredient "{ingredient.name}" updated successfully.'
            )
            return redirect("ingredient_list")
    else:
        form = IngredientForm(instance=ingredient)

    context = {
        "form": form,
        "ingredient": ingredient,
        "title": f"Edit {ingredient.name}",
        "submit_text": "Save Changes",
    }
    return render(request, "core/ingredient_form.html", context)


@login_required
def ingredient_delete(request, pk):
    """Delete an ingredient with confirmation."""
    ingredient = get_object_or_404(Ingredient, pk=pk)

    # Check if ingredient is used in recipes
    recipe_count = ingredient.recipe_ingredients.count()

    if request.method == "POST":
        if recipe_count > 0:
            messages.error(
                request,
                f'Cannot delete "{ingredient.name}" - it is used in {recipe_count} recipe(s).',
            )
            return redirect("ingredient_list")

        name = ingredient.name
        ingredient.delete()
        messages.success(request, f'Ingredient "{name}" deleted.')
        return redirect("ingredient_list")

    context = {
        "ingredient": ingredient,
        "recipe_count": recipe_count,
    }
    return render(request, "core/ingredient_delete.html", context)


@login_required
def ingredient_autocomplete(request):
    """HTMX endpoint for ingredient autocomplete in recipe forms."""
    query = request.GET.get("q", "").strip()
    ingredients = []

    if len(query) >= 2:
        ingredients = Ingredient.objects.filter(name__icontains=query).order_by(
            "name"
        )[:10]

    context = {
        "ingredients": ingredients,
        "query": query,
    }
    return render(request, "components/ingredient_autocomplete.html", context)


@login_required
def ingredient_create_inline(request):
    """HTMX endpoint for creating ingredient inline from recipe form."""
    if request.method == "POST":
        form = IngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save()
            # Return the new ingredient as an option to be inserted
            return render(
                request,
                "components/ingredient_created.html",
                {"ingredient": ingredient},
            )
        else:
            return render(
                request,
                "components/ingredient_inline_form.html",
                {"form": form, "show_form": True},
            )

    # GET request - show the form
    name = request.GET.get("name", "")
    form = IngredientForm(initial={"name": name})
    return render(
        request,
        "components/ingredient_inline_form.html",
        {"form": form, "show_form": True, "initial_name": name},
    )


# Week Plan Views


@login_required
def plan_list(request):
    """List all week plans."""
    plans = WeekPlan.objects.all().prefetch_related("planned_meals__recipe")

    context = {"plans": plans}
    return render(request, "core/plan_list.html", context)


@login_required
def plan_create(request):
    """Create a new week plan."""
    if request.method == "POST":
        form = WeekPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.save()

            # Optionally shuffle immediately
            if request.POST.get("shuffle"):
                shuffle_meals(plan)

            messages.success(request, f"Week plan created for {plan.start_date}.")
            return redirect("plan_detail", pk=plan.pk)
    else:
        form = WeekPlanForm()

    context = {
        "form": form,
        "title": "Create Week Plan",
    }
    return render(request, "core/plan_form.html", context)


@login_required
def plan_detail(request, pk):
    """View and edit a week plan."""
    plan = get_object_or_404(
        WeekPlan.objects.prefetch_related("planned_meals__recipe__meal_type"), pk=pk
    )

    # Build list of days with their planned meals
    from datetime import timedelta

    days = []
    for i in range(7):
        day_date = plan.start_date + timedelta(days=i)
        planned_meal = plan.planned_meals.filter(
            day_offset=i, is_supplementary=False
        ).first()
        supplementary_meal = plan.planned_meals.filter(
            day_offset=i, is_supplementary=True
        ).first()
        days.append(
            {
                "offset": i,
                "date": day_date,
                "day_name": day_date.strftime("%A"),
                "planned_meal": planned_meal,
                "supplementary_meal": supplementary_meal,
            }
        )

    # Get all active recipes for the assign dropdown
    recipes = Recipe.objects.filter(is_archived=False).select_related("meal_type")

    context = {
        "plan": plan,
        "days": days,
        "recipes": recipes,
    }
    return render(request, "core/plan_detail.html", context)


@login_required
def plan_delete(request, pk):
    """Delete a week plan with confirmation."""
    plan = get_object_or_404(WeekPlan, pk=pk)

    if request.method == "POST":
        start_date = plan.start_date
        plan.delete()
        messages.success(request, f"Week plan for {start_date.strftime('%d %b %Y')} deleted.")
        return redirect("plan_list")

    context = {"plan": plan}
    return render(request, "core/plan_delete.html", context)


@login_required
def plan_shuffle(request, pk):
    """HTMX endpoint to shuffle all meals for a week plan."""
    plan = get_object_or_404(WeekPlan, pk=pk)

    if request.method == "POST":
        if plan.is_locked:
            messages.error(request, "This plan is locked and cannot be shuffled.")
        else:
            shuffle_meals(plan)
            messages.success(request, "Meals shuffled!")

    return redirect("plan_detail", pk=pk)


@login_required
def plan_toggle_lock(request, pk):
    """View to toggle the lock status of a week plan."""
    plan = get_object_or_404(WeekPlan, pk=pk)

    if request.method == "POST":
        plan.is_locked = not plan.is_locked
        plan.save()
        status = "locked" if plan.is_locked else "unlocked"
        messages.success(request, f"Plan {status} successfully.")

    return redirect("plan_detail", pk=pk)


@login_required
def plan_assign(request, pk, day):
    """HTMX endpoint to assign a recipe to a specific day."""
    plan = get_object_or_404(WeekPlan, pk=pk)

    if request.method == "POST":
        recipe_id = request.POST.get("recipe_id")
        note = request.POST.get("note", "")

        # Get or create the planned meal for this day (main meal, not supplementary)
        planned_meal, created = PlannedMeal.objects.get_or_create(
            week_plan=plan, day_offset=day, is_supplementary=False, defaults={"note": note}
        )

        if recipe_id:
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            planned_meal.recipe = recipe
            planned_meal.note = ""
        else:
            planned_meal.recipe = None
            planned_meal.note = note

        planned_meal.save()

    # Return the updated day slot partial
    from datetime import timedelta

    day_date = plan.start_date + timedelta(days=day)
    planned_meal = plan.planned_meals.filter(
        day_offset=day, is_supplementary=False
    ).first()
    supplementary_meal = plan.planned_meals.filter(
        day_offset=day, is_supplementary=True
    ).first()

    context = {
        "plan": plan,
        "day": {
            "offset": day,
            "date": day_date,
            "day_name": day_date.strftime("%A"),
            "planned_meal": planned_meal,
            "supplementary_meal": supplementary_meal,
        },
        "recipes": Recipe.objects.filter(is_archived=False).select_related("meal_type"),
    }
    return render(request, "components/plan_day_slot.html", context)


@login_required
def plan_clear_day(request, pk, day):
    """HTMX endpoint to clear a recipe from a specific day."""
    plan = get_object_or_404(WeekPlan, pk=pk)

    if request.method == "POST":
        PlannedMeal.objects.filter(week_plan=plan, day_offset=day).delete()

    # Return the updated day slot partial
    from datetime import timedelta

    day_date = plan.start_date + timedelta(days=day)

    context = {
        "plan": plan,
        "day": {
            "offset": day,
            "date": day_date,
            "day_name": day_date.strftime("%A"),
            "planned_meal": None,
            "supplementary_meal": None,
        },
        "recipes": Recipe.objects.filter(is_archived=False).select_related("meal_type"),
    }
    return render(request, "components/plan_day_slot.html", context)


@login_required
def plan_assign_supplementary(request, pk, day):
    """HTMX endpoint to assign a supplementary recipe (e.g., kids' meal) to a specific day."""
    plan = get_object_or_404(WeekPlan, pk=pk)

    if request.method == "POST":
        recipe_id = request.POST.get("recipe_id")
        for_people = request.POST.get("for_people", "")

        if recipe_id:
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            # Get or create the supplementary meal for this day
            supplementary_meal, created = PlannedMeal.objects.get_or_create(
                week_plan=plan, day_offset=day, is_supplementary=True
            )
            supplementary_meal.recipe = recipe
            supplementary_meal.for_people = for_people
            supplementary_meal.save()

    # Return the updated day slot partial
    from datetime import timedelta

    day_date = plan.start_date + timedelta(days=day)
    planned_meal = plan.planned_meals.filter(
        day_offset=day, is_supplementary=False
    ).first()
    supplementary_meal = plan.planned_meals.filter(
        day_offset=day, is_supplementary=True
    ).first()

    context = {
        "plan": plan,
        "day": {
            "offset": day,
            "date": day_date,
            "day_name": day_date.strftime("%A"),
            "planned_meal": planned_meal,
            "supplementary_meal": supplementary_meal,
        },
        "recipes": Recipe.objects.filter(is_archived=False).select_related("meal_type"),
    }
    return render(request, "components/plan_day_slot.html", context)


@login_required
def plan_clear_supplementary(request, pk, day):
    """HTMX endpoint to clear a supplementary recipe from a specific day."""
    plan = get_object_or_404(WeekPlan, pk=pk)

    if request.method == "POST":
        PlannedMeal.objects.filter(
            week_plan=plan, day_offset=day, is_supplementary=True
        ).delete()

    # Return the updated day slot partial
    from datetime import timedelta

    day_date = plan.start_date + timedelta(days=day)
    planned_meal = plan.planned_meals.filter(
        day_offset=day, is_supplementary=False
    ).first()

    context = {
        "plan": plan,
        "day": {
            "offset": day,
            "date": day_date,
            "day_name": day_date.strftime("%A"),
            "planned_meal": planned_meal,
            "supplementary_meal": None,
        },
        "recipes": Recipe.objects.filter(is_archived=False).select_related("meal_type"),
    }
    return render(request, "components/plan_day_slot.html", context)


@login_required
def plan_toggle_pin(request, pk, meal_pk):
    """HTMX endpoint to toggle the pin status of a planned meal."""
    plan = get_object_or_404(WeekPlan, pk=pk)
    planned_meal = get_object_or_404(PlannedMeal, pk=meal_pk, week_plan=plan)

    if request.method == "POST":
        planned_meal.is_pinned = not planned_meal.is_pinned
        planned_meal.save()

    # Return the updated day slot partial
    from datetime import timedelta

    day_offset = planned_meal.day_offset
    day_date = plan.start_date + timedelta(days=day_offset)
    planned_meal = plan.planned_meals.filter(
        day_offset=day_offset, is_supplementary=False
    ).first()
    supplementary_meal = plan.planned_meals.filter(
        day_offset=day_offset, is_supplementary=True
    ).first()

    context = {
        "plan": plan,
        "day": {
            "offset": day_offset,
            "date": day_date,
            "day_name": day_date.strftime("%A"),
            "planned_meal": planned_meal,
            "supplementary_meal": supplementary_meal,
        },
        "recipes": Recipe.objects.filter(is_archived=False).select_related("meal_type"),
    }

    # Check if this is an HTMX request
    if request.headers.get("HX-Request"):
        return render(request, "components/plan_day_slot.html", context)
    else:
        # Fallback: redirect to plan detail page for non-HTMX requests
        return HttpResponseRedirect(reverse("plan_detail", kwargs={"pk": plan.pk}))


# Shopping List Views


@login_required
def shopping_list_create(request):
    """Create a new ad-hoc shopping list."""
    from .models import Store
    from django.http import HttpResponse

    if request.method == "POST":
        form = ShoppingListForm(request.POST)
        if form.is_valid():
            shopping_list_obj = form.save(commit=False)
            shopping_list_obj.created_by = request.user
            shopping_list_obj.save()
            messages.success(request, f'Shopping list "{shopping_list_obj.name}" created.')

            # For HTMX requests, return a redirect response
            if request.headers.get("HX-Request"):
                response = HttpResponse(status=204)
                response["HX-Redirect"] = f"/shopping/{shopping_list_obj.pk}/"
                return response

            return redirect("shopping_list", pk=shopping_list_obj.pk)
    else:
        form = ShoppingListForm()

    # Render modal for HTMX requests
    if request.headers.get("HX-Request"):
        return render(request, "core/shopping_list_create.html", {"form": form})

    # Fallback to full page
    stores = Store.objects.all()
    return render(
        request, "core/shopping_list_create.html", {"form": form, "stores": stores}
    )


@login_required
def shopping_list_delete(request, pk):
    """Delete a shopping list with appropriate warnings."""
    from .models import ShoppingList, Store

    shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)

    if request.method == "POST":
        # Check if this is the active list
        name = shopping_list_obj.name

        # Perform the deletion
        shopping_list_obj.delete()
        messages.success(request, f'Shopping list "{name}" deleted.')

        # Redirect to most recent other list
        next_list = ShoppingList.objects.first()
        if next_list:
            return redirect("shopping_list", pk=next_list.pk)
        else:
            return redirect("shopping_list_current")

    # GET request - show confirmation modal with appropriate warning
    if request.headers.get("HX-Request"):
        return render(
            request,
            "core/shopping_list_delete.html",
            {"shopping_list": shopping_list_obj},
        )

    # Fallback to full page
    stores = Store.objects.all()
    return render(
        request,
        "core/shopping_list_delete.html",
        {"shopping_list": shopping_list_obj, "stores": stores},
    )


@login_required
def shopping_list(request, pk=None):
    """View the current active shopping list or a specific one."""
    from .models import ShoppingList, Store
    from .services.shopping import get_sorted_items

    # Support query parameter for selecting list
    list_pk = request.GET.get("list")

    if pk:
        shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)
    elif list_pk:
        shopping_list_obj = get_object_or_404(ShoppingList, pk=list_pk)
    else:
        # Get the best default shopping list, in priority order:
        # 1. The active list
        # 2. The most recent list linked to a meal plan
        # 3. The most recent list (any)
        shopping_list_obj = (
            ShoppingList.objects.filter(is_active=True).first()
            or ShoppingList.objects.filter(week_plan__isnull=False).first()
            or ShoppingList.objects.first()
        )
        if not shopping_list_obj:
            # No shopping list - show empty state
            all_lists = ShoppingList.objects.all()
            stores = Store.objects.all()
            return render(
                request, "core/shopping_list.html", {"shopping_list": None, "stores": stores, "all_lists": all_lists}
            )

    # Get items grouped by category
    grouped_items = get_sorted_items(shopping_list_obj)
    stores = Store.objects.all()
    categories = ShoppingCategory.objects.all()
    all_lists = ShoppingList.objects.all()

    # Check if list is stale (meal plan was modified after list was generated)
    is_stale = shopping_list_obj.is_stale

    context = {
        "shopping_list": shopping_list_obj,
        "grouped_items": grouped_items,
        "stores": stores,
        "categories": categories,
        "all_lists": all_lists,
        "is_stale": is_stale,
    }

    # For HTMX polling, return just the items partial
    if request.headers.get("HX-Request") and request.GET.get("items_only"):
        return render(request, "components/shopping_items_only.html", context)

    return render(request, "core/shopping_list.html", context)


@login_required
def shopping_generate(request, plan_pk):
    """Generate a shopping list from a week plan."""
    from .models import ShoppingList, Store
    from .services.shopping import generate_shopping_list, format_regeneration_message

    plan = get_object_or_404(WeekPlan, pk=plan_pk)

    if request.method == "POST":
        # Get store from form or use default
        store_id = request.POST.get("store")
        store = None
        if store_id:
            store = get_object_or_404(Store, pk=store_id)

        # Check if there's an existing shopping list for this week plan
        existing_list = ShoppingList.objects.filter(week_plan=plan).first()
        if existing_list:
            shopping_list_obj = existing_list
        else:
            # Deactivate any existing active shopping lists before creating new one
            ShoppingList.objects.filter(is_active=True).update(is_active=False)
            shopping_list_obj = None

        # Generate the list (will create or add to existing)
        # Always regenerate quantities from current recipes when explicitly generating
        shopping_list_obj, changes = generate_shopping_list(
            week_plan=plan, store=store, created_by=request.user, shopping_list=shopping_list_obj,
            replace=True, return_changes=True
        )

        # Show detailed message about what changed
        message = format_regeneration_message(changes)
        messages.success(request, message)
        return redirect("shopping_list", pk=shopping_list_obj.pk)

    # GET - show store selection if multiple stores exist
    stores = Store.objects.all()
    if stores.count() <= 1:
        # Just generate with default store
        existing_list = ShoppingList.objects.filter(week_plan=plan).first()
        if existing_list:
            shopping_list_obj = existing_list
        else:
            ShoppingList.objects.filter(is_active=True).update(is_active=False)
            shopping_list_obj = None

        shopping_list_obj, changes = generate_shopping_list(
            week_plan=plan, store=stores.first(), created_by=request.user,
            shopping_list=shopping_list_obj, replace=True, return_changes=True
        )
        message = format_regeneration_message(changes)
        messages.success(request, message)
        return redirect("shopping_list", pk=shopping_list_obj.pk)

    context = {
        "plan": plan,
        "stores": stores,
    }
    return render(request, "core/shopping_generate.html", context)


@login_required
def shopping_check(request, pk, item_pk):
    """HTMX endpoint to toggle an item's checked status."""
    from .models import ShoppingListItem

    shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)
    item = get_object_or_404(ShoppingListItem, pk=item_pk, shopping_list=shopping_list_obj)

    if request.method == "POST":
        item.is_checked = not item.is_checked
        item.save()

    # Return the updated item row
    context = {
        "item": item,
        "shopping_list": shopping_list_obj,
    }
    return render(request, "components/shopping_item_row.html", context)


@login_required
def shopping_star(request, pk, item_pk):
    """HTMX endpoint to toggle an item's star status."""
    from .models import ShoppingListItem

    shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)
    item = get_object_or_404(ShoppingListItem, pk=item_pk, shopping_list=shopping_list_obj)

    if request.method == "POST":
        item.is_starred = not item.is_starred
        item.save()

    # Return the updated item row
    context = {
        "item": item,
        "shopping_list": shopping_list_obj,
    }
    return render(request, "components/shopping_item_row.html", context)


@login_required
def shopping_add(request, pk):
    """HTMX endpoint to add a manual item to the shopping list."""
    from .models import ShoppingListItem
    from .services.shopping import get_sorted_items

    shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category_id = request.POST.get("category")
        quantities = request.POST.get("quantities", "").strip()
        ingredient_id = request.POST.get("ingredient_id")

        if name:
            # Get category from ingredient if available, otherwise from form
            category = None
            ingredient = None

            if ingredient_id:
                ingredient = Ingredient.objects.filter(pk=ingredient_id).first()
                if ingredient:
                    category = ingredient.category

            if not category and category_id:
                category = ShoppingCategory.objects.filter(pk=category_id).first()

            ShoppingListItem.objects.create(
                shopping_list=shopping_list_obj,
                ingredient=ingredient,
                name=name,
                category=category,
                quantities=quantities,
                is_manual=True,
            )

    # Return updated items list
    grouped_items = get_sorted_items(shopping_list_obj)
    context = {
        "shopping_list": shopping_list_obj,
        "grouped_items": grouped_items,
    }
    return render(request, "components/shopping_items_only.html", context)


@login_required
def shopping_item_autocomplete(request, pk):
    """HTMX endpoint for autocomplete when adding items to shopping list."""

    shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)
    query = request.GET.get("name", "").strip()

    context = {"query": query, "ingredients": [], "existing_items": []}

    if len(query) >= 2:
        # Search ingredients
        ingredients = Ingredient.objects.filter(
            name__icontains=query
        ).select_related("category").order_by("name")[:8]

        # Check which items are already in the shopping list
        existing_items = shopping_list_obj.items.filter(
            name__icontains=query
        ).order_by("name")[:5]

        context["ingredients"] = ingredients
        context["existing_items"] = existing_items

    return render(request, "components/shopping_item_autocomplete.html", context)


@login_required
def shopping_clear(request, pk):
    """Clear checked items from a shopping list."""
    import json
    from .services.shopping import get_sorted_items

    shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)
    
    toast_message = None
    toast_type = None

    if request.method == "POST":
        # Clear only checked items - 'all' is no longer supported
        count = shopping_list_obj.items.filter(is_checked=True).delete()[0]
        if count > 0:
            toast_message = f"{count} checked item(s) cleared."
            toast_type = "success"
        else:
            toast_message = "No checked items to clear."
            toast_type = "info"

    # For HTMX requests, return the items partial
    if request.headers.get("HX-Request"):
        grouped_items = get_sorted_items(shopping_list_obj)
        context = {
            "shopping_list": shopping_list_obj,
            "grouped_items": grouped_items,
        }
        response = render(request, "components/shopping_items_only.html", context)
        
        # Add toast notification via HX-Trigger header for HTMX requests
        if toast_message:
            trigger_data = {
                "showToast": {
                    "message": toast_message,
                    "type": toast_type
                }
            }
            response["HX-Trigger"] = json.dumps(trigger_data)
        
        return response

    # For non-HTMX requests, add messages to framework
    if toast_message:
        if toast_type == "success":
            messages.success(request, toast_message)
        else:
            messages.info(request, toast_message)
    
    return redirect("shopping_list", pk=pk)


@login_required
def shopping_change_store(request, pk):
    """Change the store for a shopping list (re-sorts items)."""
    from .models import Store
    from .services.shopping import get_sorted_items

    shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)

    if request.method == "POST":
        store_id = request.POST.get("store")
        if store_id:
            store = get_object_or_404(Store, pk=store_id)
            shopping_list_obj.store = store
            shopping_list_obj.save()

    # Return updated items list with new ordering
    grouped_items = get_sorted_items(shopping_list_obj)
    context = {
        "shopping_list": shopping_list_obj,
        "grouped_items": grouped_items,
    }

    if request.headers.get("HX-Request"):
        return render(request, "components/shopping_items_only.html", context)

    return redirect("shopping_list", pk=pk)


@login_required
def shopping_edit_category(request, pk, item_pk):
    """HTMX endpoint to change category for a manual shopping list item."""
    from .models import ShoppingListItem

    shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)
    item = get_object_or_404(ShoppingListItem, pk=item_pk, shopping_list=shopping_list_obj)

    if request.method == "POST":
        category_id = request.POST.get("category")
        if category_id:
            category = get_object_or_404(ShoppingCategory, pk=category_id)
            item.category = category
            item.save()
            messages.success(request, f'Category updated for "{item.name}".')
        else:
            item.category = None
            item.save()
            messages.success(request, f'Category removed for "{item.name}".')

        # Return updated items list
        from .services.shopping import get_sorted_items

        grouped_items = get_sorted_items(shopping_list_obj)
        context = {
            "shopping_list": shopping_list_obj,
            "grouped_items": grouped_items,
        }
        return render(request, "components/shopping_items_only.html", context)

    # GET request - render the modal form
    context = {
        "item": item,
        "shopping_list": shopping_list_obj,
        "categories": ShoppingCategory.objects.all(),
    }
    return render(request, "components/shopping_item_category_modal.html", context)


@login_required
def shopping_item_move(request, pk, item_pk):
    """HTMX endpoint to move a shopping list item to another list."""
    from .models import ShoppingListItem

    shopping_list_obj = get_object_or_404(ShoppingList, pk=pk)
    item = get_object_or_404(ShoppingListItem, pk=item_pk, shopping_list=shopping_list_obj)

    # Get available shopping lists (excluding current list)
    available_lists = ShoppingList.objects.filter(
        created_by=request.user
    ).exclude(pk=shopping_list_obj.pk)

    if request.method == "POST":
        destination_list_id = request.POST.get("destination_list")

        if not destination_list_id:
            return HttpResponse("No destination list selected", status=400)

        destination_list = get_object_or_404(
            ShoppingList,
            pk=destination_list_id,
            created_by=request.user
        )

        # Check if destination is the current list
        if destination_list.pk == shopping_list_obj.pk:
            return HttpResponse("Cannot move item to the same list", status=400)

        # Move the item
        item.shopping_list = destination_list
        item.save()

        messages.success(request, f'Moved "{item.name}" to {destination_list.name}.')

        # Return updated items list
        from .services.shopping import get_sorted_items

        grouped_items = get_sorted_items(shopping_list_obj)
        context = {
            "shopping_list": shopping_list_obj,
            "grouped_items": grouped_items,
        }
        return render(request, "components/shopping_items_only.html", context)

    # GET request - render the modal form
    context = {
        "item": item,
        "shopping_list": shopping_list_obj,
        "available_lists": available_lists,
    }
    return render(request, "components/shopping_item_move_modal.html", context)


@login_required
@csrf_exempt
def recipe_toggle_ace(request, pk):
    """HTMX endpoint to toggle ace tag on a recipe."""
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.ace_tag = not recipe.ace_tag
    recipe.save()

    context = {"recipe": recipe}

    if request.headers.get("HX-Request"):
        if "card" in request.GET:
            return render(request, "components/recipe_ace_tag_card.html", context)
        return render(request, "components/recipe_ace_tag_detail.html", context)

    return redirect("recipe_detail", pk=pk)


@login_required
def recipe_duplicate(request, pk):
    """Create a duplicate of an existing recipe."""
    source_recipe = get_object_or_404(Recipe, pk=pk)
    
    # Create the new recipe by copying fields
    new_recipe = Recipe.objects.create(
        name=f"{source_recipe.name} COPY",
        meal_type=source_recipe.meal_type,
        difficulty=source_recipe.difficulty,
        instructions=source_recipe.instructions,
        reference=source_recipe.reference,
        ace_tag=False,  # Don't copy ace tag by default
    )
    
    # Copy recipe ingredients
    for ri in source_recipe.recipe_ingredients.all():
        RecipeIngredient.objects.create(
            recipe=new_recipe,
            ingredient=ri.ingredient,
            quantity=ri.quantity,
        )

    messages.success(request, f"Recipe '{source_recipe.name}' duplicated as '{new_recipe.name}'.")
    return redirect("recipe_edit", pk=new_recipe.pk)


@login_required
def shopping_dismiss_notification(request, pk):
    """HTMX endpoint to dismiss the stale shopping list notification.
    Returns empty response so HTMX can swap-delete the notification element.
    """
    # Just return empty response - HTMX will remove the element
    return HttpResponse("", status=200)
