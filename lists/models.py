from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class ShoppingList(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Item(models.Model):

    STATUS_CHOICES = [("need", "Need"), ("will_buy", "Will Buy"), ("bought", "Bought")]

    shopping_list = models.ForeignKey(
        ShoppingList, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="need")

    def __str__(self):
        return self.name
