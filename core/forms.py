from datetime import date, timedelta

from django import forms

from .models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCategory,
    ShoppingList,
    ShoppingListItem,
    WeekPlan,
)


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "meal_type", "difficulty", "instructions", "reference"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                    "placeholder": "Recipe name",
                }
            ),
            "meal_type": forms.Select(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                }
            ),
            "difficulty": forms.Select(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                }
            ),
            "instructions": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                    "rows": 10,
                    "placeholder": "Enter cooking instructions (Markdown supported)",
                }
            ),
            "reference": forms.URLInput(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                    "placeholder": "https://example.com/recipe",
                }
            ),
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "quantity"]
        widgets = {
            "ingredient": forms.Select(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                }
            ),
            "quantity": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                    "placeholder": "e.g., 400g, 2 tbsp",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        ingredient = cleaned_data.get("ingredient")
        quantity = cleaned_data.get("quantity")

        # If both are empty, the form should be skipped (handled by formset)
        # If only one is filled, raise an error
        if ingredient and not quantity:
            raise forms.ValidationError("Please enter a quantity for this ingredient.")
        if quantity and not ingredient:
            raise forms.ValidationError("Please select an ingredient.")

        return cleaned_data


RecipeIngredientFormSet = forms.inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=1,
    max_num=50,
    can_delete=True,
)


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ["name", "category", "is_pantry_staple", "default_unit"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                    "placeholder": "Ingredient name",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                }
            ),
            "default_unit": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                    "placeholder": "e.g., g, ml, tin",
                }
            ),
            "is_pantry_staple": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-indigo-600 focus:ring-indigo-500",
                }
            ),
        }


class WeekPlanForm(forms.ModelForm):
    class Meta:
        model = WeekPlan
        fields = ["start_date"]
        widgets = {
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default to next Monday
        if not self.instance.pk:
            today = date.today()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7  # If today is Monday, go to next Monday
            self.initial["start_date"] = today + timedelta(days=days_until_monday)


class ManualShoppingItemForm(forms.Form):
    """Form for adding manual items to a shopping list."""

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                "placeholder": "Item name",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=ShoppingCategory.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
            }
        ),
    )
    quantities = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                "placeholder": "e.g., 2 packs",
            }
        ),
    )


class ShoppingListForm(forms.ModelForm):
    """Form for creating a new shopping list."""

    class Meta:
        model = ShoppingList
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2",
                    "placeholder": "List name",
                }
            )
        }
