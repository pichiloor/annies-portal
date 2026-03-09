# Annie's Portal

A dashboard for Annie, owner of a liquor distribution company in the US. It shows profit and margin metrics by product and vendor, with filters by year, month, city, and store.

---

## Requirements

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- A `.env` file in the root folder (see below)
- CSV source files in the `data/` folder (not included in the repo)

---

## Setup

### 1. Create the `.env` file

Create a file called `.env` in the root of the project with this content:

```
POSTGRES_DB=annies_db
POSTGRES_USER=annies_user
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=db
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
```

### 2. Start the project

```bash
docker compose up -d
```

This starts two containers: the Django web app and the PostgreSQL database.

### 3. Run database migrations

```bash
docker compose exec web python manage.py migrate
```

### 4. Load the data

Place the CSV files in the `data/` folder, then run these commands in this exact order:

```bash
docker compose exec web python manage.py load_stores
docker compose exec web python manage.py load_products
docker compose exec web python manage.py load_sales
docker compose exec web python manage.py load_purchases
```

Each command reads a CSV file from the `data/` folder and saves it to the database.

### 5. Build the summary tables

After loading the data, build the pre-aggregated summary tables used by the dashboard:

```bash
docker compose exec web python manage.py build_summaries
```

This collapses millions of transaction rows into summary tables grouped by store, product, vendor, year and month. It makes the dashboard significantly faster (from ~17 seconds to ~500ms per query).

Run this command again whenever new data is loaded.

### 6. Create a superuser (admin access)

```bash
docker compose exec web python manage.py createsuperuser
```

### 7. Create Annie's user

```bash
docker compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.create_user(username='annie', password='yourpassword')
"
```

### 8. Open the app

Go to [http://localhost:8000](http://localhost:8000) and log in with Annie's credentials.

Admin panel is at [http://localhost:8000/admin](http://localhost:8000/admin).

---

## Scheduled refresh (optional)

To automatically rebuild the summary tables every night, add this line to your crontab (`crontab -e`):

```
0 2 * * * cd /path/to/annies-portal && docker compose exec -T web python manage.py build_summaries >> /tmp/build_summaries.log 2>&1
```

This runs at 2:00am every day. Logs are written to `/tmp/build_summaries.log`.

---

## Project structure

```
annies-portal/
├── backend/
│   ├── config/          # Django settings and URLs
│   ├── portal/          # Main app
│   │   ├── models.py    # Database models (including summary tables)
│   │   ├── views.py     # Dashboard logic
│   │   ├── templates/   # HTML templates
│   │   └── management/commands/  # Data loading and summary commands
│   └── requirements.txt
├── data/                # CSV source files (not in git)
├── docker-compose.yml
└── .env                 # Your environment variables (not in git)
```

---

## Models

The app has 5 core models and 2 summary models:

**Vendor** — a supplier company.
- `vendor_number` — ID from the original data
- `vendor_name` — company name

**Product** — a specific liquor product.
- `brand` — numeric brand ID from the original data
- `description` — product name
- `size` — bottle size (e.g. 750mL)
- `purchase_price` — price Annie pays per unit
- `vendor` — which vendor sells this product

**Store** — one of Annie's store locations.
- `store_id` — ID from the original data
- `city` — store name/location (e.g. HARDERSFIELD)

**Sale** — a sale made at a store.
- `store` — which store made the sale
- `product` — which product was sold
- `quantity` — how many units were sold
- `revenue` — total dollars received (quantity × price)
- `price` — unit sale price
- `sales_date` — date of the sale

**Purchase** — a purchase order from a vendor.
- `store` — which store received the order
- `product` — which product was ordered
- `vendor` — which vendor supplied it
- `quantity` — how many units were ordered
- `cost` — total dollars paid (quantity × purchase price)
- `purchase_price` — unit purchase price
- `po_date` — date of the purchase order

**SaleSummary / PurchaseSummary** — pre-aggregated summary tables used by the dashboard. Grouped by store, product, vendor, year and month. Rebuilt by running `build_summaries`.

---

## How profit and margin are calculated

```
profit = revenue - cost
margin = (profit / revenue) × 100
```

This is the standard **gross margin** formula. It tells Annie how much of every dollar she earns is actual profit.
