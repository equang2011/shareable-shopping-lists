5/31:

🗓️ 8-Week Plan (Assumes ~6–12 hrs/week)
Week	Goal
1	Finalize core Django functionality (CRUD lists/items, auth, views)
2	Add filtering, duplicate prevention, item status toggling
3	Learn Django REST Framework basics: serializers, viewsets
4	Convert shopping list views to API endpoints
5	Build a separate React app that fetches lists from /api/lists/
6	Add basic React form to create lists via POST
7	Add login + logout (either in React or just show protected behavior)
8	Polish, deploy frontend (optional), add README + demo GIF

✅ Step-by-Step Path to “REST Level” with Django
📦 1. Solidify Django Core (You're already 70%+ there)
Make sure you're comfortable with:

✅ Models

✅ Views

✅ Templates

✅ URL routing

✅ User auth (login_required, request.user)

✅ Pushing to GitHub, deploying (you’ve done all of this!)

Goal: Understand how Django serves HTML pages and handles user state.

2. Understand What REST Is

🛠️ 3. Learn Django REST Framework (DRF) Core Tools
Concept	What to Learn
✅ Serializers	Convert model instances ↔ JSON
✅ API Views	Class-based views (like APIView, ModelViewSet)
✅ Routers	DRF's auto-URL generator for viewsets
✅ Permissions	Enforce access rules (IsAuthenticated, etc.)
✅ Browsable API UI	DRF's built-in dev tool for exploring endpoints 🔥

5/25:

🧱 When you’re ready to improve it...
Here’s a natural checklist of incremental improvements you can tackle next:

Feature	Skill it teaches
✅ Prevent adding duplicate items	Validation logic in forms.py
🧠 Edit an item’s name/status	More advanced form prepopulation
🎨 Add some CSS	Learn basic static file setup
🗑️ Delete items	Build your first POST-only action
✅ Mark status as "Bought" via toggle	Learn how to update DB state from a button
🔐 Require login to create lists/items	Learn Django auth decorators
🔍 Filter items by status (Need vs Bought)	Learn query filters and GET params

maybe add a logout to Your Shopping Lists

5/24:
next items
    - Display items in a given shopping list
    - add a form to create an item in a list
    - filter lists by user



FUTURE:
- add slugify url logic