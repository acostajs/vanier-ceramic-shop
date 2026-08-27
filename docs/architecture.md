# System Architecture / Application Map

## High-Level Architecture

```
                    ┌─────────────────────────┐
                    │        Browser          │
                    │  (Django Templates UI)  │
                    └────────────┬────────────┘
                                 │ HTTP(S)
                                 ▼
                    ┌──────────────────────────┐
                    │      Django App          │
                    │  ┌───────┐ ┌───────┐     │
                    │  │account│ │ shop  │     │
                    │  ├───────┤ ├───────┤     │
                    │  │ cart  │ │contact│     │
                    │  └───────┘ └───────┘     │
                    │      (main project)      │
                    └──────┬──────────┬────────┘
                           │           │
                 ┌─────────┘           └──────────┐
                 ▼                                ▼
      ┌───────────────────┐                ┌──────────────────┐
      │   PostgreSQL /    │                │  Stripe Checkout │
      │   SQLite (dev)    │                │   + Webhooks     │
      └───────────────────┘                └──────────────────┘
```

## Components

| Component                        | Responsibility                                               |
| -------------------------------- | ------------------------------------------------------------ |
| `main`                           | Project settings, URL routing, root configuration            |
| `account`                        | User registration, authentication, profile management        |
| `shop`                           | Product catalog, product detail views                        |
| `cart`                           | Cart session/state management, cart-to-checkout handoff      |
| `contact`                        | Contact form handling                                        |
| `templates`, `static`            | Presentation layer (Django Templates, HTML, CSS)             |
| PostgreSQL (prod) / SQLite (dev) | Persistent data storage                                      |
| Stripe Checkout                  | Hosted payment page — card data never touches the app server |
| Stripe Webhooks                  | Asynchronous payment status notifications back to the app    |

## Key Integration Points

1. **App ↔ Stripe Checkout** — session creation, redirect handoff, success/cancel URL handling
2. **Stripe ↔ App Webhook endpoint** — signature verification, event parsing, order status update, idempotency on retried events
3. **Cart session ↔ Order creation** — ensuring cart contents accurately convert into an order at checkout time
4. **Auth ↔ Session management** — login state persisted correctly across requests

## Data Flow: Checkout (example — critical path)

1. Customer adds items to cart → cart state stored
2. Customer proceeds to checkout → app creates a Stripe Checkout Session server-side
3. Customer is redirected to Stripe-hosted payment page
4. On completion, Stripe redirects customer to a success URL **and** independently sends a webhook event to the app
5. App's webhook handler verifies the event signature and updates the order status in the database
6. Order confirmation is reflected to the user

## Deployment / Environments

| Environment         | Database   | Notes                                    |
| ------------------- | ---------- | ---------------------------------------- | --- |
| Local dev           | SQLite     | Used for development and local test runs |     |
| CI (GitHub Actions) |            | Runs full automated suite on push/PR     |
| Production          | PostgreSQL |                                          |
