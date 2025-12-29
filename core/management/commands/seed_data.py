from django.core.management.base import BaseCommand

from core.models import MealType, ShoppingCategory, Store, StoreCategoryOrder


class Command(BaseCommand):
    help = "Seed initial data for meal types, shopping categories, and stores"

    def handle(self, *args, **options):
        self.stdout.write("Seeding initial data...")

        # Create meal types
        meal_types = [
            ("Rice", "#10B981"),  # Green
            ("Pasta", "#F59E0B"),  # Amber
            ("Potato", "#8B5CF6"),  # Purple
        ]
        for name, colour in meal_types:
            obj, created = MealType.objects.get_or_create(
                name=name, defaults={"colour": colour}
            )
            if created:
                self.stdout.write(f"  Created meal type: {name}")

        # Create shopping categories
        categories = [
            "Fruit & Veg",
            "Dairy",
            "Tinned",
            "Cereals",
            "Bread",
            "Baking",
            "Household",
            "Frozen",
            "Meat",
            "Condiments",
        ]
        category_objects = {}
        for name in categories:
            obj, created = ShoppingCategory.objects.get_or_create(name=name)
            category_objects[name] = obj
            if created:
                self.stdout.write(f"  Created shopping category: {name}")

        # Create stores
        stores_data = [
            ("Tesco", True),
            ("Morrisons", False),
        ]
        for name, is_default in stores_data:
            store, created = Store.objects.get_or_create(
                name=name, defaults={"is_default": is_default}
            )
            if created:
                self.stdout.write(f"  Created store: {name}")

        # Create store category orders for Tesco
        tesco = Store.objects.get(name="Tesco")
        tesco_order = [
            "Fruit & Veg",
            "Dairy",
            "Meat",
            "Tinned",
            "Cereals",
            "Bread",
            "Baking",
            "Condiments",
            "Household",
            "Frozen",
        ]
        for i, cat_name in enumerate(tesco_order, start=1):
            if cat_name in category_objects:
                StoreCategoryOrder.objects.get_or_create(
                    store=tesco,
                    category=category_objects[cat_name],
                    defaults={"sort_order": i},
                )

        # Create store category orders for Morrisons (different order)
        morrisons = Store.objects.get(name="Morrisons")
        morrisons_order = [
            "Fruit & Veg",
            "Bread",
            "Dairy",
            "Meat",
            "Tinned",
            "Cereals",
            "Baking",
            "Condiments",
            "Frozen",
            "Household",
        ]
        for i, cat_name in enumerate(morrisons_order, start=1):
            if cat_name in category_objects:
                StoreCategoryOrder.objects.get_or_create(
                    store=morrisons,
                    category=category_objects[cat_name],
                    defaults={"sort_order": i},
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded initial data!"))
