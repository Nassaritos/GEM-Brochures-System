# GEM Brochure Tracker

A small Django app for tracking brochure and flyer orders, deliveries, stock, and issues.

## What it covers
- Products
- Orders with PR and PO numbers
- Partial batch deliveries
- Storekeeper issues
- Auto stock balance and product status

## Local run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Render deploy
This repo already includes:
- `build.sh`
- `render.yaml`
- Postgres connection via `DATABASE_URL`

### Deploy steps
1. Create a GitHub repo and push this project.
2. In Render, choose **New +** > **Blueprint**.
3. Connect the GitHub repo.
4. Render reads `render.yaml` and creates:
   - one Python web service
   - one Postgres database
5. After deploy finishes, open the app.
6. Create an admin user from Render Shell:
   ```bash
   python manage.py createsuperuser
   ```
7. Open `/admin/` and start adding products, orders, deliveries, and issues.

## Important free-tier note
Render free web services spin down after inactivity, and free Postgres databases expire after 30 days. Upgrade before real internal production use.


## Role setup
Run this after migrations to create the two groups:
```bash
python manage.py seed_roles
```

Then in Django admin:
- assign marketing users to **Marketing Team**
- assign store users to **Storekeeper**
