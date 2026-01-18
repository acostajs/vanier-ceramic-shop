# Ceramics Portfolio – Full-Stack Django E-Commerce

**Full-Stack Django Project · Freelancer Simulation**

This project is a full-stack Django e-commerce application built as a simulated freelance engagement. It focuses on the core responsibilities expected in junior to mid-level Django roles: building clean backend logic, integrating third-party services, working with production databases, and deploying a real application.

The project upgrades a ceramic artist’s static portfolio into a functional online shop with product management, payments, and cloud-based storage.

A live version is deployed on Render using PostgreSQL for data persistence and AWS S3 for media storage.


## Key Features

* Django models for products, collections, and contact submissions
* Server-rendered templates using Django Templates
* Stripe Checkout integration (test mode)
* PostgreSQL database for production
* AWS S3 for product image storage
* Responsive layouts with Tailwind CSS
* Accessible, semantic HTML

## Tech Stack

* **Backend:** Django (Python)
* **Frontend:** Django Templates, Tailwind CSS
* **Payments:** Stripe Checkout
* **Database:** PostgreSQL (production), SQLite (local)
* **Media Storage:** AWS S3
* **Hosting:** Render
* **Tooling:** Git, GitHub, uv

## Architecture Overview

The application follows a modular Django structure with clear separation between models, views, templates, and settings.
PostgreSQL is used for structured data, while AWS S3 handles image uploads and storage.
Stripe manages payments externally, with checkout sessions created and tracked within the application.

This setup reflects a realistic small-scale production environment commonly encountered in junior and mid-level roles.

## Areas for Improvement

* Resolve authentication edge cases and improve user account flows
* Optimize layouts and performance for mobile-first usage
* Expand admin-side inventory and order management tools

## Local Development

This section is intended for developers reviewing or running the project locally.

### Prerequisites

* Python 3.11+
* `uv` (Astral)
* Stripe account with test API keys

### Setup

```bash
git clone https://github.com/acostajs/vanier-ceramic-shop project-name
cd project-name
uv init
uv venv
source .venv/bin/activate
uv sync
```

### Environment variables

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Database and server

```bash
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```