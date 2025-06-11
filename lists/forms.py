from django import forms
from .models import ShoppingList, Item
from django.contrib.auth.forms import UserCreationForm


class CreateListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ["name"]


class AddItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "status"]


class EditItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "status"]
