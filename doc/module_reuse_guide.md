# Django E-Commerce Module Reuse Guide

> **Who is this for?**  
> You know basic Python. You are a UI/UX designer who wants to build real web apps by reusing these modules and just changing the design. You do not need to understand Django deeply — just follow each step exactly.

---

## What is This Project?

This is a full Django e-commerce web app. It is split into **independent modules (apps)**. You pick only the ones you need and wire them together. Think of them like LEGO bricks.

| Module | What it does | Needs |
|--------|-------------|-------|
| `core` | Home, About, Contact pages | Nothing |
| `accounts` | Register, Login, Logout | Nothing |
| `products` | Product listing, detail pages | Nothing |
| `cart` | Shopping cart (no database needed) | `products` |
| `orders` | Checkout, payment proof, order history | `cart`, `products` |
| `reviews` | Star ratings and reviews on products | `products` |

---

## Part 1 — Setting Up a Brand New Project (Do This First, Always)

### Step 1 — Install Python

1. Go to https://python.org/downloads and download **Python 3.11 or higher**
2. Install it. On the installer, tick **"Add Python to PATH"**
3. Open a terminal (search "Terminal" or "Command Prompt" on your PC)
4. Type this and press Enter to confirm Python works:
   ```
   python --version
   ```
   You should see something like `Python 3.11.x`

---

### Step 2 — Create Your Project Folder

Pick a folder on your computer where you want the project. In the terminal:

```bash
# Create the folder and go into it
mkdir my_new_project
cd my_new_project
```

---

### Step 3 — Create a Virtual Environment

A virtual environment is an isolated box where Python packages are installed — it keeps your projects from interfering with each other.

```bash
python -m venv venv
```

Now **activate** it:

- **On Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```
- **On Windows:**
  ```bash
  venv\Scripts\activate
  ```

You will see `(venv)` at the start of your terminal line. This must be active whenever you work on the project.

---

### Step 4 — Install Required Packages

Create a file called `requirements.txt` in your project folder and paste this into it:

```
django==6.0.3
python-dotenv
django-jazzmin
cloudinary
django-cloudinary-storage
whitenoise
dj-database-url
psycopg2-binary
requests
Pillow
django-tailwind
```

Then install everything:

```bash
pip install -r requirements.txt
```

---

### Step 5 — Create the Django Project

```bash
django-admin startproject tes .
```

> The dot `.` at the end is important — it creates the project in the current folder instead of making a nested folder.

Your folder should now look like:
```
my_new_project/
├── venv/
├── requirements.txt
├── manage.py
└── tes/
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    └── asgi.py
```

---

### Step 6 — Create the `.env` File

Create a file called `.env` in your project folder (next to `manage.py`). This stores all secrets:

```env
DJANGO_SECRET_KEY=put-any-long-random-string-here-change-this
DEBUG=True
ALLOWED_HOSTS=*

# Leave these blank for now — fill them in later
DATABASE_URL=
CLOUDINARY_URL=
UPI_ID=yourname@upi
PAYEE_NAME=Your Business Name
GOOGLE_SCRIPT_URL=
```

> **Never share this file or upload it to GitHub.** Add `.env` to your `.gitignore`.

---

### Step 7 — Configure `settings.py`

Open `tes/settings.py` and **replace the entire file** with this:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

# --- INSTALLED APPS ---
# Add or remove apps here depending on which modules you use
INSTALLED_APPS = [
    "jazzmin",                        # Admin UI — must be FIRST
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary_storage",             # Must be before cloudinary
    "cloudinary",
    # --- Your apps go here ---
    "core",
    "accounts",
    "products",
    "cart",
    "orders",
    "reviews",
    "tailwind",
    "theme",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tes.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
            "cart.cart.cart_context",          # Injects cart into every template
            "tes.context_processors.theme_colors",
            "core.context_processors.contact_info",
        ],
    },
}]

WSGI_APPLICATION = "tes.wsgi.application"

# --- DATABASE ---
import dj_database_url
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL, conn_max_age=600, conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- SESSIONS (cookie-based, no DB needed) ---
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"

# --- STATIC FILES ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# --- MEDIA FILES (Cloudinary) ---
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedStaticFilesStorage"
            if not DEBUG
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

# --- CUSTOM SETTINGS ---
CART_SESSION_ID = "cart"
UPI_ID = os.environ.get("UPI_ID", "yourname@upi")
PAYEE_NAME = os.environ.get("PAYEE_NAME", "Your Store")
GOOGLE_SCRIPT_URL = os.environ.get("GOOGLE_SCRIPT_URL", "")

TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = ["127.0.0.1"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"

# --- SITE CONTACT INFO (used in footer/contact page) ---
SITE_CONTACT = {
    "phone": os.environ.get("CONTACT_PHONE", "+91 00000 00000"),
    "email": os.environ.get("CONTACT_EMAIL", "you@email.com"),
    "address": os.environ.get("CONTACT_ADDRESS", "Your City, India"),
    "working_hours": os.environ.get("CONTACT_HOURS", "Mon–Sat: 9 AM – 6 PM"),
    "whatsapp_url": os.environ.get("CONTACT_WHATSAPP_URL", "https://wa.me/"),
    "instagram_url": os.environ.get("CONTACT_INSTAGRAM_URL", "https://instagram.com/"),
}

# --- JAZZMIN ADMIN UI ---
JAZZMIN_SETTINGS = {
    "site_title": "My Store Admin",
    "site_header": "My Store",
    "site_brand": "My Store",
    "welcome_sign": "Welcome to My Store Management",
    "copyright": "My Store Ltd",
    "search_model": ["auth.User", "products.Product"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["auth", "products", "orders", "cart"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "products.Product": "fas fa-box",
        "products.Category": "fas fa-tags",
        "orders.Order": "fas fa-shopping-cart",
    },
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "pulse",          # Change this to any Bootswatch theme name
    "brand_colour": "navbar-primary",
    "sidebar": "sidebar-dark-primary",
    "navbar": "navbar-dark",
}
```

---

### Step 8 — Set Up Tailwind CSS

```bash
python manage.py tailwind init
```

When it asks for the app name, type: `theme`

Then install Tailwind's Node dependencies:
```bash
python manage.py tailwind install
```

> You need Node.js installed for this step. Download from https://nodejs.org (LTS version).

---

### Step 9 — Copy the App Folders

From this project, copy the app folders you need into your new project:

```
copy → core/
copy → accounts/
copy → products/
copy → cart/
copy → orders/
copy → reviews/
```

Also copy:
```
copy → templates/        (the root-level templates folder with base.html)
copy → static/           (the root-level static folder with CSS/JS)
copy → tes/context_processors.py
```

---

### Step 10 — Set Up Root URLs

Open `tes/urls.py` and replace its content:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("products/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("reviews/", include("reviews.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

> **Only include the URL lines for modules you actually copied.**

---

### Step 11 — Run Migrations and Create Admin

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

Follow the prompts to set your admin username and password.

---

### Step 12 — Run the Development Server

```bash
python manage.py runserver
```

Open your browser and go to: **http://127.0.0.1:8000**

Admin panel: **http://127.0.0.1:8000/admin**

---

## Part 2 — Module Reference (Pick Only What You Need)

---

### Module A — `core` (Home / About / Contact)

**What it gives you:** Home page, About page, Contact page, static info pages.

**Depends on:** Nothing.

**To enable it:** Just copy the `core/` folder. It's already in the URLs above.

**Customise the contact info:** Edit `.env`:
```env
CONTACT_PHONE=+91 99999 99999
CONTACT_EMAIL=you@gmail.com
CONTACT_ADDRESS=Chennai, Tamil Nadu
CONTACT_HOURS=Mon-Sat: 10 AM - 7 PM
CONTACT_WHATSAPP_URL=https://wa.me/919999999999
```

**To change the homepage content:** Edit `core/templates/core/home.html`.

---

### Module B — `accounts` (Register / Login / Logout)

**What it gives you:** User registration with email, login, logout, profile page.

**Depends on:** Nothing (uses Django's built-in User model).

**Key behaviours:**
- After registration → user is logged in automatically and redirected home
- Login uses username + password
- Logout requires a POST form (security — prevents accidental logout)

**Logout button in any template:**
```html
<form method="post" action="{% url 'accounts:logout' %}">
  {% csrf_token %}
  <button type="submit">Logout</button>
</form>
```

**Check if a user is logged in, in any template:**
```html
{% if user.is_authenticated %}
  Hello, {{ user.username }}!
{% else %}
  <a href="{% url 'accounts:login' %}">Login</a>
{% endif %}
```

**To skip accounts entirely:** Remove `"accounts"` from `INSTALLED_APPS` and remove its URL line. Everything else still works — orders will accept guest checkouts.

---

### Module C — `products` (Product Catalogue)

**What it gives you:** Product list page with filtering/sorting/search, product detail page, category pages.

**Depends on:** Nothing.

**How to add products:** Go to admin → Products → Add Product. Fill in:
- Name (required)
- Price (required)
- Category (required — create one first)
- Stock Quantity — how many are available
- Availability Status — set to "In Stock"
- Image — upload the product photo
- Short Description — shown on list cards
- Specifications — stored as `{"RAM": "8GB", "Storage": "256GB"}`

**The product detail page shows:**
- Product image gallery
- Price (with sale badge if `original_price > price`)
- Stock count (e.g. "✔ 12 in stock" or "⚠ Only 2 left!")
- Specifications table
- Related products
- Reviews (if reviews module is enabled)

**URL to product detail in templates:**
```html
<a href="{{ product.get_absolute_url }}">View Product</a>
```

**URL to add to cart:**
```html
<form method="post" action="{{ product.get_add_to_cart_url }}">
  {% csrf_token %}
  <input type="hidden" name="quantity" value="1">
  <button type="submit">Add to Cart</button>
</form>
```

---

### Module D — `cart` (Shopping Cart)

**What it gives you:** Session-based cart — no database table needed. Cart data is stored in the browser session (cookie).

**Depends on:** `products`

**Special setup required in `settings.py`** — already included in the settings above:
```python
CART_SESSION_ID = "cart"
```

And in `TEMPLATES → context_processors`:
```python
"cart.cart.cart_context",
```

This injects the cart object into **every** template automatically.

**Use cart data in any template:**
```html
{{ cart|length }}           {# Number of items in cart #}
{{ cart.get_total_price }}  {# Total price #}
```

**Cart page URL:**
```html
<a href="{% url 'cart:cart_detail' %}">View Cart</a>
```

**Stock validation (built-in):**  
The cart page automatically compares each item's quantity against live stock. If a product has only 2 in stock but the customer tries to order 3, a red warning appears and the **Checkout button is disabled** until the quantity is corrected.

**How quantities work:**
- Each product has a `−` and `+` button in the cart
- Pressing `−` when quantity is 1 removes the item
- No manual number input — just tap the buttons

---

### Module E — `orders` (Checkout + Payment)

**What it gives you:** Checkout form (name, address, phone, email), UPI QR code payment, payment screenshot upload, order confirmation page, order history.

**Depends on:** `cart`, `products`

**Required settings in `.env`:**
```env
UPI_ID=yourname@upi
PAYEE_NAME=Your Store Name
GOOGLE_SCRIPT_URL=          # Leave blank to disable Google Sheets sync
```

**Checkout flow:**
1. Customer fills in shipping details
2. Customer scans the UPI QR code and pays
3. Customer uploads a screenshot of the payment
4. Customer enters the UTR number (transaction ID from their UPI app)
5. On submit → order is created, stock is automatically reduced, cart is cleared
6. Customer sees order confirmation page

**Stock safety (built-in):**  
Before placing the order, the system re-checks live stock. If stock ran out between the customer adding to cart and submitting the order, the checkout is blocked with a clear error message.

**Google Sheets sync (optional):**  
If you add a `GOOGLE_SCRIPT_URL`, every successful order is automatically sent to a Google Sheet in the background. To set this up:
1. Create a Google Apps Script project
2. Deploy it as a Web App
3. Copy the web app URL into your `.env`

If you don't need Google Sheets, leave `GOOGLE_SCRIPT_URL=` blank — the system works perfectly without it.

**Guest checkout:**  
Customers do not need an account to place an order. The confirmation page is accessible via a session token for guest users.

**Order management (admin):**  
Go to admin → Orders. You can:
- See all orders with payment screenshots
- Change order status (Pending → Confirmed → Shipped → Delivered)
- Use bulk actions to update multiple orders at once

---

### Module F — `reviews` (Product Reviews)

**What it gives you:** Star ratings (1–5) on products, written reviews with titles and comments, moderation (only approved reviews show publicly), automatic rating average updates.

**Depends on:** `products`

**How it works:**
- Reviews are saved to the database
- They are hidden until an admin approves them (`is_approved = True`)
- Once approved, the product's `average_rating` and `review_count` fields update automatically via Django signals
- The product detail page shows the star breakdown chart

**To approve reviews:** Admin → Reviews → tick the checkbox → Actions → "Approve selected reviews"

**To remove the reviews module entirely:**
1. Remove `"reviews"` from `INSTALLED_APPS`
2. Remove `reviews/` URL from `tes/urls.py`
3. The products app still works — ratings just won't update

---

## Part 3 — Changing the Design (UI/UX)

As a designer, this is your primary area. Here is where to find each piece:

### Design Tokens (Colors, Fonts, Spacing)

**Primary colors and gradients** are defined in:
```
static/css/    or    theme/static/
```

The project uses **Tailwind CSS**. To change the color system, edit `tailwind.config.js`.

**The admin UI theme** is controlled by one line in `settings.py`:
```python
JAZZMIN_UI_TWEAKS = {
    "theme": "pulse",   # ← Change this
}
```

Available themes (all free, just change the name):
`cerulean`, `cosmo`, `cyborg`, `darkly`, `flatly`, `journal`, `litera`, `lumen`, `lux`, `materia`, `minty`, `morph`, `pulse`, `quartz`, `sandstone`, `simplex`, `sketchy`, `slate`, `solar`, `spacelab`, `superhero`, `united`, `vapor`, `yeti`, `zephyr`

---

### Template Locations

| What you want to change | File to edit |
|------------------------|-------------|
| Global nav, footer, base layout | `templates/base.html` |
| Home page | `core/templates/core/home.html` |
| About page | `core/templates/core/about.html` |
| Contact page | `core/templates/core/contact.html` |
| Product list grid | `products/templates/products/product_list.html` |
| Product detail page | `products/templates/products/product_detail.html` |
| Shopping cart page | `cart/templates/cart/cart_detail.html` |
| Checkout form page | `orders/templates/orders/checkout.html` |
| Order confirmation | `orders/templates/orders/order_confirmation.html` |
| Login page | `accounts/templates/accounts/login.html` |
| Register page | `accounts/templates/accounts/register.html` |

---

### How to Change Only the UI Without Breaking Logic

The golden rule: **never edit `views.py`, `models.py`, or `urls.py` for design changes.** Only edit `.html` files.

Template variables are pre-filled by the views — just use them in your new design:

```html
<!-- These always work on the product detail page -->
{{ product.name }}
{{ product.price }}
{{ product.image.url }}
{{ product.stock_quantity }}
{{ product.availability_status }}
{{ product.short_description }}
```

```html
<!-- These always work on the cart page -->
{% for item in cart_items %}
  {{ item.product.name }}
  {{ item.quantity }}
  {{ item.price }}
  {{ item.total_price }}
  {{ item.available_stock }}     {# How many are actually in stock #}
  {{ item.over_limit }}          {# True if cart qty > stock #}
{% endfor %}
```

---

## Part 4 — Cloudinary (Image Uploads)

Cloudinary stores all uploaded images (product photos, payment screenshots) in the cloud instead of your server. This is required for Vercel deployment because Vercel's file system is read-only.

### How to Set Up Cloudinary

1. Go to https://cloudinary.com and create a free account
2. After logging in, go to your Dashboard
3. Copy the **API Environment variable** — it looks like:
   ```
   cloudinary://your_api_key:your_api_secret@your_cloud_name
   ```
4. Paste it into your `.env`:
   ```env
   CLOUDINARY_URL=cloudinary://your_api_key:your_api_secret@your_cloud_name
   ```

That's it. All image uploads now go to Cloudinary automatically.

---

## Part 5 — Deploying to Vercel (Production)

### Step 1 — Create `vercel.json`

Create a file called `vercel.json` in your project root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "tes/wsgi.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "15mb", "runtime": "python3.11" }
    },
    {
      "src": "build_files.sh",
      "use": "@vercel/static-build",
      "config": { "distDir": "staticfiles" }
    }
  ],
  "routes": [
    { "src": "/static/(.*)", "dest": "/static/$1" },
    { "src": "/(.*)", "dest": "tes/wsgi.py" }
  ]
}
```

### Step 2 — Create `build_files.sh`

```bash
#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
```

### Step 3 — Set Environment Variables on Vercel

Go to your Vercel project → Settings → Environment Variables. Add:

| Name | Value |
|------|-------|
| `DJANGO_SECRET_KEY` | A long random string (generate at https://djecrety.ir) |
| `DEBUG` | `False` |
| `DATABASE_URL` | Your PostgreSQL connection URL (get from Neon or Supabase — both free) |
| `CLOUDINARY_URL` | Your Cloudinary URL from Part 4 |
| `UPI_ID` | Your UPI address |
| `PAYEE_NAME` | Your business name |
| `ALLOWED_HOSTS` | `yourapp.vercel.app` |

### Step 4 — Get a Free PostgreSQL Database

1. Go to https://neon.tech (free tier is enough)
2. Create a project and database
3. Copy the **connection string** — it starts with `postgresql://`
4. Paste it as `DATABASE_URL` in Vercel environment variables

### Step 5 — Deploy

1. Push your code to GitHub
2. Go to https://vercel.com and import the GitHub repository
3. Click Deploy

Vercel will run `build_files.sh` automatically, collect static files, run migrations, and start the server.

---

## Part 6 — Common Recipes

### "I only want a simple website — just Home, About, Contact"

Use only `core`. In `settings.py`:
```python
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "tailwind",
    "theme",
]
```

In `tes/urls.py`:
```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]
```

Remove `"cart.cart.cart_context"` from context processors.

---

### "I want a product catalogue but no cart or orders"

Use `core` + `products`. Remove `cart`, `orders`, `reviews` from `INSTALLED_APPS` and remove their URL lines. Also remove `"cart.cart.cart_context"` from context processors.

---

### "I want everything — the full shop"

Use all six modules exactly as shown in the settings template in Part 1.

---

### "I want to add a new page"

1. Open `core/views.py` and add a new function:
   ```python
   def my_page(request):
       return render(request, "core/my_page.html", {})
   ```

2. Open `core/urls.py` and add a URL:
   ```python
   path("my-page/", views.my_page, name="my_page"),
   ```

3. Create the template `core/templates/core/my_page.html`:
   ```html
   {% extends 'base.html' %}
   {% block content %}
   <h1>My New Page</h1>
   {% endblock %}
   ```

---

## Part 7 — Recent Changes Changelog

This section tracks significant changes made during active development so you know what the current codebase does vs older documentation.

### Stock Management (April 2026)

**Product detail page** now shows live stock count below the availability badge:
- Green: "✔ 12 in stock"
- Amber warning: "⚠ Only 2 left in stock – order soon!" (when ≤ 5)
- Hidden when out of stock

**Cart page** now validates stock before checkout:
- Each cart item shows a red error if quantity exceeds available stock
- The Checkout button becomes disabled until all quantities are corrected
- The `cart_detail` view injects `cart_items` (a list with `over_limit` and `available_stock` per item) instead of the raw `cart` object

**Checkout view** has a stock pre-check:
- Before writing to the database, live stock is rechecked
- If any product ran out between cart and checkout, the order is deleted and the user is redirected with a clear error

### Cart UX (April 2026)

- Quantity controls replaced: no more text input + refresh icon
- New `−` / `+` stepper buttons — tapping `−` at qty 1 removes the item
- Works on both mobile (card view) and desktop (table view)

### Image Gallery (April 2026)

- A new `ProductImage` model with Django Admin inline support replaced the old JSON `image_gallery` field
- Product gallery images can now be uploaded directly from admin

### Modular Architecture (April 2026)

- `reviews` app was decoupled from `products` using Django Signals
- `products` no longer directly calls review logic — `reviews/signals.py` listens and triggers `product.update_rating()` automatically

---

## Quick Reference — Terminal Commands

```bash
# Activate the virtual environment (do this every time you open the terminal)
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows

# Run the local server
python manage.py runserver

# After editing models.py — always run these two commands
python manage.py makemigrations
python manage.py migrate

# Create an admin user
python manage.py createsuperuser

# Collect static files (needed before deploying)
python manage.py collectstatic

# Check for errors
python manage.py check

# Run tests
python manage.py test
```

---

*Last updated: April 2026*
