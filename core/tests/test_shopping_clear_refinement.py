from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import (
    Store,
    ShoppingList,
    ShoppingListItem,
)

User = get_user_model()

class ShoppingClearRefinementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.store = Store.objects.create(name="SuperMart")
        self.shopping_list = ShoppingList.objects.create(
            name="My List", created_by=self.user, store=self.store
        )
        self.checked_item = ShoppingListItem.objects.create(
            shopping_list=self.shopping_list, name="Checked Item", is_checked=True
        )
        self.unchecked_item = ShoppingListItem.objects.create(
            shopping_list=self.shopping_list, name="Unchecked Item", is_checked=False
        )

    def test_clear_checked_only_removes_checked_items(self):
        """Verify that a request to the clear endpoint only removes items with is_checked=True."""
        response = self.client.post(
            reverse("shopping_clear", args=[self.shopping_list.pk]),
            {"type": "checked"}
        )
        self.assertEqual(response.status_code, 302)
        
        # Checked item should be gone
        self.assertFalse(ShoppingListItem.objects.filter(pk=self.checked_item.pk).exists())
        # Unchecked item should still exist
        self.assertTrue(ShoppingListItem.objects.filter(pk=self.unchecked_item.pk).exists())

    def test_clear_all_is_no_longer_supported(self):
        """
        Verify that even with type='all', only checked items are removed,
        or 'all' is ignored/treated as 'checked'.
        """
        response = self.client.post(
            reverse("shopping_clear", args=[self.shopping_list.pk]),
            {"type": "all"}
        )
        # If we refactor the view to ignore 'type=all' and only do 'checked',
        # then the unchecked item should still exist.
        self.assertTrue(ShoppingListItem.objects.filter(pk=self.unchecked_item.pk).exists(), 
                        "Unchecked item should remain even if type='all' is sent")
        self.assertFalse(ShoppingListItem.objects.filter(pk=self.checked_item.pk).exists(),
                         "Checked item should be removed")

    def test_clear_checked_htmx(self):
        """Verify that HTMX requests return only the items partial, not a full redirect."""
        response = self.client.post(
            reverse("shopping_clear", args=[self.shopping_list.pk]),
            {"type": "checked"},
            HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "components/shopping_items_only.html")
        self.assertNotEqual(response.status_code, 302)

    def test_clear_no_checked_items(self):
        """Verify that it works even if there are no checked items."""
        # Remove the checked item from setUp
        self.checked_item.delete()
        
        response = self.client.post(
            reverse("shopping_clear", args=[self.shopping_list.pk]),
            {"type": "checked"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ShoppingListItem.objects.filter(pk=self.unchecked_item.pk).exists())
