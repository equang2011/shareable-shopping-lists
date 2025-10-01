# lists/urls.py
from django.urls import path
from . import views

app_name = "lists"  # <-- this creates namespace

urlpatterns = [
    path("", views.index, name="shoppinglist-index"),  # /lists/
    path("new/", views.create_list, name="create-list"),  # /lists/new/
    path("<int:list_id>/", views.item_view, name="shoppinglist-detail"),  # /lists/42/
    path("<int:list_id>/add/", views.add_item, name="add-item"),  # /lists/42/add/
    path(
        "items/<int:item_id>/edit/", views.edit_item, name="edit-item"
    ),  # /lists/items/123/edit/
    path("modern/", views.shoppinglist_modern, name="shoppinglist-modern"),
]
