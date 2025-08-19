from django.conf import settings
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from .models import ShoppingList, Item
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .permissions import get_lists_user_can_view, user_can_access_list
from .forms import CreateListForm, AddItemForm, EditItemForm


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(
                "shoppinglist-index"
            )  # redirect to index. how does redirect work
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
            return redirect("shoppinglist-index")  # send them to lists
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def index(request):
    lists = get_lists_user_can_view(request.user)
    return render(request, "lists/index.html", {"lists": lists})


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
            return redirect("shoppinglist-index")

    else:
        form = CreateListForm()

    return render(request, "lists/create_shoppinglist.html", {"form": form})


@login_required
def item_view(request, list_id):
    shoppinglist = get_object_or_404(lists_user_can_view_qs(request.user), id=list_id)

    items = shoppinglist.items.all()
    return render(
        request, "lists/item_view.html", {"shoppinglist": shoppinglist, "items": items}
    )


@login_required
def add_item(request, list_id):
    shoppinglist = get_object_or_404(lists_user_can_view_qs(request.user), id=list_id)

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


def lists_user_can_view_qs(user, include_archived: bool = False):
    qs = (
        ShoppingList.objects.filter(Q(author=user) | Q(shared_with=user))
        .distinct()
        .select_related("author")
    )  # you’ll display author
    if not include_archived:
        qs = qs.filter(is_archived=False)
    return qs.order_by("-created_at")


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
