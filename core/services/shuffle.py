from random import choice

from core.models import MealType, PlannedMeal, Recipe


def shuffle_meals(week_plan, num_days=7):
    """
    Assign random recipes to each day, ensuring no consecutive days
    have the same meal type.

    Args:
        week_plan: WeekPlan instance
        num_days: Number of days to fill (default 7)

    Returns:
        List of PlannedMeal instances (saved)
    """
    # Clear existing main planned meals (preserve supplementary meals)
    week_plan.planned_meals.filter(is_supplementary=False).delete()

    # Get all active recipes grouped by meal type
    recipes_by_type = {}
    for meal_type in MealType.objects.all():
        recipes = list(Recipe.objects.filter(meal_type=meal_type, is_archived=False))
        if recipes:
            recipes_by_type[meal_type.id] = recipes

    if not recipes_by_type:
        return []

    planned_meals = []
    previous_type_id = None

    for day_offset in range(num_days):
        # Get available types (excluding previous day's type)
        available_type_ids = [
            type_id
            for type_id in recipes_by_type.keys()
            if type_id != previous_type_id
        ]

        if not available_type_ids:
            # Fallback: only one meal type exists, allow repeat
            available_type_ids = list(recipes_by_type.keys())

        # Pick random type, then random recipe from that type
        chosen_type_id = choice(available_type_ids)
        chosen_recipe = choice(recipes_by_type[chosen_type_id])

        planned_meal = PlannedMeal.objects.create(
            week_plan=week_plan,
            day_offset=day_offset,
            recipe=chosen_recipe,
            is_supplementary=False,
        )
        planned_meals.append(planned_meal)
        previous_type_id = chosen_type_id

    return planned_meals
