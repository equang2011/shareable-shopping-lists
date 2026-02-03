# Shareable Shopping Lists - MVP v0.1

Share simple shopping lists with friends. Prevent duplicate items (case-insensitive) and invite collaborators to shared lists, with item status tracking ('need'/'bought').

## Stack
- Python 3.x • Django • Django REST Framework
- SQLite (local dev); Postgres-compatible for production
- Deployment-ready (Render)

## Quickstart
```bash
python -m venv .venv & source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # set DB URL, SECRET_KEY, DEBUG
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

## Features
- Create shopping lists
- Invite collaborators to shared lists
- Prevent duplicate items (case-insensitive check)
- Mark items as "need", "bought" or "will buy"
- Permission rules: only author or collaborators can add items

## API
JSON endpoints available under `/api/` for lists and items. 
Example: `GET /api/shoppinglists/` returns the authenticated user's lists.

## Roadmap
- Public read-only links
- Filtering & pagination
- Deployment polish