# Shareable Shopping Lists - MVP v0.1

Share simple shopping lists with friends. Prevent duplicate items (case-insensitive), invite collaborators via token links, and mark items 'need'/'bought'.

## Stack
- Python 3.x • Django • Django REST Framework
- Postgres (recommended for case-insensitive unique constraint)
- Deployed on Render

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
- Invite collaborators via shareable token links
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