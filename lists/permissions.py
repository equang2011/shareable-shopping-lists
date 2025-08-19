from django.db.models import Q
from .models import ShoppingList


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
    return getattr(user, "is_authenticated", False) and (
        shoppinglist.author_id == user.id
        or shoppinglist.shared_with.filter(id=user.id).exists()
    )
