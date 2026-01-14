# Ceramics Portfolio – Full-Stack Django E-Commerce

**LIA Final Project – Freelancer Simulation**

This project is a full-stack upgrade of a ceramic artist’s portfolio site. It was built as part of the LIA Final Project, simulating a freelance client brief.

The objective was to evolve a static, one-page portfolio into a small but complete e-commerce experience. The application uses Django for the backend, Stripe Checkout for payments, and a responsive, accessible front end.

For recruiters, this project demonstrates end-to-end feature planning, Django architecture, third-party payment integration, and attention to accessibility and UX.

## Key Features

- Accessible, semantic one-page layout
- Responsive product grid for collections and series
- Django backend with `Product` and `Collection` models
- Stripe Checkout integration (test mode)
- Contact form backed by Django models and email
- Tailwind CSS for responsive styling
- Python environment and dependency management with `uv`

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** Django Templates, Tailwind CSS
- **Payments:** Stripe Checkout
- **Database:** SQLite (development)
- **Tooling:** Git, GitHub Projects, uv

## Local Setup

### Prerequisites

- Python 3.11+
- `uv` (Astral)
- Stripe account with test API keys

### Clone the repository

```bash
git clone https://github.com/<your-repo>/<project>.git
cd <project>
```

### Create and activate the environment

```bash
uv init
uv venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
```

Install dependencies:

```bash
uv sync
```

### Environment variables

Create a `.env` file in the project root (not committed):

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...  # Optional
```

### Database setup

```bash
uv run manage.py makemigrations
uv run manage.py migrate
uv run manage.py createsuperuser
```

### Run the server

```bash
uv run manage.py runserver
```

The application will be available at
`http://127.0.0.1:8000/`

### Run tests

```bash
uv run manage.py test
```

## Project Focus

This project emphasizes:

- Clean Django app separation
- Real payment flow using Stripe Checkout
- Accessibility-first HTML and responsive layouts
- Practical full-stack decision-making in a freelance context
