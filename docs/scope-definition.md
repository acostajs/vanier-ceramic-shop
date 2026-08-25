# Scope Definition

This document defines the boundaries of what is being tested in this project.

## In Scope

### Functional Areas

- User registration, login, logout. Module: Account.
- Product catalog browsing and product detail views. Module: Shop.
- Cart operations: add, update quantity, remove. Module: Cart.
- Checkout flow via Stripe Checkout, including webhook-driven order status updates.
- Contact form submission and validation. Module: Contact.

### Test Levels

- Unit testing (models, forms, business logic).
- Integration testing (multi-component flows, Stripe webhook handling).
- API testing (backend endpoints, authentication, request/response contracts).
- E2E testing (Full user journeys via Playwright, using POM).
- Smoke testing (critical-path page load verification).
- Performance/load testing (Locust - Response times and failure rate under simulated traffic).

### Environments

- Local development environment (SQLite).
- CI environment (Github Actions).

## Out of scope

| **Item**                              | **Reason**                                                                          |
| ------------------------------------- | ----------------------------------------------------------------------------------- |
| Payment processing / Live Stripe mode | Testing uses Stripe test mode only, no real financial transactions are tested.      |
| Email deliverability                  | Only that the app triggers/queues the email action is verified, not the third-party |
| Accessibility (WCAG)                  | Not currently part of the test strategy                                             |
| Localization i18n                     | Not currently part of the test strategy                                             |
| Admin                                 | The project uses Django Admin Framework, whish is tested upstream                   |
| Third-party service internals(Stripe) | Only the application's integration points with these services are tested            |
| Load testing beyond scale defined.    | Current benchmark simulates a modest concurrent user count                          |
| ------------------------------------- | ----------------------------------------------------------------------------------- |

## Assumptions

- Stripe test-mode API keys are available and correctly configured in all test environments
- Test data can be freely created/destroyed in local and CI databases without affecting any persisten/shared data
- The application is single-tenant, meaning is one store, not multi-vendor marketplace

## Constraints

- Testing is performed by a single contributor (portfolio project), so scope is deliberately limited to what can be reliably maintained
- No dedicated staging environment with production-like data volume currently exists
