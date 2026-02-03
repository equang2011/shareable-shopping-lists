# lists/serializers.py
from rest_framework import serializers
from .models import ShoppingList, Item, ListInvite


class ItemSerializer(serializers.ModelSerializer):
    shopping_list = serializers.PrimaryKeyRelatedField(
        queryset=ShoppingList.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Item
        fields = ["id", "name", "status", "added_by"]
        read_only_fields = ["id", "added_by"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["added_by"] = request.user
        return super().create(validated_data)


class ShoppingListSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = ShoppingList
        fields = [
            "id",
            "name",
            "author",
            "created_at",
            "items",
        ]
        read_only_fields = ["author", "created_at", "shared_with"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["author"] = request.user
        return super().create(validated_data)


class InviteSerializer(serializers.ModelSerializer):
    """
    1. create invite
    """

    class Meta:
        model = ListInvite
        fields = [
            "shopping_list",
            "invitee",
        ]
        read_only_fields = ["id", "inviter", "created_at", "status", "accepted_at"]

    invitee_username = serializers.ReadOnlyField(source="invitee.username")
    inviter_username = serializers.ReadOnlyField(source="inviter.username")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["inviter"] = request.user
        return super().create(validated_data)
