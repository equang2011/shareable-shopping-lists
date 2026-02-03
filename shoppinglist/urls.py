"""
URL configuration for shoppinglists project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

from rest_framework.routers import DefaultRouter
from lists.api import ShoppingListViewSet, ItemViewSet, InviteViewSet
from lists import views as list_views

# DRF router
router = DefaultRouter()
router.register("shoppinglists", ShoppingListViewSet, basename="shoppinglist")
router.register("items", ItemViewSet, basename="item")
router.register("invites", InviteViewSet, basename ="invite")

urlpatterns = [
    # Root: redirect to your list index (cleaner than hardcoding "/login/")
    # NOTE: requires app_name="lists" in lists/urls.py and a route named "shoppinglist-index"
    path(
        "",
        RedirectView.as_view(pattern_name="lists:shoppinglist-index", permanent=False),
        name="root",
    ),
    path("admin/", admin.site.urls),
    # Mount your HTML app
    path("lists/", include("lists.urls")),
    # Auth (keep your custom views or swap to Django's later)
    path("signup/", list_views.signup_view, name="signup"),
    path("login/", list_views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    # DRF API
    path("api/", include(router.urls)),
]
