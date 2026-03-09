# Annie's Portal

A dashboard for Annie, owner of a liquor distribution company in the US. It shows profit and margin metrics by product and vendor, with filters by year, month, city, and store.

---

## Requirements

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- A `.env` file in the root folder (see below)

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

Run these commands in this exact order:

```bash
docker compose exec web python manage.py load_stores
docker compose exec web python manage.py load_products
docker compose exec web python manage.py load_sales
docker compose exec web python manage.py load_purchases
```

Each command reads a CSV file from the `data/` folder and saves it to the database.

### 5. Create a superuser (admin access)

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Create Annie's user

```bash
docker compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.create_user(username='annie', password='yourpassword')
"
```

### 7. Open the app

Go to [http://localhost:8000](http://localhost:8000) and log in with Annie's credentials.

Admin panel is at [http://localhost:8000/admin](http://localhost:8000/admin).
 |

---

## Project structure

```
annies-portal/
├── backend/
│   ├── config/          # Django settings and URLs
│   ├── portal/          # Main app
│   │   ├── models.py    # Database models
│   │   ├── views.py     # Dashboard logic
│   │   ├── templates/   # HTML templates
│   │   └── management/commands/  # Commands to load CSV data
│   └── requirements.txt
├── data/                # CSV source files
├── docker-compose.yml
└── .env                 # Your environment variables (not in git)
```

---

## Models

The app has 5 models:

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

---

## How profit and margin are calculated

```
profit = revenue - cost
margin = (profit / revenue) × 100
```

This is the standard **gross margin** formula. It tells Annie how much of every dollar she earns is actual profit.
