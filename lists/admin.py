from django.contrib import admin
from .models import ShoppingList, Item, User

# Register your models here.
admin.site.register(ShoppingList)
admin.site.register(Item)
