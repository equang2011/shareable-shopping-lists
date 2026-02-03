# lists/api.py
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import ShoppingList, Item, ListInvite
from .serializers import ShoppingListSerializer, ItemSerializer, InviteSerializer
from .permissions import get_lists_user_can_view, IsOwnerOrShared
from .services import archive_list, update_item, send_invite


class ShoppingListViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Shopping Lists:

    Responsibilities:
    - only show lists the user can access
    - auto-set the author on create
    - allow CRUD operations via DRF Router
    - add custom actions like archive
    """

    serializer_class = ShoppingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_lists_user_can_view(self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        """Custom action: archive this shopping list (POST /shoppinglists/{id}/archive/)"""
        sl = self.get_object()
        archive_list(sl, request.user)
        return Response(ShoppingListSerializer(sl).data)


class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for items
    - Expose CRUD endpoints for items /api/items
    - enforce permissions
    - hook into service layer
    """

    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        visible = get_lists_user_can_view(self.request.user)
        return Item.objects.select_related("shopping_list").filter(
            shopping_list__in=visible
        )

    def perform_create(self, serializer):
        sl = serializer.validated_data["shopping_list"]

        if not get_lists_user_can_view(self.request.user).filter(pk=sl.pk).exists():
            raise PermissionDenied("Not allowed on this list")
        serializer.save()

    def perform_update(self, serializer):
        item = self.get_object()
        user = self.request.user
        validated = serializer.validated_data
        update_item(item, user, **validated)


class InviteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for list invites
    - Expose CRUD endpoints for invites
    - enforce permissions
    - hook into service layer
    """

    serializer_class = InviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        list_invites = ListInvite.objects.filter(
            Q(invitee=self.request.user) | Q(inviter=self.request.user)
        )
        return list_invites

    def perform_create(self, serializer):
        request = self.request
        list_id = serializer.validated_data["shopping_list"].id
        invitee = serializer.validated_data["invitee"]

        sl = ShoppingList.objects.get(pk=list_id)

        invite = send_invite(
            shopping_list=sl,
            inviter=request.user,
            invitee=invitee,
        )

        serializer.instance = invite

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)

        if request.headers.get("HX-Request"):
            invite_obj = serializer.instance
            return render(
                request,
                "lists/_invite_success.html",
                {"username": invite_obj.invitee.username},
            )

        return Response(serializer.data, status=201, headers=headers)
