from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="shoppinglist-index"),
    path("<int:list_id>/", views.item_view, name="shoppinglist-detail"),
    path("new/", views.create_list, name="create-list"),  # what does this do
    path("<int:list_id>/add/", views.add_item, name="add-item"),
]
