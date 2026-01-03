from django.conf import settings
from django.db import models


class MealType(models.Model):
    """Categorises recipes by their primary carbohydrate/base."""

    name = models.CharField(max_length=50, unique=True)
    colour = models.CharField(max_length=7, default="#6B7280")  # Hex colour for UI

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ShoppingCategory(models.Model):
    """Intrinsic category for ingredients (what type of product it is)."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Shopping categories"

    def __str__(self):
        return self.name


class Store(models.Model):
    """Represents a supermarket with its own aisle ordering."""

    name = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Ensure only one default store
        if self.is_default:
            Store.objects.filter(is_default=True).exclude(pk=self.pk).update(
                is_default=False
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class StoreCategoryOrder(models.Model):
    """Maps shopping categories to sort order for each store."""

    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="category_orders"
    )
    category = models.ForeignKey(ShoppingCategory, on_delete=models.CASCADE)
    sort_order = models.PositiveIntegerField()

    class Meta:
        unique_together = ["store", "category"]
        ordering = ["store", "sort_order"]

    def __str__(self):
        return f"{self.store.name}: {self.category.name} ({self.sort_order})"


class Ingredient(models.Model):
    """A distinct ingredient that can be used in recipes."""

    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(
        ShoppingCategory, on_delete=models.PROTECT, related_name="ingredients"
    )
    is_pantry_staple = models.BooleanField(
        default=False, help_text="If true, flagged on shopping lists for verification"
    )
    default_unit = models.CharField(
        max_length=30, blank=True, help_text="e.g., 'g', 'ml', 'medium', 'tin'"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """A meal recipe with ingredients and instructions."""

    DIFFICULTY_CHOICES = [
        (1, "Easy"),
        (2, "Medium"),
        (3, "Hard"),
    ]

    name = models.CharField(max_length=200)
    meal_type = models.ForeignKey(
        MealType, on_delete=models.PROTECT, related_name="recipes"
    )
    difficulty = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_CHOICES, null=True, blank=True
    )
    instructions = models.TextField(help_text="Markdown supported")
    reference = models.URLField(
        blank=True, help_text="Link to the original recipe online"
    )
    is_archived = models.BooleanField(
        default=False, help_text="Hidden from active recipe lists"
    )
    ace_tag = models.BooleanField(
        default=False, help_text="Marked as a favourite recipe"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def times_made(self):
        """Count how many times this recipe has been in a meal plan."""
        return self.planned_meals.count()

    def last_made(self):
        """Return the most recent date this recipe was planned."""
        last_plan = (
            self.planned_meals.select_related("week_plan")
            .order_by("-week_plan__start_date")
            .first()
        )
        if last_plan:
            return last_plan.actual_date()
        return None


class RecipeIngredient(models.Model):
    """Join table linking recipes to ingredients with quantities."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, related_name="recipe_ingredients"
    )
    quantity = models.CharField(
        max_length=50, help_text="Free text, e.g., '2', '400g', 'a handful'"
    )

    class Meta:
        unique_together = ["recipe", "ingredient"]
        ordering = ["ingredient__name"]

    def __str__(self):
        return f"{self.quantity} {self.ingredient.name}"


class WeekPlan(models.Model):
    """A meal plan for a specific week."""

    start_date = models.DateField(
        unique=True, help_text="Should be a Sunday or Monday depending on preference"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, help_text="When the plan was last modified")

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"Week of {self.start_date.strftime('%d %b %Y')}"


class PlannedMeal(models.Model):
    """A single meal assigned to a day within a week plan."""

    week_plan = models.ForeignKey(
        WeekPlan, on_delete=models.CASCADE, related_name="planned_meals"
    )
    day_offset = models.PositiveSmallIntegerField(
        help_text="0=start_date, 1=start_date+1 day, etc."
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="planned_meals",
    )
    note = models.CharField(
        max_length=200, blank=True, help_text="e.g., 'Eating out', 'Leftovers'"
    )
    is_supplementary = models.BooleanField(
        default=False,
        help_text="True for supplementary meals (e.g., kids' meals)",
    )
    for_people = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., 'Harvey and Sophie' - who this meal is for",
    )

    class Meta:
        unique_together = ["week_plan", "day_offset", "is_supplementary"]
        ordering = ["week_plan", "day_offset", "is_supplementary"]

    def actual_date(self):
        """Return the actual date for this planned meal."""
        from datetime import timedelta

        return self.week_plan.start_date + timedelta(days=self.day_offset)

    def __str__(self):
        date_str = self.actual_date().strftime("%a %d %b")
        prefix = "(Supp) " if self.is_supplementary else ""
        if self.recipe:
            return f"{date_str}: {prefix}{self.recipe.name}"
        return f"{date_str}: {prefix}{self.note or 'No meal'}"


class ShoppingList(models.Model):
    """A shopping list generated from a week plan (or manual)."""

    name = models.CharField(max_length=100, default="Shopping List")
    week_plan = models.ForeignKey(
        WeekPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shopping_lists",
    )
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    generated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this list was last generated from a meal plan",
    )
    is_active = models.BooleanField(
        default=True, help_text="The current shopping list in use"
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Ensure only one active shopping list
        if self.is_active:
            ShoppingList.objects.filter(is_active=True).exclude(pk=self.pk).update(
                is_active=False
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.created_at.strftime('%d %b %Y')})"

    @property
    def checked_count(self):
        """Return count of checked items."""
        return self.items.filter(is_checked=True).count()

    @property
    def is_stale(self):
        """Check if the shopping list is stale (meal plan was modified after list was generated)."""
        if not self.week_plan or not self.generated_at:
            return False
        return self.week_plan.modified_at > self.generated_at


class ShoppingListItem(models.Model):
    """An item on a shopping list."""

    shopping_list = models.ForeignKey(
        ShoppingList, on_delete=models.CASCADE, related_name="items"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(
        max_length=100, help_text="For manual items without an ingredient link"
    )
    category = models.ForeignKey(
        ShoppingCategory, on_delete=models.SET_NULL, null=True
    )
    quantities = models.TextField(
        help_text="Aggregated quantities, e.g., '400g, 200g' or '2, 1'"
    )
    is_checked = models.BooleanField(default=False)
    is_manual = models.BooleanField(
        default=False, help_text="Manually added item (not from recipe)"
    )
    is_pantry_override = models.BooleanField(
        default=False, help_text="Manually added despite being a pantry staple"
    )
    is_pantry_item = models.BooleanField(
        default=False, help_text="Item is a pantry staple (included for verification)"
    )
    is_starred = models.BooleanField(
        default=False, help_text="User marked as checked in pantry"
    )

    class Meta:
        ordering = ["shopping_list", "category", "name"]

    def __str__(self):
        return f"{self.name}: {self.quantities}"
