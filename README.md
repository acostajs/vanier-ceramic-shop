# Laura Melissa Ceramics – Full-Stack Django E-Commerce

**Full-Stack Django Project · Freelancer Simulation**

This project is a premium full-stack Django e-commerce application built as an upscale showroom and online store for an artisanal ceramics maker. The storefront blends earthy, minimalist design compliance with a robust backend feature set, third-party payment integrations, and automated quality assurance pipelines.

The application upgrades a ceramic artist’s static portfolio into a functional online shop with structured inventory management, Stripe Checkout integration, and cloud-hosted database and media storage services.

---

## Key Features

### 🎨 Design System & Branding
* **Warm Oatmeal Canvas:** Solid base backdrop using `{colors.canvas}` (`#fcf9f5`) to evoke a natural studio space.
* **5-Color Mineral Palette:** Curated accent tones inspired by natural slip clays: Terracotta (`#c87a53`), Sage (`#8fa48f`), Celadon (`#b2c4be`), Ochre (`#d4a359`), and Sand (`#e3ded5`).
* **Editorial Typography:** Exclusively uses the **Inter** font family, restricted to Light (300) and Regular (400) weights to convey minimalist luxury without bold structural distractions.
* **Balanced Component Shapes:** Restrained radii including `{rounded.xs}` (4px) for stock/limited tags, `{rounded.sm}` (6px) for checkout buttons and input fields, and `{rounded.md}` (12px) for product imagery cards.
* **Visual Rhythm:** Section vertical margins standardized to `{spacing.section}` (112px) for clean spacing, grounded by a dark charcoal-iron footer (`#1c1b1a`).
* **Homepage Hero Layout:** Asymmetrical 7-5 grid layout showcasing an editorial displaying headline and CTA on the left, paired with a full-height highlight image on the right.

### 🌐 Frontend UX & Internationalization (i18n)
* **Multi-Language Support (i18n):** Full support for **English**, **Français**, and **Español** translations with custom selector forms on both desktop and mobile headers.
* **Responsive Navigation:** A 72px-tall top bar featuring translucent glassmorphism (`bg-canvas-blur`), mobile drawer overlay menu, and a live cart counter badge (`Cart [X]`).
* **Animations & Performance:** Fade-in-up scroll reveals powered by `IntersectionObserver`, auto-dismissing toast notifications for cart and auth alerts, and optimized image loading (lazy loading and fetch priority adjustments).

### 🛒 E-Commerce & Stripe Integration
* **Stripe Checkout:** Integrates Stripe Checkout sessions for secure payment flows.
* **Automated Inventory Management:** Automatic inventory decrementing upon order transitions to `"paid"` status (e.g., triggered by Stripe Checkout Webhook verification).
* **Safe State Handling:** Unified cart and wishlist context processors showing counts to guests/users safely, with robust bounds checking (`get_object_or_404` views) to prevent unhandled 500 errors.
* **Purchase Audits:** Secure checkout views with decimal currency precision and cent-to-dollar arithmetic calculations.

---

## Tech Stack

* **Backend:** Django 5.2 (Python 3.13+)
* **Frontend:** Django Templates, Modern CSS (Vanilla, CSS Variables)
* **Payments:** Stripe Checkout API & Stripe Webhooks
* **Database:** PostgreSQL (production), SQLite (local development)
* **Tooling & Environment:** Astral `uv` (package and virtual environment management)
* **Code Quality:** Ruff (linter & formatter), Lefthook (Git hooks manager), GitHub Actions (CI pipeline)

---

## Directory Structure

The application is structured into modular Django apps for scalability:

* **`main`:** Core project configurations, settings modules divided by environment (`base.py`, `development.py`, `production.py`), URL routing, and shared helper mixins.
* **`shop`:** Product inventory and collection management, catalog views, and collection context processors.
* **`cart`:** Shopping cart database logic, Stripe Checkout session generators, payment success/cancel handling, and Stripe webhook endpoints.
* **`account`:** Custom user profiles (`Account`), shipping and billing addresses, and customer `Wishlist` models.
* **`contact`:** Customer contact form submissions saved to models, dispatching confirmation emails via console backends.

---

## Local Development

### Prerequisites
* Python 3.13+
* Astral `uv`
* Stripe Developer account with test keys

### 1. Repository Setup
Clone the repository and install dependencies using `uv`:
```bash
git clone https://github.com/acostajs/vanier-ceramic-shop.git project-name
cd project-name

# Create a virtual environment and sync packages
uv venv
source .venv/bin/activate
uv sync
```

### 2. Environment Configurations
Create a `.env` file in the root directory and configure the following:
```env
DJANGO_SECRET_KEY=your-django-secret-key
DJANGO_DEBUG=True

# Stripe credentials
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```
*(Make sure `.env` is listed in your `.gitignore` to prevent committing secrets).*

### 3. Database Initialization
Run Django migrations to construct the local SQLite database and create an admin user:
```bash
uv run manage.py migrate
uv run manage.py createsuperuser
```

### 4. Running the Development Server
You can run the Django development server:

```bash
uv run manage.py runserver
```

---

## Code Quality & CI/CD

To ensure codebase health, linting, formatting, and tests are automated.

### 1. Code Style and Linters
We use **Ruff** for all Python formatting and linting:
```bash
# Run formatter check
uv run ruff format --check

# Run linter
uv run ruff check
```

### 2. Running Tests
Run the Django test suite to verify backend and model logic:
```bash
uv run manage.py test
```

### 3. Git Hooks (Lefthook)
Git hooks are managed via **Lefthook** and automatically run:
* **Pre-commit:** Checks and formats staged python files using Ruff.
* **Pre-push:** Runs the Django test suite before pushing commits.

To install or reinstall Lefthook in your local git settings:
```bash
uv run lefthook install
```
