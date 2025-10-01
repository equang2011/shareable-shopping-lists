from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from .models import ShoppingList, Item, ListInvite
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .permissions import get_lists_user_can_view
from .forms import CreateListForm, AddItemForm, EditItemForm
from .serializers import ShoppingListSerializer, ItemSerializer, InviteSerializer
from .services import archive_list, update_item
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.http import HttpResponse


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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("lists:shoppinglist-index")  # send them to lists
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def index(request):
    lists = get_lists_user_can_view(request.user)
    print("DEBUG lists:", lists)
    return render(request, "lists/index.html", {"lists": lists})


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
def item_view(request, list_id):
    shoppinglist = get_object_or_404(get_lists_user_can_view(request.user), id=list_id)

    items = shoppinglist.items.all()
    return render(
        request, "lists/item_view.html", {"shoppinglist": shoppinglist, "items": items}
    )


@login_required
def add_item(request, list_id):
    shoppinglist = get_object_or_404(get_lists_user_can_view(request.user), id=list_id)

    items = shoppinglist.items.all()

    if request.method == "POST":
        form = AddItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.shopping_list = shoppinglist
            item.save()
            return redirect(shoppinglist)
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
