from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from .models import ShoppingList, Item, ListInvite
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .permissions import get_lists_user_can_view, get_invites_user_can_view
from .forms import (
    CreateListForm,
    AddItemForm,
    EditItemForm,
    CustomUserCreationForm,
    InviteForm,
)
from .serializers import ShoppingListSerializer, ItemSerializer, InviteSerializer
from . import services
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next") or ""
            is_safe = url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            )
            default_url = reverse("lists:shoppinglist-index")
            return redirect(next_url if is_safe and next_url else default_url)
        else:
            return render(
                request,
                "registration/login.html",
                {"error": "Invalid username or password."},
            )
    return render(request, "registration/login.html")


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("lists:shoppinglist-index")  # send them to lists
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def index(request):
    lists = get_lists_user_can_view(request.user)
    print("DEBUG lists:", lists)
    return render(request, "lists/index.html", {"lists": lists})


@login_required
def delete_list(request, list_id):
    sl = get_object_or_404(ShoppingList, id=list_id)
    if sl.author != request.user:
        raise PermissionDenied("You do not have permission to delete this list.")
    if request.method == "POST":
        sl.delete()
        return redirect("lists:shoppinglist-index")
    else:
        return render(request, "lists/confirm_delete.html", {"shoppinglist": sl})


# --------------- INVITES ----------------


@login_required
def invites_dashboard(request):
    invites = get_invites_user_can_view(request.user)
    incoming = invites.filter(invitee=request.user)
    outgoing = invites.filter(inviter=request.user)
    return render(
        request,
        "invites/invites_dashboard.html",
        {"incoming": incoming, "outgoing": outgoing},
    )


@login_required
def send_invite(request, list_id):
    shopping_list = get_object_or_404(ShoppingList, id=list_id)

    if request.method == "POST":
        invitee_id = request.POST.get("invitee_id")

        if not invitee_id:
            messages.error(request, "No invitee selected.")
            return redirect("lists:send-invite", list_id=list_id)

        invitee = get_object_or_404(User, id=invitee_id)

        try:
            services.send_invite(shopping_list, request.user, invitee)
            display_name = invitee.get_full_name() or invitee.username
            messages.success(request, f"Invite sent to {display_name}.")
        except (PermissionDenied, ValidationError) as e:
            messages.error(request, str(e))

        return redirect("lists:send-invite", list_id=list_id)

    return render(
        request,
        "invites/invite_form.html",
        {"shopping_list": shopping_list},
    )


@login_required
def accept_invite(request, invite_id):
    invite = get_object_or_404(ListInvite, id=invite_id)

    try:
        services.accept_invite(invite, request.user)
        messages.success(
            request, f"You have successfully joined {invite.shopping_list.name}."
        )
    except (PermissionDenied, ValidationError) as e:
        messages.error(request, str(e))
    return redirect("lists:invites-dashboard")


@login_required
def cancel_invite(request, invite_id):
    invite = get_object_or_404(ListInvite, id=invite_id)

    try:
        services.cancel_invite(invite, request.user)
        messages.success(request, "You have successfully cancelled this invite.")
    except (PermissionDenied, ValidationError) as e:
        messages.error(request, str(e))
    return redirect("lists:invites-dashboard")


@login_required
def decline_invite(request, invite_id):
    invite = get_object_or_404(ListInvite, id=invite_id)
    try:
        services.decline_invite(invite, request.user)
        messages.success(
            request, f"You've declined the invite to {invite.shopping_list.name}."
        )
    except (PermissionDenied, ValidationError) as e:
        logger.warning(f"Invite decline error for {request.user}: {e}")
        messages.error(request, str(e))
    return redirect("lists:invites-dashboard")


@login_required
def invite_detail(request, invite_id):
    invite = get_object_or_404(ListInvite, id=invite_id)
    if request.user not in [invite.invitee, invite.inviter]:
        raise PermissionDenied

    return render(request, "invites/invite_detail.html", {"invite": invite})


@login_required
def search_users(request):
    q = request.GET.get("q", "").strip()
    results = []
    if len(q) >= 2:
        results = User.objects.filter(first_name__icontains=q)[:10]
    return render(request, "invites/_user_results.html", {"results": results})


@login_required
def select_invitee(request):
    if request.method != "POST":
        raise PermissionDenied("Invalid request.")
    user_id = request.POST.get("user_id")
    if not user_id:
        raise ValidationError("No user_id provided.")
    invitee = get_object_or_404(User, id=user_id)
    return render(request, "invites/_selected_invitee_input.html", {"invitee": invitee})


@login_required
def shoppinglist_modern(request):
    """Return a modernized version of the list (HTMX partial)."""
    lists = get_lists_user_can_view(request.user)
    return render(request, "lists/modern_list.html", {"lists": lists})


@login_required
def create_list(request):
    # if POST request, need to process data
    if request.method == "POST":
        # create form instance and populate with data from the request
        form = CreateListForm(request.POST)
        if form.is_valid():
            shoppinglist = form.save(commit=False)
            shoppinglist.author = request.user
            shoppinglist.save()
            return redirect("lists:shoppinglist-index")

    else:
        form = CreateListForm()

    return render(request, "lists/create_shoppinglist.html", {"form": form})


@login_required
def list_detail(request, list_id):
    shoppinglist = get_object_or_404(get_lists_user_can_view(request.user), id=list_id)
    items = shoppinglist.items.all()
    return render(
        request,
        "lists/list_detail.html",
        {"shoppinglist": shoppinglist, "items": items},
    )


@login_required
def add_item(request, list_id):
    shoppinglist = get_object_or_404(get_lists_user_can_view(request.user), id=list_id)

    items = shoppinglist.items.all()

    if request.method == "POST":
        form = AddItemForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            try:
                item = services.add_item(shoppinglist, request.user, name)
                messages.success(request, f"{item.name} was successfully added.")

                if request.POST.get("action") == "add_another":
                    return redirect("lists:add-item", list_id=list_id)
                return redirect(shoppinglist)
            except (PermissionDenied, ValidationError) as e:
                messages.error(request, str(e))

    else:
        form = AddItemForm()
    return render(
        request,
        "lists/add_item.html",
        {"form": form, "shoppinglist": shoppinglist, "items": items},
    )


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(
        Item.objects.select_related("shopping_list").filter(
            Q(shopping_list__author=request.user)
            | Q(shopping_list__shared_with=request.user)
        ),
        id=item_id,
    )

    if request.method == "POST":
        form = EditItemForm(request.POST, instance=item)

        if form.is_valid():
            form.save()
            return redirect(item.shopping_list)
    else:
        form = EditItemForm(instance=item)

    return render(
        request,
        "lists/edit_item.html",
        {"form": form, "item": item, "shoppinglist": item.shopping_list},
    )


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    shoppinglist = item.shopping_list

    if request.method == "POST":
        try:
            services.delete_item(request.user, item)
            messages.success(request, f"{item.name} was successfully deleted.")
        except (PermissionDenied, ValidationError) as e:
            messages.error(request, str(e))

        return redirect("lists:shoppinglist-detail", list_id=shoppinglist.id)
    return redirect(shoppinglist)
