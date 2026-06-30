# Ceramic shop Django E-Commerce | QA & Test Automation Showcase [![Coverage Status](https://coveralls.io/repos/github/acostajs/ceramic-shop-qa-showcase/badge.svg)](https://coveralls.io/github/acostajs/ceramic-shop-qa-showcase)

A Django e-commerce application built for an artisanal ceramics store. 

Although this project is a complete online store with customer accounts, shopping cart, and Stripe payments, its main purpose is to showcase my **Software QA and Test Automation** skills. The project demonstrates how I build, test, and maintain production-style Python applications using modern QA practices.

---

# Why This Project?

This project highlights my experience with:

* Building automated test suites with **pytest**
* Writing **unit, integration, API, smoke, performance, and end-to-end tests**
* Using the **Page Object Model (POM)** for maintainable UI automation
* Running automated tests in **GitHub Actions**
* Enforcing code quality with **Ruff** and **Git hooks**
* Working with modern Python development tools and best practices

For more information about the testing strategy, see:

**➡️ [tests/docs/README.md](tests/docs/README.md)**

---

# Tech Stack

### Backend

* Django 5.2
* Python 3.13+

### Frontend

* Django Templates
* HTML
* CSS

### Database

* PostgreSQL (Production)
* SQLite (Development)

### Payments

* Stripe Checkout
* Stripe Webhooks

### Development Tools

* pytest
* Ruff
* GitHub Actions
* Lefthook
* Astral uv

---

# Project Structure

The application is organized into feature folders and a dedicated testing folder.

```
tests/
    api/
    docs/
    e2e/
        pages/
    integration/
    performance/
    smoke/
    unit/
    conftest.py

main/
shop/
cart/
account/
contact/
```

The **tests/** folder contains different types of automated tests:

* **Unit tests** for models, forms, and views
* **Integration tests** for application workflows and Stripe webhooks
* **API tests** for backend endpoints
* **End-to-end browser tests** using the Page Object Model
* **Smoke tests** to quickly verify the application works
* **Performance tests** using Locust

---

# Getting Started

## Requirements

* Python 3.13+
* Astral uv
* Stripe test account

## Install

```bash
git clone github.com/acostajs/ceramic-shop-qa-showcase.git
cd project-name

uv venv
source .venv/bin/activate
uv sync
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Run the Application

```bash
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

---

# Code Quality

Run formatting and linting checks:

```bash
uv run ruff format --check
uv run ruff check
```

---

# Running Tests

Run the complete test suite:

```bash
uv run pytest
```

Generate a coverage report:

```bash
uv run task coverage
```

Generate an HTML coverage report:

```bash
uv run task coverage-report
```

---

# Performance Testing

Run performance tests with Locust:

```bash
uv run task perf
```

Run a headless performance test:

```bash
uv run task perf-report
```

The application averages **17 ms response times** with a **0.00% failure rate** during the included load test.

---

# Git Hooks

The project uses **Lefthook** to help keep the codebase clean.

Before every commit:

* Runs Ruff formatting and linting

Before every push:

* Runs the automated test suite

Install the Git hooks with:

```bash
uv run lefthook install
```
