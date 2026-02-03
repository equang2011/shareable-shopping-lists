from django import forms
from .models import ShoppingList, Item, ListInvite
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class CreateListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ["name"]


class InviteForm(forms.Form):
    email = forms.EmailField(label="Invitee email")

    def __init__(self, *args, inviter=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.inviter = inviter  # allows self-invite check

    def clean_email(self):
        email = self.cleaned_data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("User does not exist.")
        if user == self.inviter:
            raise forms.ValidationError("You cannot invite yourself.")

        return user


class AddItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "status"]

    def clean_name(self):
        name = self.cleaned_data.get("name")
        shopping_list = self.instance.shopping_list
        if shopping_list.items.filter(name__iexact=name).exists():
            raise ValidationError("This item already exists in the shopping list.")
        return name


class EditItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "status"]
