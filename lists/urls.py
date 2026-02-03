# lists/urls.py
from django.urls import path
from . import views

app_name = "lists"  # <-- this creates namespace

urlpatterns = [
    path("", views.index, name="shoppinglist-index"),  # /lists/
    path("new/", views.create_list, name="create-list"),  # /lists/new/
    path("<int:list_id>/", views.list_detail, name="shoppinglist-detail"),  # /lists/42/
    path("<int:list_id>/add/", views.add_item, name="add-item"),  # /lists/42/add/
    path(
        "items/<int:item_id>/edit/", views.edit_item, name="edit-item"
    ),  # /lists/items/123/edit/
    path("modern/", views.shoppinglist_modern, name="shoppinglist-modern"),
    path(
        "invites/", views.invites_dashboard, name="invites-dashboard"
    ),  # /lists/invites/
    path("search_users/", views.search_users, name="search-users"),
    path("<int:list_id>/delete/", views.delete_list, name="delete-list"),
    path("items/<int:item_id>/delete/", views.delete_item, name="delete-item"),
    path("<int:list_id>/invite/", views.send_invite, name="send-invite"),
    path("invites/<int:invite_id>/accept/", views.accept_invite, name="accept-invite"),
    path("invites/<int:invite_id>/cancel/", views.cancel_invite, name="cancel-invite"),
    path(
        "invites/<int:invite_id>/decline/", views.decline_invite, name="decline-invite"
    ),
    path("invites/<int:invite_id>/", views.invite_detail, name="invite-detail"),
    path("select-invitee/", views.select_invitee, name="select-invitee"),
]
