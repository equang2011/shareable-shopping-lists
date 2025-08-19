from django.contrib import admin
from .models import ShoppingList, Item

# Register your models here.
admin.site.register(ShoppingList)
admin.site.register(Item)
