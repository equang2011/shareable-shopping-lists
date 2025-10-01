# lists/api.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import ShoppingList, Item
from .serializers import ShoppingListSerializer, ItemSerializer
from .permissions import get_lists_user_can_view, IsOwnerOrShared


class ShoppingListViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingListSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrShared]

    def get_queryset(self):
        return get_lists_user_can_view(self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrShared]

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
