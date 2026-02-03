from django.db.models import Q
from .models import ShoppingList, ListInvite
from rest_framework import permissions


def get_lists_user_can_view(user, include_archived: bool = False):
    qs = ShoppingList.objects.filter(
        Q(author_id=user.id) | Q(shared_with=user)
    ).distinct()
    if not include_archived:
        qs = qs.filter(is_archived=False)
    # Nice for your index page (author, created_at)
    return qs.select_related("author").order_by("-created_at", "id")


def user_can_access_list(user, shoppinglist):
    # extra guard is harmless even with @login_required
    if not user.is_authenticated:
        return False
    return (
        shoppinglist.author_id == user.id
        or shoppinglist.shared_with.filter(id=user.id).exists()
    )


def get_invites_user_can_view(user, pending_only: bool = True):
    invites = ListInvite.objects.filter(Q(inviter=user) | Q(invitee=user)).distinct()
    if pending_only:
        invites = invites.filter(status="pending")
    return invites.select_related("shopping_list", "inviter", "invitee").order_by(
        "-created_at", "id"
    )


class IsOwnerOrShared(permissions.BasePermission):
    """
    Custom permission: Only allow access to list authors or shared users.
    """

    def has_object_permission(self, request, view, obj):
        sl = obj if isinstance(obj, ShoppingList) else obj.shopping_list
        if sl.is_archived and request.method not in permissions.SAFE_METHODS:
            return False
        return user_can_access_list(request.user, sl)
