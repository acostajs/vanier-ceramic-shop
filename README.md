# 582-41E-VA-LIA-Final_Project
Block 4 - Web Project Planning and Management - Final Project

A small full-stack upgrade of a ceramics portfolio site for the LIA Final Project – Freelancer Simulation.  
The goal is to turn a static one-page layout into a functional mini e‑commerce experience with a Django backend, Stripe payments, and an accessible, responsive front end.

## Features

- Semantic, accessible one-page layout for an independent ceramic artist.
- Responsive product grid for the collections and other series.
- Django backend with `Product` and `Collection` models.
- Stripe Checkout integration for secure payments.
- Contact form backed by Django models and email.
- Managed with [`uv`](https://docs.astral.sh/uv/) from Astral for Python, virtualenv, and dependency management.

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML5, CSS, a bit of TS
- **Payments:** Stripe Checkout
- **Tooling:** Git, GitHub Projects, uv
- **Database:** SQLite in development

## Getting Started

### Prerequisites

- `uv` installed (see Astral’s docs).
- Stripe account with test API keys.
- Python supported by uv (e.g. 3.11+).

### 1. Clone the repository

- git clone https://github.com//.git project
- cd project

### 2. Create environment and install dependencies

- uv init - Initialize project
- uv venv - creates virtual environment
- source .venv/bin/activate  # or .venv\Scripts\activate on Windows - Activates Virtual Environment
- uv add package-name - to add dependencies
- uv sync - to install requirements from pyproject.toml

### 3. Environment variables

- Create a `.env` file in the project root (not committed to Git) with at least:
- DJANGO_SECRET_KEY=your-secret-key 
- DJANGO_DEBUG=True 
- STRIPE_PUBLIC_KEY=pk_test_… 
- STRIPE_SECRET_KEY=sk_test_… 
- STRIPE_WEBHOOK_SECRET=whsec_…  # optional if using webhooks

### 4. Install Django (and other dependencies)
- uv add install django stripe 
- uv add install stripe
- uv add install python-dotenv

### 5. Create the Django project

From the repo root:
- uv run django-admin startproject project
- This creates `manage.py` and a `config/` directory with `settings.py`, `urls.py`, etc.

### 6. Create core apps
- uv run manage.py startapp inventory
- uv run manage.py startapp contact


### 7. Database setup

Once the models are created:
- uv run manage.py makemigrations
- uv run manage.py migrate
- uv run manage.py createsuperuser

### 8. Run server
- uv run manage.py runserver

### 9. Testing
- uv run manage.py test
