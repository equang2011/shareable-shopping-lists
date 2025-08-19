# Shopping List App — Decisions Log

*A compact, living log of choices. Each section ends with an **Interview hook** you can say out loud. Use the checkboxes to track completion.*

---

## 0) TL;DR (Current Direction)

* [x] **Salvage** the current project (no restart) ✅
* [x] Keep models; switch to `AUTH_USER_MODEL`; add `blank=True` on `shared_with` ✅
* [ ] Add centralized object-level authorization (helper + DRF permission)
* [ ] Ship minimal DRF endpoints under `/api/` with safe `get_queryset()`
* [ ] Add 4 auth tests (owner/shared/stranger/share-action)

**Interview hook:** “I audited for IDOR and added object-level authorization; serializers and viewsets mirror UI rules.”

---

## 1) Domain Model

**Decision:**

* `ShoppingList(author, name, created_at, shared_with<M2M>)`
* `Item(shopping_list→ShoppingList, name, status∈{need, will_buy, bought})`
* Use `related_name="items"` on `Item.shopping_list`.
* Use `settings.AUTH_USER_MODEL` for `author` & `shared_with`.
* `shared_with`: `blank=True` to simplify forms.

**Rationale:** Minimal, readable schema; maps 1\:many (list→items) and many\:many (list↔users) cleanly.

**Tiny snippet (≤5 lines):**

```py
from django.conf import settings

author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_lists', blank=True)
```

**Interview hook:** “I kept the schema intentionally small and user-swappable via `AUTH_USER_MODEL` for portability.”

---

## 2) S





prompt:
8/18

Context to load:

Project: shoppinglist_project (server-rendered UI), we’re layering DRF into THIS project; shoppinglist_api is archived.

Current state:

Working pages: index → detail → add/edit item.

Object-level auth in views (author or shared_with).

lists/urls.py namespaced with app_name="lists".

Project urls.py mounts lists/ and auth routes; root redirect OK.

Models: ShoppingList(author, name, created_at, is_archived, shared_with[blank=True]); Item(shopping_list, name, status).

Migrations applied; basic templates render.

Goal for this session: Add DRF endpoints under /api/ with flat routes (no nested routers). Keep code minimal; reuse existing authorization rules.

How I want help:

Don’t spoon-feed big blocks. Give me 1–5 line fixes and short implementation checklists.

If a change is >5 lines, outline a brief plan and the exact files to touch.

Tie guidance to interview talking points (object-level auth, DRF viewsets, queryset design, n+1 avoidance).

Tasks to guide me through now:

Create lists/serializers.py for ShoppingList and Item (fields consistent with my models; author read-only; nested items read-only).

Create lists/api_permissions.py with IsOwnerOrShared (object-level: list owner or in shared_with; for items, check item.shopping_list).

Create lists/api.py with ShoppingListViewSet and ItemViewSet:

get_queryset() mirrors my visibility rule;

perform_create() sets author and validates shopping_list access before saving an item.

Wire DRF router in project urls.py at /api/ and verify /api/ → /api/shoppinglists/ works.

Write one pytest for each: owner OK, shared OK, stranger 403.

Add a notes.md entry summarizing the API surface + auth story.

Files I’ll paste if you ask: current models.py, urls.py, any serializers I draft, and failing test output.