# QA Showcase - Vanier Ceramic Shop

**Full-Stack Django Production Application with Multi-Layered QA & Test Automation Framework**

This repository features a professional full-stack Django e-commerce showroom and online store built for an artisanal ceramics maker. While fully functional for customer checkout, the architectural focus of this codebase is to demonstrate production-grade **Software Quality Assurance (QA) and Test Automation practices** within a modern Python development ecosystem.

---

## QA & Test Automation Showcase

This project enforces a strict test-first mentality. For comprehensive test strategies, test plan briefs, and framework configuration details, see the dedicated documentation:

--> **[Read the Test Automation & QA Documentation (tests/docs/README.md)](tests/docs/README.md)**

### Core Testing Pillars:
* **Multi-Layered Automation:** Full coverage spanning unit boundaries, system integration points, backend API endpoints, and end-to-end user browser interactions.
* **Page Object Model (POM):** Clean, maintainable UI testing separation of concerns where individual view layouts and element selectors are fully encapsulated.
* **CI/CD Guardrails:** Automated GitHub Actions workflows that run the test matrices and static analysis checking on every incoming Pull Request.
* **Local Git Hooks:** Automated local safety checks that ensure no linting regressions or broken tests ever leave the developer's computer.

---

## Tech Stack

* **Backend Framework:** Django 5.2 (Python 3.13+)
* **Frontend Architecture:** Django Templates & Native CSS (Vanilla/CSS Variables)
* **Payment Architecture:** Stripe Checkout API & Stripe Webhook Infrastructure
* **Database Systems:** PostgreSQL (Production) / SQLite (Local Development)
* **Dependency & Environment Tooling:** Astral `uv`
* **Static Analysis & Formatting:** Ruff
* **Git Hook Management:** Lefthook

---

## Directory Structure

The application architecture decouples business logic from a comprehensive testing lifecycle framework:

* **`tests/`:** Central automation workspace containing distinct validation boundaries:
  * **`api/`:** Payload structure and server response verification (`test_endpoints.py`).
  * **`docs/`:** Test strategies and automation specifications (`README.md`).
  * **`e2e/`:** Browser automation regression flows (`test_flows.py`) leveraging the Page Object Model (POM) pattern.
    * **`pages/`:** Structural selectors and interface interactions mapped per view (e.g., `home.py`, `cart.py`, `checkout.py`, `account.py`).
  * **`integration/`:** State transitions and asynchronous Stripe webhook event simulation (`test_integration.py`).
  * **`smoke/`:** High-priority health checks verifying global platform availability (`test_smoke.py`).
  * **`unit/`:** Isolated boundary testing for Django models, views, forms, and contexts (`test_account.py`, `test_cart.py`, `test_contact.py`, `test_shop.py`).
  * **`conftest.py`:** Shared test automation plugins, configuration states, and mock fixtures.
* **`main/`:** Core runtime orchestration and environmental settings profiles (`base.py`, `development.py`, `production.py`).
* **`shop/`:** Catalog display, collection listings, and product inventory tracking tracking.
* **`cart/`:** Checkout flows, session factories, and asynchronous Stripe webhook receipt handling.
* **`account/`:** User authentication profiles, localized addresses, and client wishlists.
* **`contact/`:** Customer contact interactions and transactional message dispatch.

---

## Local Setup & Environment Lifecycle

### Prerequisites
* Python 3.13+
* Astral `uv`
* Stripe Developer Account (Test Keys)

### 1. Installation
Clone the repository and compile the virtual environment profile using `uv`:
```bash
git clone [https://github.com/acostajs/vanier-ceramic-shop.git](https://github.com/acostajs/vanier-ceramic-shop.git) project-name
cd project-name

# Establish local virtual environment and synchronize dependencies
uv venv
source .venv/bin/activate
uv sync

```

### 2. Environment Configurations

Instantiate a local `.env` block in the project root:

```env
DJANGO_SECRET_KEY=your-django-secret-key
DJANGO_DEBUG=True

# Stripe keys
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

```

### 3. Database & App Initialization

Apply database schemas and initialize the web instance:

```bash
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver

```

---

## Verification & Guardrails

### 1. Static Code Analysis

Run code auditing checks and deterministic code styling formats via **Ruff**:

```bash
# Run styling conformance checks
uv run ruff format --check

# Execute static analysis linter
uv run ruff check

```

### 2. Executing Automated Test Runners

To trigger the automated backend testing runtime:

```bash
uv run manage.py test

```

### 3. Git Hooks Automation (Lefthook)

Automated pre-configured project guardrails are applied locally via **Lefthook**:

* **Pre-commit:** Runs `ruff` checks to guarantee code compliance before tracking commits.
* **Pre-push:** Runs the complete Django regression suite to verify zero breakages reach remote repositories.

To activate or reset local Git configurations:

```bash
uv run lefthook install

```
