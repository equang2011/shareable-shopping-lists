"""
Functions: send_invite(list, inviter, invitee), accept_invite(invite, actor), decline_invite(invite, actor), cancel_invite(invite, actor).

Benefits:
- reusable logic
- testable in isolation
- cleaner seperation from models/views

What do we need services for?

- Send invite
- accept invite
- decline invite


"""

from django.db import transaction, IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from .models import ListInvite, Item
from django.db.models import Q


# Optional: define domain-specific exceptions in lists/exceptions.py and import them here
# class DuplicatePendingInvite(Exception): ...
# class InvalidInviteTransition(Exception): ...


def send_invite(shopping_list, inviter, invitee):
    """
    Send a pending invite for a shopping list.

    BusinessRule:
    The owner of a shopping list can send a one-time invite to another user to collaborate on the list, provided the list is active
    and there is no existing pending invite.

    Preconditions:
    - inviter is the shopping_list.author
    - shopping_list is not archived
    - invitee is a different user and not already in shared_with
    - no pending invite already exists for (shopping_list, invitee)

    Side effects:
    - Inserts a new ListInvite(status='pending') into the database

    Returns:
    - The created ListInvite instance

    Raises:
    - PermissionDenied: if inviter is not the list owner
    - ValidationError: if list is archived, self-invite attempted,
                    invitee already a collaborator, or a pending invite exists
    """
    if inviter != shopping_list.author:
        raise PermissionDenied("Only the owner can invite")
    if shopping_list.is_archived:
        raise ValidationError("This Shopping List is not active.")
    if invitee == inviter:  # self-invite check
        raise ValidationError("Cannot invite yourself or an existing collaborator")
    if shopping_list.shared_with.filter(id=invitee.id).exists():
        raise ValidationError("This user is already invited to this list.")
    if shopping_list.shared_with.count() >= 49:
        raise ValidationError(
            "This shopping list is full. You cannot send this invite."
        )

    if ListInvite.objects.filter(
        shopping_list=shopping_list, invitee=invitee, status="pending"
    ).exists():
        raise ValidationError("Pending invite already exists for this user")

    # create
    invite = ListInvite.objects.create(
        shopping_list=shopping_list,
        inviter=inviter,
        invitee=invitee,
        status="pending",
        created_at=timezone.now(),
    )
    return invite


def accept_invite(invite, actor):
    """
    Accept a pending invite.

    Preconditions:
    - invite.status == 'pending'
    - actor == invite.invitee
    - invite.shopping_list.is_archived is False

    Side effects (atomic):
    - Sets invite.status='accepted', invite.accepted_at=now
    - Adds actor to invite.shopping_list.shared_with
    - Saves invite

    Raises:
    - PermissionDenied if actor != invitee
    - InvalidInviteTransition if status != 'pending'
    - ValidationError if list is archived or actor already a collaborator (edge)
    """
    if actor != invite.invitee:
        raise PermissionDenied("You cannot accept this invite.")
    if invite.status != "pending":
        raise ValidationError("This invite cannot be accepted.")

    sl = invite.shopping_list

    if sl.is_archived:
        raise ValidationError(
            "This invite cannot be accepted because the shopping list is archived."
        )
    if sl.shared_with.filter(id=actor.id).exists():
        raise ValidationError("You have already been added to this list.")
    if sl.shared_with.count() >= 49:
        raise ValidationError(
            "This shopping list is full. You cannot accept this invite."
        )

    with transaction.atomic():
        sl.shared_with.add(actor)

        invite.status = "accepted"
        invite.accepted_at = timezone.now()
        invite.save(update_fields=["status", "accepted_at"])

    return invite


def decline_invite(invite, actor):
    """
    Decline a pending invite.

    Preconditions:
    - invite.status == 'pending'
    - actor == invite.invitee

    Side effects:
    - Sets invite.status = 'declined'
    - Does not modify shared_with

    Raises:
    - PermissionDenied if actor != invite.invitee
    - ValidationError if invite is not pending
    """
    if actor != invite.invitee:
        raise PermissionDenied("You cannot respond to this invite.")
    if invite.status != "pending":
        raise ValidationError("This invite cannot be declined.")

    with transaction.atomic():
        invite.status = "declined"
        invite.save(update_fields=["status"])

    return invite


def cancel_invite(invite, actor):
    """
    Cancel a pending invite (owner action).

    Preconditions:
    - invite.status == 'pending'
    - actor == invite.shopping_list.author

    Side effects:
    - Sets invite.status='canceled'

    Raises:
    - PermissionDenied if actor is not the list author
    - InvalidInviteTransition if status != 'pending'
    """
    if actor != invite.shopping_list.author:
        raise PermissionDenied("You cannot cancel this invite.")
    if invite.status != "pending":
        raise ValidationError("This invite cannot be cancelled.")

    with transaction.atomic():
        invite.status = "canceled"
        invite.save(update_fields=["status"])

    return invite


# ----- List services ----------
def archive_list(shopping_list, actor):
    """
    BusinessLogic: allows List Owner to archive list
    """
    if actor != shopping_list.author:
        raise PermissionDenied("Only the owner of this list can archive it.")
    if shopping_list.is_archived:
        raise ValidationError("This Shopping List is not active.")

    with transaction.atomic():
        shopping_list.is_archived = True
        shopping_list.save(update_fields=["is_archived"])

    return shopping_list


# ------ item services ------


def add_item(shopping_list, actor, name):
    """
    allows actor to add item to shopping list
    - list must be active
    - item cannot already be on list
    """
    # Permission check
    if (
        actor != shopping_list.author
        and not shopping_list.shared_with.filter(id=actor.id).exists()
    ):
        raise PermissionDenied("You are not allowed to add items to this list.")
    # List must be active
    if shopping_list.is_archived:
        raise ValidationError("This Shopping List is not active.")
    # No duplicates
    if shopping_list.items.filter(name__iexact=name).exists():
        raise ValidationError("This item has already been added to the Shopping List.")

    # max item count
    if shopping_list.items.count() > 99:
        raise ValidationError("List cannot have more than 99 items.")
    with transaction.atomic():
        new_item = Item.objects.create(
            shopping_list=shopping_list,
            name=name,
            status="need",
            added_by=actor,
        )

    return new_item


def update_item(item, actor, **changes):
    """ """
    if (
        actor != item.shopping_list.author
        and not item.shopping_list.shared_with.filter(id=actor.id).exists()
    ):
        raise PermissionDenied("You cannot update this item.")

    changed_fields = []
    if "status" in changes:
        item.status = changes["status"]
        changed_fields.append("status")
    if "name" in changes:
        if actor != item.added_by:
            raise PermissionDenied("Only the author can rename this item.")
        item.name = changes["name"]
        changed_fields.append("name")
    if not changed_fields:
        return item
    with transaction.atomic():
        item.save(update_fields=changed_fields)
    return item


def delete_item(actor, item):
    """
    Delete an item from a shopping list.
    Preconditions:
    - actor == item.added_by or ==list.author
    - list not archived
    """
    if actor != item.added_by and actor != item.shopping_list.author:
        raise PermissionDenied("You cannot delete this item.")
    if item.shopping_list.is_archived:
        raise ValidationError("Cannot delete items from an archived list.")
    item.delete()
    return


def get_item_user_can_edit(user, item_id):
    """Return item user is allowed to edit or return 404"""
    return get_object_or_404(
        Item.objects.select_related("shopping_list").filter(
            Q(shopping_list__author=user) | Q(shopping_list__shared_with=user)
        ),
        id=item_id,
    )


"""

"""
