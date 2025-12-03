
---

# 📦 E-Commerce Nexus API

A modular, production-ready **Django + Django REST Framework** backend powering core e-commerce functionality such as products, categories, orders, authentication, and admin operations.
Includes support for JWT authentication, idempotency handling, filtering, signals, Celery, and OpenAPI documentation.

---

## 🚀 Features

* 🔐 **JWT Authentication** using SimpleJWT
* 🏷️ **Categories & Products** (CRUD via DRF ViewSets)
* 📦 **Orders API** with audit logging
* 🧩 **Reusable catalog engine module**
* ⚙️ **Idempotent write operations**
* 🔄 **Celery integration**
* 📑 **Swagger & ReDoc API Docs**
* 🗄️ **Configurable DB** (Postgres / SQLite / DATABASE_URL auto-detect)
* 📁 **Static files ready for production**
* 🎯 Clean project layout following best practices

---

# 🗂 Project Structure

```
ecommerce_alx_project_nexus/
│── Procfile
│── runtime.txt
│── requirements.txt
│── README.md
│── ecommerce_nexus/
│     ├── accounts/
│     ├── catalog/
│     ├── ecommerce_nexus/ (project config)
│     ├── manage.py
│     ├── db.sqlite3
│     └── staticfiles/
```

---

# ⚙️ Environment Setup

## 1. Clone the project

```bash
git clone https://github.com/your-username/ecommerce_alx_project_nexus.git
cd ecommerce_alx_project_nexus
```

## 2. Create `.venv` & install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Add `.env` file in project root (`ecommerce_nexus/`)

```
SECRET_KEY=your-secret-key
DEBUG=True

# database priorities:
DATABASE_URL=
USE_POSTGRES=False

POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=
```

### Database Priority

1️⃣ If `DATABASE_URL` exists → use it
2️⃣ Else if `USE_POSTGRES=True` → use Postgres vars
3️⃣ Else → use SQLite

---

## 4. Apply migrations

```bash
python manage.py migrate
```

## 5. Create superuser

```bash
python manage.py createsuperuser
```

## 6. Run server

```bash
python manage.py runserver
```

---

# 📘 API Endpoints (Fully Accurate)

Your `urls.py` structure:

```
/api/ → catalog.urls
/api/ → accounts.urls
/api/auth/token/ → JWT Login
/api/auth/token/refresh/ → JWT Refresh
/swagger/ → API Docs
/redoc/ → Redoc Docs
```

Below is the full documentation grouped by module.

---

# 🔐 Authentication (accounts)

Base path: `/api/auth/`

| Method | Endpoint              | Description                         |
| ------ | --------------------- | ----------------------------------- |
| POST   | `/api/auth/register/` | Register a new user                 |
| POST   | `/api/auth/login/`    | Login & obtain access/refresh token |
| POST   | `/api/auth/refresh/`  | Refresh expired access token        |
| POST   | `/api/auth/logout/`   | Logout (JWT blacklist)              |

Additionally:

| Method | Endpoint                   | Description                                 |
| ------ | -------------------------- | ------------------------------------------- |
| POST   | `/api/auth/token/`         | (Duplicate login endpoint via project urls) |
| POST   | `/api/auth/token/refresh/` | (Duplicate refresh endpoint)                |

---

# 🏷️ Catalog Endpoints (categories, products, orders)

Base path: `/api/`

These come from DRF **ViewSets** registered via a router.

---

## 📂 Categories

| Method | Endpoint                | Description         |
| ------ | ----------------------- | ------------------- |
| GET    | `/api/categories/`      | List all categories |
| POST   | `/api/categories/`      | Create a category   |
| GET    | `/api/categories/<id>/` | Retrieve category   |
| PUT    | `/api/categories/<id>/` | Update category     |
| PATCH  | `/api/categories/<id>/` | Partial update      |
| DELETE | `/api/categories/<id>/` | Delete category     |

---

## 🛍 Products

| Method | Endpoint              | Description                  |
| ------ | --------------------- | ---------------------------- |
| GET    | `/api/products/`      | List products (with filters) |
| POST   | `/api/products/`      | Create product               |
| GET    | `/api/products/<id>/` | Retrieve product             |
| PUT    | `/api/products/<id>/` | Update product               |
| PATCH  | `/api/products/<id>/` | Partial update               |
| DELETE | `/api/products/<id>/` | Delete product               |

Filtering is available via:

```
/api/products/?category=<id>
/api/products/?min_price=...
/api/products/?max_price=...
/api/products/?search=keyword
```

*(From `catalog/filters.py`)*

---

## 📦 Orders

| Method | Endpoint            | Description                         |
| ------ | ------------------- | ----------------------------------- |
| GET    | `/api/orders/`      | List all orders (user/admin scoped) |
| POST   | `/api/orders/`      | Create an order                     |
| GET    | `/api/orders/<id>/` | Retrieve order                      |
| PUT    | `/api/orders/<id>/` | Update order                        |
| PATCH  | `/api/orders/<id>/` | Partial update                      |
| DELETE | `/api/orders/<id>/` | Delete order                        |

Orders support audit via `audit_models.py`.

---

# 📚 API Documentation

| URL             | Description                     |
| --------------- | ------------------------------- |
| `/swagger/`     | Interactive Swagger UI          |
| `/swagger.json` | OpenAPI schema                  |
| `/redoc/`       | Redoc interactive documentation |

Provided by drf-yasg.

---

# 🚢 Deployment Guide

## Procfile (already included)

```
web: gunicorn ecommerce_nexus.ecommerce_nexus.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

Supports deployment on:

* **PythonAnywhere**
* **Render**
* **Railway**
* **Heroku-style PaaS**
* **Cyclic.sh**
* **Dokku**

### Production steps

1. Set env vars
2. Turn off DEBUG
3. Add allowed hosts
4. Run migrations
5. Collect static

```bash
python manage.py collectstatic --no-input
```

6. Start service (Gunicorn handled by Procfile)

---

# 🧪 Running Tests

Tests exist under:

* `accounts/tests/`
* `catalog/tests/`

Run all:

```bash
pytest
```

or Django test runner:

```bash
python manage.py test
```

---

# 🤝 Contributing

Pull requests are welcome.

---

# 📄 License

MIT License.

---

