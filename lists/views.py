from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import ShoppingList
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .forms import CreateListForm, AddItemForm


# Create your views here.
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
    lists = ShoppingList.objects.filter(author=request.user)
    return render(request, "lists/index.html", {"lists": lists})


@login_required
def item_view(request, list_id):
    shoppinglist = get_object_or_404(ShoppingList, id=list_id)
    items = shoppinglist.items.all()
    return render(
        request, "lists/item_view.html", {"shoppinglist": shoppinglist, "items": items}
    )


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

    return render(request, "lists/create_shopppinglist.html", {"form": form})


@login_required
def add_item(request, list_id):
    shoppinglist = get_object_or_404(ShoppingList, id=list_id)
    items = shoppinglist.items.all()

    if request.method == "POST":
        form = AddItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.shopping_list = shoppinglist
            item.save()
            return redirect("shoppinglist-detail", list_id=shoppinglist.id)
    else:
        form = AddItemForm()
    return render(
        request,
        "lists/add_item.html",
        {"form": form, "shoppinglist": shoppinglist, "items": items},
    )
