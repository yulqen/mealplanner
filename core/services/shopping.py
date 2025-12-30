import re
from collections import Counter

from core.models import ShoppingList, ShoppingListItem, Store


def aggregate_quantities(quantities):
    """
    Aggregate a list of quantity strings into a readable format.

    Examples:
        ["1", "1", "1", "1"] → "4"
        ["2 slices", "2 slices", "2 slices"] → "6 slices"
        ["400g", "200g"] → "600g"
        ["1", "2", "3"] → "6"
        ["a handful", "a handful"] → "a handful ×2"
    """
    if not quantities:
        return ""

    if len(quantities) == 1:
        return quantities[0]

    # Try to parse and sum numeric quantities with same units
    parsed = []
    for q in quantities:
        q = q.strip()
        # Match patterns like "400g", "2 slices", "1.5 cups", "2"
        # Capture whether there's a space between number and unit
        match = re.match(r'^([\d.]+)(\s*)(.*)$', q)
        if match:
            try:
                num = float(match.group(1))
                has_space = bool(match.group(2))
                unit = match.group(3).strip()
                parsed.append((num, unit, has_space))
            except ValueError:
                parsed.append((None, q, False))
        else:
            parsed.append((None, q, False))

    # Check if all parsed successfully
    if all(p[0] is not None for p in parsed):
        # Group by unit (use first occurrence's spacing preference)
        by_unit = {}
        unit_spacing = {}
        for num, unit, has_space in parsed:
            if unit not in by_unit:
                by_unit[unit] = 0
                unit_spacing[unit] = has_space
            by_unit[unit] += num

        # Format results
        results = []
        for unit, total in by_unit.items():
            # Format number nicely (no decimal if whole number)
            if total == int(total):
                total = int(total)
            if unit:
                spacer = " " if unit_spacing[unit] else ""
                results.append(f"{total}{spacer}{unit}")
            else:
                results.append(str(total))

        return " + ".join(results) if len(results) > 1 else results[0]

    # Fall back to counting duplicates
    counts = Counter(quantities)
    results = []
    for qty, count in counts.items():
        if count > 1:
            results.append(f"{qty} ×{count}")
        else:
            results.append(qty)

    return ", ".join(results)


def generate_shopping_list(week_plan, store=None, created_by=None):
    """
    Generate a shopping list from a week plan.

    Aggregates ingredients across all recipes, respects pantry staples,
    and orders by store-specific category order.

    Args:
        week_plan: WeekPlan instance
        store: Store instance (uses default if None)
        created_by: User instance

    Returns:
        ShoppingList instance with items
    """
    # Get store (use default if not specified)
    if store is None:
        store = Store.objects.filter(is_default=True).first()
        if store is None:
            store = Store.objects.first()

    # Collect all recipe ingredients from planned meals
    # {ingredient_id: {'ingredient': obj, 'quantities': [], 'is_pantry': bool}}
    ingredient_quantities = {}

    for planned_meal in week_plan.planned_meals.select_related("recipe").all():
        if not planned_meal.recipe:
            continue

        for ri in planned_meal.recipe.recipe_ingredients.select_related(
            "ingredient__category"
        ).all():
            ing = ri.ingredient

            if ing.id not in ingredient_quantities:
                ingredient_quantities[ing.id] = {
                    "ingredient": ing,
                    "quantities": [],
                    "is_pantry": ing.is_pantry_staple,
                }
            ingredient_quantities[ing.id]["quantities"].append(ri.quantity)

    # Create shopping list
    shopping_list = ShoppingList.objects.create(
        name=f"Shopping for {week_plan}",
        week_plan=week_plan,
        store=store,
        created_by=created_by,
        is_active=True,
    )

    # Get store category ordering
    category_order = {
        sco.category_id: sco.sort_order for sco in store.category_orders.all()
    }

    # Create items
    items = []
    for data in ingredient_quantities.values():
        ing = data["ingredient"]
        quantities = data["quantities"]
        is_pantry = data["is_pantry"]

        # Aggregate quantities intelligently
        aggregated = aggregate_quantities(quantities)

        item = ShoppingListItem(
            shopping_list=shopping_list,
            ingredient=ing,
            name=ing.name,
            category=ing.category,
            quantities=aggregated,
            is_pantry_item=is_pantry,
        )
        items.append(item)

    # Bulk create
    ShoppingListItem.objects.bulk_create(items)

    return shopping_list


def get_sorted_items(shopping_list):
    """
    Get shopping list items sorted by store category order.

    Returns items grouped by category in store-specific order.
    """
    store = shopping_list.store

    # Get category ordering for this store
    category_order = {}
    if store:
        category_order = {
            sco.category_id: sco.sort_order for sco in store.category_orders.all()
        }

    # Get all items
    items = shopping_list.items.select_related("category", "ingredient").all()

    # Sort by category order, then by checked status, then by name
    def sort_key(item):
        cat_order = category_order.get(item.category_id, 999) if item.category else 999
        return (item.is_checked, cat_order, item.name.lower())

    sorted_items = sorted(items, key=sort_key)

    # Group by category
    grouped = {}
    for item in sorted_items:
        cat_name = item.category.name if item.category else "Other"
        cat_id = item.category_id if item.category else 0
        cat_order = category_order.get(cat_id, 999)

        if cat_name not in grouped:
            grouped[cat_name] = {"order": cat_order, "items": [], "category": item.category}
        grouped[cat_name]["items"].append(item)

    # Sort groups by order
    sorted_groups = sorted(grouped.items(), key=lambda x: x[1]["order"])

    return sorted_groups
