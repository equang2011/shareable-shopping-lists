"""
test_accept_invite_only_invitee_can_accept

test_accept_invite_fails_if_not_pending

test_accept_invite_fails_if_list_archived

test_accept_invite_adds_actor_to_shared_with

(Optional) test_accept_invite_twice_is_idempotent_or_raises
"""

import pytest
from django.utils import timezone
from lists.models import ShoppingList, ListInvite
from lists.services import accept_invite
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_accept_invite_adds_user_to_shared_with():
    owner = User.objects.create_user(username="owner", password="123")
    invitee = User.objects.create_user(username="invitee", password="456")

    sl = ShoppingList.objects.create(author=owner, name="Groceries")
    invite = ListInvite.objects.create(
        sent_from=owner, sent_to=invitee, shopping_list=sl, status="pending"
    )

    result = accept_invite(invite, invitee)

    assert invitee in result.shopping_list.shared_with.all()
    assert result.status == "accepted"
    assert result.accepted_at is not None
