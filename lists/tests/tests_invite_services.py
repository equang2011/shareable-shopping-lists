from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied

from lists.models import ShoppingList, ListInvite, Item
from lists import services

# Create your tests here.
# critical tests:
# owner can send invite
# non owner cannot send invite
"""
critical tests
INVITES:
- owner can send invite
- non owner cannot send
- cannot invite to archived list
- cannot send duplicate pending invite
- cannot invite yourself
High Priority (Test These):
1. Service Layer Functions ← Your business logic lives here!
Example: send_invite() service

✅ Test: Owner can send invite
✅ Test: Non-owner cannot send invite (raises PermissionDenied)
✅ Test: Cannot invite to archived list (raises ValidationError)
✅ Test: Cannot send duplicate pending invite (raises ValidationError)
✅ Test: Cannot invite yourself (raises ValidationError)

Why test services? Because if send_invite() is broken, BOTH your views AND your API are broken. One test protects multiple entry points.
2. Permission Logic
Example: Who can delete items?

✅ Test: Item creator can delete their item
✅ Test: List owner can delete anyone's item
✅ Test: Random user cannot delete (raises PermissionDenied)

3. State Transitions
Example: Invite status changes

✅ Test: Pending invite can be accepted
✅ Test: Accepted invite cannot be accepted again (raises ValidationError)
✅ Test: Accepting invite adds user to shared_with
"""


# --- INVITES
class SendInviteTests(TestCase):
    def setUp(self):
        """Create test data before each test"""
        self.owner = User.objects.create_user(username="alice")
        self.non_owner = User.objects.create_user(username="bob")
        self.invitee = User.objects.create_user(username="charlie")

        self.shopping_list = ShoppingList.objects.create(
            author=self.owner, name="Test List"
        )

    def test_owner_can_send_invite(self):
        invite = services.send_invite(self.shopping_list, self.owner, self.invitee)

        self.assertEqual(invite.status, "pending")
        self.assertEqual(invite.inviter, self.owner)
        self.assertEqual(invite.invitee, self.invitee)

    def test_non_owner_cannot_send_invite(self):
        pass

    def test_cannot_accept_invite_when_list_is_full(self):
        """Cannot accept invite if list already has 49 shared users"""
        for i in range(49):
            user = User.objects.create_user(username=f"user{i}")
            self.shopping_list.shared_with.add(user)
        self.assertEqual(self.shopping_list.shared_with.count(), 49)
        with self.assertRaises(ValidationError) as context:
            accept_invite(self.invite, self.invitee)

        # Check error message is helpful
        self.assertIn("full", str(context.exception))


def AcceptInviteTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="alice")
        self.invitee = User.objects.create_user(username="bob")

        self.shopping_list = ShoppingList.objects.create(
            author=self.owner, name="Groceries"
        )

        self.invite = ListInvite.objects.create(
            shopping_list=self.shopping_list,
            inviter=self.owner,
            invitee=self.invitee,
            status="pending",
        )

    def test_accept_invite_adds_user_to_shared_with(self):
        pass

    def test_cannot_accept_invite_when_list_is_full(self):
        for i in range(49):
            user = User.objects.create_user(username=f"user{i}")
            self.shopping_list.shared_with.add(user)
        self.assertEqual(self.shopping_list.shared_with.count(), 49)

        with self.assertRaises(ValidationError) as context:
            services.accept_invite(self.invite, self.invitee)
        self.assertIn("full", str(context.exception))

'''
OLD TEST
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
'''