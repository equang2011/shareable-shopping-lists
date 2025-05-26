from django import forms
from .models import ShoppingList, Item


class CreateListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ["name"]


class AddItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "status"]
