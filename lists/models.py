from django.db import models
from django.conf import settings
from django.urls import reverse


# Create your models here.
class ShoppingList(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="shared_lists", blank=True
    )
    is_archived = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("lists:shoppinglist-detail", kwargs={"list_id": self.id})


class Item(models.Model):
    STATUS_CHOICES = [("need", "Need"), ("will_buy", "Will Buy"), ("bought", "Bought")]
    shopping_list = models.ForeignKey(
        ShoppingList, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="need")
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="items_added",
    )

    def __str__(self):
        return self.name


class ListInvite(models.Model):
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invites_sent"
    )
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invites_received",
    )
    shopping_list = models.ForeignKey(
        ShoppingList, on_delete=models.CASCADE, related_name="invites"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("cancelled", "Cancelled"),
        ("declined", "Declined"),
    ]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")

    class Meta:
        constraints = [
            #  prevent user inviting themselves
            models.CheckConstraint(
                check=~models.Q(inviter=models.F("invitee")), name="no_self_invites"
            ),
            #  only one pending invite per (list, user)
            models.UniqueConstraint(
                fields=["shopping_list", "invitee"],
                condition=models.Q(status="pending"),
                name="unique_pending_invite",
            ),
        ]
